from __future__ import annotations

from .bank_definitions import get_banked_parameter
from .command_encoder import CommandEncoder
from .errors import ConfigurationError, CriticalConfigurationError, NumberedDeviceMissingError
from .parse_target_path import parse_target_path
from .util import is_chain_map_positional


class BindingsMixin(object):

    def __init__(self, *args, **kwargs):
        ...

    def setup_bindings(self, bindings_raw, all_zcx_modes, allow_command_encoder=False):
        if isinstance(bindings_raw, dict):
            if list(bindings_raw.keys())[0] == "command":
                bindings_raw = {"default": bindings_raw}
        elif isinstance(bindings_raw, str):
            bindings_raw = {"default": bindings_raw}
        else:
            raise CriticalConfigurationError(
                f"Invalid binding config for {self._name}"
                f"\n`binding` key must be a dict or a string. was:"
                f"\n{bindings_raw}"
                f"\n\nconfig:"
                f"\n{self._raw_config}"
            )

        binding_dict = {}
        concerned_modes = []

        for binding_mode, binding_def in bindings_raw.items():
            command_encoder_def = None

            if isinstance(binding_def, str):
                binding_params = {}
            elif isinstance(binding_def, dict):
                binding_params = copy.deepcopy(binding_def)
                if allow_command_encoder and "command" in binding_def:
                    command_encoder_def = binding_def["command"]
                elif "target" in binding_params:
                    binding_def = binding_params["target"]
                    del binding_params["target"]
            else:
                raise CriticalConfigurationError(
                    f"Invalid binding config for {self._name}"
                    f"\nBinding definitions must be a dict or a string"
                    f"\n{self._raw_config}"
                )

            these_modes = binding_mode.split("__")
            for mode in these_modes:
                if mode not in ["default", ""]:
                    if mode not in all_zcx_modes:
                        raise CriticalConfigurationError(
                            f"Definition for `{self._name}` references mode `{mode}`"
                            f" that does not appear in `modes.yaml`"
                        )
                if mode not in concerned_modes:
                    concerned_modes.append(mode)

            these_modes.sort()
            sorted_mode_string = "__".join(these_modes)

            if command_encoder_def:
                try:
                    binding_dict[sorted_mode_string] = CommandEncoder(
                        self, command_encoder_def, sorted_mode_string
                    )
                except Exception as e:
                    self.critical(
                        f"Error creating command encoder for `{self._name}`"
                        f" mode `{sorted_mode_string}`:"
                    )
                    self.critical(f"{e.__class__.__name__}: {e}")
                    raise
            else:
                binding_def = binding_def.rstrip('\n')
                parsed_target_string, status = self.action_resolver.compile(
                    binding_def,
                    self._vars,
                    self._context,
                )
                if status != 0:
                    raise ConfigurationError(
                        f"Error creating `{self._name}`. Binding `{sorted_mode_string}`"
                        f" contains unparseable template string:"
                        f"\n{binding_def}"
                    )
                target_map = parse_target_path(parsed_target_string)
                if target_map["error"] is not None:
                    raise ConfigurationError(target_map["error"])

                binding_dict[sorted_mode_string] = target_map

        concerned_modes.sort()
        return binding_dict, concerned_modes

    def traverse_chain_map(self, track, chain_map):
        def parse_templated_node(_node):
            if not isinstance(_node, str) or '${' not in _node:
                try:
                    return int(_node)
                except (ValueError, TypeError):
                    if isinstance(_node, str):
                        try:
                            if _node.startswith('"') and _node.endswith('"'):
                                return _node.strip('"')
                        except (ValueError, AttributeError):
                            pass
                    return _node

            # Parse templated string using action_resolver
            parsed, status = self.action_resolver.compile(_node, self._vars, self._context)
            if status != 0:
                raise ConfigurationError(f"Unparseable node: {_node}")

            # Strip quotes if present
            if isinstance(parsed, str) and parsed.startswith('"') and parsed.endswith('"'):
                return parsed.strip('"')
            return parsed

        track_devices = list(track.devices)
        current_search_obj = track_devices

        for i, node in enumerate(chain_map):
            is_device = i % 2 == 0
            node = parse_templated_node(node)

            if i == 0:
                # First node is always a device
                if isinstance(node, int):
                    current_search_obj = track_devices[node - 1]
                else:
                    found = False
                    for device in track_devices:
                        if device.name == node:
                            current_search_obj = device
                            found = True
                            break
                    if not found:
                        raise ConfigurationError(f"No device called: {node}")
            elif is_device:
                # Looking for a device in the current chain
                if isinstance(node, int):
                    current_search_obj = list(current_search_obj.devices)[node - 1]
                else:
                    found = False
                    for device in current_search_obj.devices:
                        if device.name == node:
                            current_search_obj = device
                            found = True
                            break
                    if not found:
                        raise ConfigurationError(f'No device in {current_search_obj.name} called {node}')
            else:
                # Looking for a chain in the current device
                if isinstance(node, int) and hasattr(current_search_obj, "chains"):
                    current_search_obj = list(current_search_obj.chains)[node - 1]
                else:
                    found = False
                    if hasattr(current_search_obj, "chains"):
                        for chain in current_search_obj.chains:
                            if chain.name == node:
                                current_search_obj = chain
                                found = True
                                break
                    if not found:
                        raise ConfigurationError(f'No chain in {current_search_obj.name} called {node}')

        return current_search_obj

    def get_track(self, track_def):
        if track_def.lower() == "sel":
            return self.root_cs.song.view.selected_track
        elif track_def.lower() == "mst":
            return self.root_cs.song.master_track

        try:
            track = self.root_cs.component_map["CxpBridge"].get_track_by_name(track_def)
            return track
        except RuntimeError:
            self.debug(f"Failed to get track called `{track_def}` from CXP")

        for track in self.root_cs.song.tracks:
            if track.name == track_def:
                return track

        try:
            track_num = int(track_def) - 1
            tracklist = list(self.root_cs.song.tracks)
            return tracklist[track_num]
        except (ValueError, IndexError):
            return None

    def override_binding_definition(self, binding_def, mode='default', unparsed_mode_string=False, refresh_binding=True):
        try:
            parsed_target_string, status = self.action_resolver.compile(
                binding_def,
                self._vars,
                self._context,
            )
            if status != 0:
                raise ConfigurationError(f"Unparseable binding definition: {binding_def}")  # todo: error type
            target_map = parse_target_path(parsed_target_string)
            if unparsed_mode_string:
                modes = unparsed_mode_string.split("__")
                modes.sort()
                mode = "__".join(modes)

            if mode != "default":
                mode = f"__{mode}"

            if self._binding_dict.get(mode) is None:
                raise ConfigurationError(f"Unable to set binding for mode `{mode}`. Mode did not exist on target at startup.")

            self._binding_dict[mode] = target_map
            if refresh_binding:
                self.refresh_binding()
        except Exception as e:
            self.error(f"{e.__class__.__name__}: {e}")

    def apply_listeners(self, listen_dict):
        try:
            if listen_dict.get("selected_track"):
                self.selected_track_listener.subject = self.root_cs.song.view
            else:
                self.selected_track_listener.subject = None

            if listen_dict.get("track_list"):
                self.track_list_listener.subject = self.root_cs.song
            else:
                self.track_list_listener.subject = None

            if listen_dict.get("device_list"):
                self.device_list_listener.subject = self._mapped_track
            else:
                self.device_list_listener.subject = None

            if listen_dict.get("parameter_list"):
                pass
            else:
                pass

            if listen_dict.get("chain_list"):
                self.selected_chain_listener.subject = self.selected_device_watcher
            else:
                self.selected_chain_listener.subject = None

            if listen_dict.get("sends_list"):
                self.return_list_listener.subject = self.root_cs.song
            else:
                self.return_list_listener.subject = None

            if listen_dict.get("selected_parameter"):
                self.selected_parameter_listener.subject = self.root_cs.song.view
            else:
                self.selected_parameter_listener.subject = None

            if listen_dict.get("ring_tracks"):
                self.session_ring_track_listener.subject = self.root_cs._session_ring_custom
                self.track_list_listener.subject = self.root_cs.song
            else:
                self.session_ring_track_listener.subject = None
                self.track_list_listener.subject = None

            if listen_dict.get("selected_device"):
                self.selected_device_listener.subject = self.selected_device_watcher
            else:
                self.selected_device_listener.subject = None

            if self.is_encoder:
                return

            if listen_dict.get("mapped_device_selected") and self._mapped_track:
                self.mapped_device_is_selected_listener.subject = self._mapped_track.view
            else:
                self.mapped_device_is_selected_listener.subject = None

            if listen_dict.get("play_clip"):
                self.playing_slot_index_listener.subject = self._mapped_track
                self.fired_slot_index_listener.subject = self._mapped_track
                self.selected_scene_listener.subject = self.root_cs.song.view
            elif listen_dict.get("stop_clip") and self._mapped_track:
                self.playing_slot_index_listener.subject = self._mapped_track
                self.fired_slot_index_listener.subject = self._mapped_track
            else:
                self.playing_slot_index_listener.subject = None
                self.fired_slot_index_listener.subject = None
                self.selected_scene_listener.subject = None
        except Exception as e:
            self.error(e)

    def bind_ad_hoc(self, binding_def):
        parsed_target_string, status = self.action_resolver.compile(
            binding_def,
            self._vars,
            self._context,
        )

        if status != 0:
            raise ConfigurationError(f"Unparseable binding definition: {binding_def}")

        target_map = parse_target_path(parsed_target_string)
        self._active_map = target_map
        self.bind_to_active()

    def rebind_from_dict(self, lookup_key: str):
        try:
            target_map = self._binding_dict.get(lookup_key or "default")
            if self.is_encoder and type(target_map) is not CommandEncoder:
                self._active_map = target_map
                self._mapped_command = None
                self.bind_to_active()
            else:
                self._active_map = target_map
                if self.is_encoder:
                    self.unbind_control()
                    self._mapped_command = target_map
                    self.mapped_parameter = None
                else:
                    self.bind_to_active()
        except Exception as e:
            self.error(f"{e.__class__.__name__}: {e}")

    def get_device_from_list_by_name(self, device_list, device_name):
        for device in device_list:
            if device.name == device_name:
                return device
            elif hasattr(device, "chains"):
                for chain in device.chains:
                    result = self.get_device_from_list_by_name(
                        chain.devices, device_name
                    )
                    if result is not None:
                        return result
        return None

    def get_track_by_number(self, track_number):
        return self.root_cs._session_ring_custom.get_ring_track(track_number)

    def assess_dynamism(self, target_map) -> dict:

        listen_dict = {
            "selected_track": False,
            "track_list": False,
            "device_list": False,
            "parameter_list": False,
            "chain_list": False,
            "sends_list": False,
            "selected_parameter": False,
            "ring_tracks": False,
            "selected_device": False,
            "mapped_device_selected": False,
            "play_clip": False,
            "stop_clip": False,
        }

        track_def = target_map.get("track")
        if track_def is None and target_map.get("track_select") is not True:
            listen_dict["selected_track"] = False
        elif (isinstance(track_def, str) and track_def.lower() == "sel") or target_map.get("track_select"):
            listen_dict["selected_track"] = True
        else:
            listen_dict["track_list"] = True

        device_def = target_map.get("device")
        if device_def is None:
            listen_dict["selected_device"] = False
            listen_dict["device_list"] = False
        else:
            listen_dict["device_list"] = True
            par_type = target_map.get("parameter_type")
            if isinstance(par_type, str) and par_type.lower() == "sel":
                listen_dict["mapped_device_selected"] = True
            if target_map.get("track") is None:
                listen_dict["selected_track"] = True

        if device_def and device_def.lower() == "sel":
            listen_dict["selected_device"] = True
        elif device_def:
            try:
                int(device_def)
                listen_dict["device_list"] = True
            except ValueError:
                pass

        chain_map = target_map.get("chain_map")
        if chain_map is None:
            pass
        else:
            listen_dict["chain_list"] = True
            listen_dict["device_list"] = True

        sends_def = target_map.get("send_track")
        if sends_def is None:
            pass
        else:
            listen_dict["sends_list"] = True

        if target_map.get('ring_track') is not None:
            listen_dict["ring_tracks"] = True

        if self.is_encoder:
            return listen_dict

        if target_map.get("play"):
            listen_dict["play_clip"] = True
        elif target_map.get("stop"):
            listen_dict["stop_clip"] = True

        if (target_map.get("chain_map") and is_chain_map_positional(target_map["chain_map"])) \
                or (target_map.get("device") and target_map.get("device").isdigit()):
            listen_dict["device_list"] = True
            listen_dict["chain_list"] = True

        return listen_dict

    def map_self_to_par(self, target_map):
        self.debug(f"attempting to bind")
        self.debug(target_map)

        self._mapped_track = None
        if not self.is_encoder:
            self._mapped_device = None
        self.mapped_parameter = None
        try:
            par_type = target_map.get("parameter_type")
            if par_type is not None:
                if par_type.lower() == "selp":
                    self.mapped_parameter = self.song.view.selected_parameter
                    return True
                elif par_type.lower() == "xfader":
                    self.mapped_parameter = self.song.master_track.mixer_device.crossfader
                    return True

            if target_map.get("device") is None and target_map.get("chain_map") is None:
                if not self.is_encoder:
                    self._mapped_device = None
                if target_map.get("track") is not None:
                    track_def = target_map.get("track")
                    track_obj = self.get_track(track_def)
                    if track_obj is None:
                        raise ConfigurationError(f"No track found for {track_def}")
                elif target_map.get("ring_track") is not None:
                    ring_track_def = target_map.get("ring_track")
                    ring_track_parsed, status = self.action_resolver.compile(
                        ring_track_def,
                        self._vars,
                        self._context
                    )
                    if status != 0:
                        raise ConfigurationError(f"Unparseable ring target: {ring_track_def}")

                    track_num = int(ring_track_parsed)

                    track_obj = self.get_track_by_number(track_num)
                    if track_obj is None:
                        raise ConfigurationError(f"Invalid ring target: `{target_map}`")
                else:
                    return False

                self._mapped_track = track_obj
                is_master_track = self._mapped_track == self.song.master_track

                par_type = target_map.get("parameter_type")
                if par_type is None:
                    raise ConfigurationError("Missing parameter_type")

                par_type = par_type.lower()

                if par_type == "vol":
                    self.mapped_parameter = track_obj.mixer_device.volume
                    return True
                elif par_type == "cue":
                    if not is_master_track:
                        self.error(f"target CUE is only available for main track")
                        return False
                    self.mapped_parameter = track_obj.mixer_device.cue_volume
                    return True
                elif not self.is_encoder and target_map.get('track_select'):
                    self.mapped_parameter = None
                    self.apply_track_param_listener(track_obj, "track_select")
                    return True
                elif is_master_track:
                    return False
                ### only targets not available on main track below
                elif par_type == "send":
                    try:
                        send_def = target_map.get("send")
                        if not send_def.isdigit():
                            send_letter = send_def.upper()
                            send_num = ord(send_letter) - 65  # `A` in ASCII
                            sends_count = len(list(self.song.return_tracks))
                            if send_num < 0 or send_num >= sends_count:
                                raise ConfigurationError(
                                    f"Invalid send: {send_letter} | {send_num} | sends_count {sends_count}"
                                )
                        else:
                            send_num = int(send_def)
                            if send_num >= SENDS_COUNT:
                                send_num = send_num % SENDS_COUNT

                        self.mapped_parameter = track_obj.mixer_device.sends[send_num]
                        return True
                    except Exception as e:
                        self.error(e)
                        raise ConfigurationError(f"Failed to bind to send: {e}")

                elif par_type == "pan":
                    self.mapped_parameter = track_obj.mixer_device.panning
                    return True
                elif par_type == "panl":
                    self.mapped_parameter = track_obj.mixer_device.left_split_stereo
                    return True
                elif par_type == "panr":
                    self.mapped_parameter = track_obj.mixer_device.right_split_stereo
                    return True
                elif self.is_encoder:
                    return False
                ### only targets not available on encoders below
                elif target_map.get('arm'):
                    if track_obj.can_be_armed:
                        self.apply_track_param_listener(track_obj, "arm")
                        return True
                    else:
                        return False
                elif target_map.get('monitor'):
                    self.mapped_parameter = None
                    if track_obj.clip_slots[0].is_group_slot:
                        return False
                    self.apply_track_param_listener(track_obj, "monitor")
                    return True
                elif target_map.get('mute'):
                    self.mapped_parameter = None
                    self.apply_track_param_listener(track_obj, "mute")
                    return True
                elif target_map.get('solo'):
                    self.mapped_parameter = None
                    self.apply_track_param_listener(track_obj, "solo")
                    return True
                elif target_map.get('play'):
                    self.mapped_parameter = None
                    self._mapped_track = track_obj
                    return True
                elif target_map.get('stop'):
                    self.mapped_parameter = None
                    self._mapped_track = track_obj
                    return True
                elif target_map.get('x_fade_assign'):
                    self.mapped_parameter = None
                    self.apply_track_param_listener(track_obj, "x_fade_assign")
                    return True
                else:
                    raise ConfigurationError(f"Unsupported parameter type: {par_type}")
            else:
                if target_map.get("track") is not None:
                    track_def = target_map.get("track", "SEL")
                    track_obj = self.get_track(track_def)
                    if track_obj is None:
                        raise ConfigurationError(f"No track found for {track_def}")
                elif target_map.get("ring_track") is not None:
                    ring_track_def = target_map.get("ring_track")
                    ring_track_parsed, status = self.action_resolver.compile(
                        ring_track_def,
                        self._vars,
                        self._context
                    )
                    if status != 0:
                        raise ConfigurationError(f"Unparseable ring target: {ring_track_def}")

                    track_num = int(ring_track_parsed)

                    track_obj = self.get_track_by_number(track_num)
                    if track_obj is None:
                        raise ConfigurationError(f"Invalid ring target: `{target_map}`")
                else:
                    track_obj = self.root_cs.song.view.selected_track

                self._mapped_track = track_obj

                par_def = target_map.get("parameter_name")

                device_def = target_map.get("device")
                chain_map_def = target_map.get("chain_map")

                if device_def is not None:
                    if device_def.lower() == "sel":
                        device_obj = track_obj.view.selected_device
                    else:
                        try:
                            device_def = int(device_def) - 1
                            device_obj = list(track_obj.devices)[device_def]
                        except ValueError:
                            device_obj = self.get_device_from_list_by_name(
                                list(track_obj.devices), device_def
                            )
                        except IndexError as e:
                            if not self.is_encoder:
                                self._mapped_device = None
                                self._disabled = True
                            raise NumberedDeviceMissingError()

                    if device_obj is None:
                        raise ConfigurationError(f"No device found for {device_def}")
                elif chain_map_def is not None:
                    device_obj = self.traverse_chain_map(track_obj, chain_map_def)

                    if hasattr(device_obj, "delete_device"):  # todo: better test for chainy-ness
                        if par_type is None:
                            raise ConfigurationError("Missing parameter_type")  # todo:

                        chain_mixer = device_obj.mixer_device

                        if par_type.lower() == 'vol':
                            self.mapped_parameter = chain_mixer.volume
                            return True
                        elif par_type.lower() == 'pan':
                            self.mapped_parameter = chain_mixer.panning
                            return True
                        elif par_type.lower() == 'send':
                            send_letter = target_map.get("send").upper()
                            send_num = ord(send_letter) - 65
                            self.mapped_parameter = chain_mixer.sends[send_num]
                            return True

                else:
                    raise ConfigurationError("")  # todo:

                if not self.is_encoder:
                    self._mapped_device = device_obj

                if par_type is not None and par_type.lower() == "cs":
                    self.mapped_parameter = device_obj.chain_selector
                    return True

                par_num = target_map.get("parameter_number")
                par_name = target_map.get("parameter_name")

                bank_def = target_map.get("bank")
                if bank_def is not None:
                    bank_num = int(bank_def)
                    banked_param = get_banked_parameter(device_obj, device_obj.class_name, bank_num, int(par_num), self._prefer_left)
                    self.mapped_parameter = banked_param
                    return self.mapped_parameter is not None

                if not self.is_encoder:
                    if par_type is not None and par_type.lower() == "sel":
                        return True

                    if par_type is None and par_name is None and par_num is None:
                        self.mapped_parameter = device_obj.parameters[0]  # bypass parameter
                        return True

                if isinstance(par_name, str):
                    if "${" in par_name:
                        parsed_par_name, status = (
                            parse_target_path(par_num)
                        )
                        if status != 0:
                            raise ConfigurationError(
                                f"Failed to parse parameter: {par_num}"
                            )  # todo
                        par_name = parsed_par_name

                    for par in device_obj.parameters:
                        if par.name == par_name:
                            self.mapped_parameter = par
                            return True

                    raise ConfigurationError(
                        f'Parameter "{par_def}" not found on device {device_def}'
                    )
                else:
                    if isinstance(par_num, str) and "${" in par_num:
                        parsed_par_num, status = parse_target_path(
                            par_num
                        )
                        if status != 0:
                            raise ConfigurationError(
                                f"Failed to parse parameter: {par_num}"
                            )  # todo
                        par_num = parsed_par_num
                    elif isinstance(par_num, int):
                        pass
                    else:
                        try:
                            par_num = int(par_num)
                        except ValueError:
                            raise ConfigurationError(
                                f"Failed to parse parameter: {par_num}"
                            )
                    try:
                        self.mapped_parameter = device_obj.parameters[par_num]
                    except IndexError as e:
                        return False
                    return True
        except NumberedDeviceMissingError:
            raise
        except Exception as e:
            self.error(f"Error in map_self_to_par: {e}")
            self._mapped_track = None
            self.mapped_parameter = None
            if not self.is_encoder:
                self._mapped_device = None
            raise
