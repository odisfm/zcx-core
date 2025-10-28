import copy

from ableton.v2.base import EventObject, listenable_property
from ableton.v3.base import listens
from ableton.v3.control_surface import ControlSurface

from .action_resolver import ActionResolver
from .encoder_element import EncoderElement
from .encoder_state import EncoderState
from .errors import ConfigurationError, CriticalConfigurationError
from .mode_manager import ModeManager
from .session_ring import SessionRing
from .bank_definitions import get_banked_parameter
from .parse_target_path import parse_target_path


class ZEncoder(EventObject):

    root_cs: ControlSurface = None
    mode_manager: ModeManager = None
    action_resolver: ActionResolver = None
    session_ring: SessionRing = None
    song = None
    selected_device_watcher = None
    _log_failed_bindings = True

    def __init__(self, root_cs, raw_config, name):
        super().__init__()
        self._control_element = None
        self.root_cs = root_cs
        self._raw_config = raw_config
        self._name = name
        self._logger = self.root_cs.component_map["EncoderManager"]._logger
        self._control_element: EncoderElement = None
        self._state: EncoderState = None
        self._context = {}
        self._vars = {}
        self._default_map = None
        self._mapped_parameter = None
        self._mapped_track = None
        self._concerned_modes = []
        self._current_mode_string = ""
        self._binding_dict = {}
        self._active_map = {}
        self._unbind_on_fail = True
        self._prefer_left = True
        self.modes_changed.subject = self.mode_manager

    def log(self, *msg):
        for msg in msg:
            self._logger.debug(f'({self._name}): {msg}')

    def setup(self):
        self._context = self._raw_config["context"]
        self._vars = self._raw_config.get("vars", {})

        self._unbind_on_fail = self._raw_config.get("unbind_on_fail", self._unbind_on_fail)
        self._prefer_left = self._raw_config.get("prefer_left", self._prefer_left)
        if not isinstance(self._prefer_left, bool):
            self._prefer_left = True

        bindings = self._raw_config.get("binding")
        if isinstance(bindings, dict):
            pass
        elif isinstance(bindings, str):
            bindings = {"default": bindings}
        else:
            raise CriticalConfigurationError(
                f"Invalid binding config for {self._name}"
                f"\n`binding` key must be a dict or a string. was:"
                f"\n{bindings}"
                f"\n\nconfig:"
                f"\n{self._raw_config}"
            )

        binding_dict = {}
        concerned_modes = []

        all_zcx_modes = self.mode_manager.all_modes

        for binding_mode, binding_def in bindings.items():
            if isinstance(binding_def, str):
                binding_params = {}
            elif isinstance(binding_def, dict):
                binding_params = copy.deepcopy(binding_def)
                if "target" in binding_params:
                    binding_def = binding_params["target"]
                    del binding_params["target"]
                else:
                    pass
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
                        raise CriticalConfigurationError(f"Definition for encoder `{self._name}` references mode `{mode}` that does not appear in `modes.yaml`")
                if mode not in concerned_modes:
                    concerned_modes.append(mode)

            these_modes.sort()
            sorted_mode_string = "__".join(these_modes)

            binding_def = binding_def.rstrip('\n')

            parsed_target_string, status = self.action_resolver.compile(
                binding_def,
                self._vars,
                self._context,
            )

            if status != 0:
                raise ConfigurationError(f"Unparseable target\n" f"{binding_def}")

            target_map = parse_target_path(parsed_target_string)

            if target_map["error"] is not None:
                raise ConfigurationError(target_map["error"])

            binding_dict[sorted_mode_string] = target_map

        if "default" in binding_dict:
            self._default_map = binding_dict["default"]

        concerned_modes.sort()
        self._concerned_modes = concerned_modes
        self._binding_dict = binding_dict
        self._active_map = self._default_map

    @property
    def mapped_parameter(self):
        return self._mapped_parameter

    @listenable_property
    def mapped_parameter(self):
        return self._mapped_parameter

    @mapped_parameter.setter
    def mapped_parameter(self, value):
        old = self.mapped_parameter
        self._mapped_parameter = value
        if old != self.mapped_parameter:
            self.notify_mapped_parameter(self.mapped_parameter)
        if self.mapped_parameter:
            if self.mapped_parameter.is_quantized:
                self._control_element.mapping_sensitivity = 0.05
            else:
                self._control_element.mapping_sensitivity = self._control_element._original_sensitivity

    def bind_to_active(self):

        try:
            try:
                if self._active_map is None:
                    map_success = False
                else:
                    map_success = self.map_self_to_par(self._active_map)
            except ConfigurationError:
                map_success = False

            self.log(f'map_success: {map_success}')
            if map_success is not True:
                if self._log_failed_bindings:
                    self._logger.error(f"Failed to bind {self._name} to target: {self._active_map}")
                if self._unbind_on_fail:
                    if self._log_failed_bindings:
                        self.log(f'{self._name} failed to find target, unmapping')
                    self.unbind_control()
                    self.mapped_parameter = None
                    self._mapped_track = None
                return

            self.bind_control()

        except Exception as e:
            if self._log_failed_bindings:
                self._logger.error(f"Failed to bind {self._name} to target: {self._active_map} ....")
            if self._unbind_on_fail:
                if self._log_failed_bindings:
                    self.log(f'{self._name} failed to find target, unmapping')
                self.unbind_control()
                self.mapped_parameter = None
                self._mapped_track = None
            return
        finally:
            dynamism = self.assess_dynamism(self._active_map)
            self.apply_listeners(dynamism)

    def apply_listeners(self, listen_dict):

        if listen_dict.get("selected_track"):
            self.selected_track_listener.subject = self.song.view
        else:
            self.selected_track_listener.subject = None

        if listen_dict.get("track_list"):
            self.track_list_listener.subject = self.song
        else:
            self.track_list_listener.subject = None

        if listen_dict.get("device_list"):
            self.log(f"setting device_list subject to {self._mapped_track}")
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
            self.return_list_listener.subject = self.song
        else:
            self.return_list_listener.subject = None

        if listen_dict.get("selected_parameter"):
            self.selected_parameter_listener.subject = self.song.view
        else:
            self.selected_parameter_listener.subject = None

        if listen_dict.get("ring_tracks"):
            self.session_ring_track_listener.subject = self.session_ring
        else:
            self.session_ring_track_listener.subject = None

        if listen_dict.get("selected_device"):
            self.selected_device_listener.subject = self.selected_device_watcher
        else:
            self.selected_device_listener.subject = None

    def bind_control(self):
        if self._control_element is None:
            return
        self._control_element.connect_to(self.mapped_parameter)

    def unbind_control(self):
        if self._control_element is not None:
            self._control_element.release_parameter()

    def map_self_to_par(self, target_map):

        # perhaps some of the worst code ever written?
        self._logger.debug(target_map)

        self._mapped_track = None
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

                par_type = target_map.get("parameter_type")
                if par_type is None:
                    raise ConfigurationError("Missing parameter_type")

                par_type = par_type.lower()

                if par_type == "vol":
                    self.mapped_parameter = track_obj.mixer_device.volume
                    return True
                elif par_type == "send":
                    try:
                        send_letter = target_map.get("send").upper()
                        send_num = ord(send_letter) - 65  # `A` in ASCII
                        sends_count = len(list(self.song.return_tracks))
                        if send_num < 0 or send_num >= sends_count:
                            raise ConfigurationError(
                                f"Invalid send: {send_letter} | {send_num} | sends_count {sends_count}"
                            )

                        self.mapped_parameter = track_obj.mixer_device.sends[send_num]
                        return True
                    except Exception as e:
                        self.log(e)
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
                elif par_type == "cue":
                    self.mapped_parameter = track_obj.mixer_device.cue_volume
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

                        track_num = int(ring_track_parsed) - 1

                        track_obj = self.get_track_by_number(track_num)
                        if track_obj is None:
                            raise ConfigurationError(f"Invalid ring target: `{target_map}`")
                else:
                    track_obj = self.song.view.selected_track

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
                            return False

                    if device_obj is None:
                        raise ConfigurationError(f"No device found for {device_def}")
                elif chain_map_def is not None:
                    device_obj = self.traverse_chain_map(track_obj, chain_map_def)

                    if hasattr(device_obj, "delete_device"): # todo: better test for chainy-ness
                        if par_type is None:
                            raise ConfigurationError("Missing parameter_type") # todo:

                        chain_mixer = device_obj.mixer_device

                        self.log(target_map)

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
                    raise ConfigurationError("") # todo:

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

        except Exception as e:
            self.log(f"Error in map_self_to_par: {e}")
            raise

    @classmethod
    def get_device_from_list_by_name(cls, device_list, device_name):
        for device in device_list:
            if device.name == device_name:
                return device
            elif hasattr(device, "chains"):
                for chain in device.chains:
                    result = cls.get_device_from_list_by_name(
                        chain.devices, device_name
                    )
                    if result is not None:
                        return result
        return None

    @classmethod
    def get_track_by_number(cls, track_number):
        return cls.session_ring.get_ring_track(track_number)

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
        }

        track_def = target_map.get("track")
        if track_def is None:
            listen_dict["selected_track"] = True
        elif track_def.lower() == "sel":
            listen_dict["selected_track"] = True
        else:
            listen_dict["track_list"] = True

        device_def = target_map.get("device")
        if device_def is None:
            listen_dict["selected_device"] = False
        elif device_def.lower() == "sel":
            listen_dict["device_list"] = True
            listen_dict["selected_device"] = True
        else:
            try:
                int(device_def)
                listen_dict["device_list"] = True
            except ValueError:
                pass

        if target_map.get("track") is None:
            listen_dict["selected_track"] = True

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

        return listen_dict

    def rebind_from_dict(self, lookup_key: str):
        target_map = self._binding_dict.get(lookup_key or "default")
        self._active_map = target_map
        self.bind_to_active()

    def refresh_binding(self):
        self.rebind_from_dict(self._current_mode_string)

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

    def override_binding_definition(self, binding_def, mode='default', unparsed_mode_string=False, refresh_binding=True):
        try:
            parsed_target_string, status = self.action_resolver.compile(
                binding_def,
                self._vars,
                self._context,
            )
            if status != 0:
                raise ConfigurationError(f"Unparseable binding definition: {binding_def}") # todo: error type
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
            self.rebind_from_dict(self._current_mode_string)

        except Exception as e:
            self.log(e)

    @listens("current_modes")
    def modes_changed(self, _):
        old_mode_string = self._current_mode_string
        self.update_mode_string(_)
        if self._current_mode_string == "":
            mode_string = "default"
        else:
            mode_string = self._current_mode_string
        new_mode_string = self._current_mode_string
        if old_mode_string != new_mode_string:
            self.rebind_from_dict(mode_string)

    def update_mode_string(self, mode_states):
        if len(self._concerned_modes) == 0:
            self._current_mode_string = ""
            return

        active_concerned_modes = [
            mode for mode in self._concerned_modes if mode_states.get(mode, False)
        ]

        if not active_concerned_modes:
            self._current_mode_string = ""
            return

        candidates = []

        for binding_key in self._binding_dict.keys():
            if binding_key == "default":
                continue

            if binding_key.startswith("__"):
                clean_key = binding_key[2:]
            else:
                continue

            if clean_key:
                binding_modes = clean_key.split("__")
            else:
                continue

            if all(mode in active_concerned_modes for mode in binding_modes):
                mode_count = len(binding_modes)
                candidates.append((binding_key, mode_count))

        if candidates:
            best_match = min(candidates, key=lambda x: (-x[1], x[0]))
            self._current_mode_string = best_match[0]
        else:
            self._current_mode_string = ""

    @classmethod
    def get_track(cls, track_def):
        tracklist = list(cls.song.tracks)
        try:
            track_num = int(track_def) - 1
            return tracklist[track_num]
        except (ValueError, IndexError):
            track_obj = None
            if track_def.lower() == "sel":
                return cls.song.view.selected_track
            elif track_def.lower() == "mst":
                return cls.song.master_track
            else:
                for track in tracklist:
                    if track.name == track_def:
                        return track
                if track_obj is None:
                    return None

    def traverse_chain_map(self, track, chain_map):
        self.log(f'trying to traverse chain map {chain_map}')

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

            self.log(f'traversing part {i}: {node}')

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
                if isinstance(node, int):
                    current_search_obj = list(current_search_obj.chains)[node - 1]
                else:
                    found = False
                    for chain in current_search_obj.chains:
                        if chain.name == node:
                            current_search_obj = chain
                            found = True
                            break
                    if not found:
                        raise ConfigurationError(f'No chain in {current_search_obj.name} called {node}')

        return current_search_obj


    @listens("selected_track")
    def selected_track_listener(self):
        self.bind_to_active()

    @listens("selected_parameter")
    def selected_parameter_listener(self):
        self.bind_to_active()

    @listens("selected_chain")
    def selected_chain_listener(self, _):
        self.bind_to_active()

    @listens("selected_device")
    def selected_device_listener(self, _):
        self.bind_to_active()

    @listens("devices")
    def device_list_listener(self):
        self.log("device_list_listener")
        self.bind_to_active()

    @listens("tracks")
    def track_list_listener(self):
        self.bind_to_active()

    @listens("chains")
    def chain_list_listener(self):
        self.bind_to_active()

    @listens("parameters")
    def parameter_list_listener(self):
        self.bind_to_active()

    @listens("return_tracks")
    def return_list_listener(self):
        self.bind_to_active()

    @listens("offsets")
    def session_ring_track_listener(self):
        self.bind_to_active()
