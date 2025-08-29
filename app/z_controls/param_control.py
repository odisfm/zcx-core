from ..z_control import ZControl
from ableton.v2.base import EventObject, listenable_property
from ableton.v3.base import listens
from ..colors import parse_color_definition, RgbColor
from ..errors import ConfigurationError, CriticalConfigurationError
from ..bank_definitions import get_banked_parameter

class ParamControl(ZControl):

    selected_device_watcher = None

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self._default_map = None
        self._mapped_parameter = None
        self._binding_dict = {}
        self._active_map = {}
        self._unbind_on_fail = True
        self._mapped_track = None
        self._mapped_device = None
        self.action_resolver = self.root_cs.component_map["ActionResolver"]
        self._log_failed_bindings = True
        self.__disabled = True
        self._suppress_animations = True
        self._will_toggle_param = True
        self._concerned_binding_modes = []
        self._current_binding_mode_string = ""

    def setup(self):
        try:
            self.set_color(5)

            self._create_context([
                self._raw_config.get('section_context', {}),
                self._raw_config.get('group_context', {}),
                self._raw_config.get('props', {})
            ])
            self.set_gesture_dict(self._raw_config.get('gestures', {}))
            self._vars = self._raw_config.get("vars", {})

            self._unbind_on_fail = self._raw_config.get("unbind_on_fail", self._unbind_on_fail)

            self._will_toggle_param = self._raw_config.get("toggle_param", True)

            bindings = self._raw_config.get("binding", {})
            if isinstance(bindings, dict):
                pass
            elif isinstance(bindings, str):
                bindings = {"default": bindings}
            else:
                raise CriticalConfigurationError(
                    f"Invalid binding config in {self.parent_section.name}"
                    f"\n`bindings` key must be a dict or a string"
                    f"\n{self._raw_config}"
                )

            binding_dict = {}
            concerned_modes = []

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
                        f"Invalid binding config in {self.parent_section.name}"
                        f"\nBinding definitions must be a dict or a string"
                        f"\n{self._raw_config}"
                    )

                these_modes = binding_mode.split("__")
                for mode in these_modes:
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

                target_map = self.action_resolver.parse_target_path(parsed_target_string)

                if target_map["error"] is not None:
                    raise ConfigurationError(target_map["error"])

                binding_dict[sorted_mode_string] = target_map

            if "default" in binding_dict:
                self._default_map = binding_dict["default"]
            else:
                self._default_map = list(binding_dict.values())[0]

            self._concerned_binding_modes = concerned_modes
            self._binding_dict = binding_dict
            self._active_map = self._default_map

            color_on_def = self._raw_config.get("on_color") or self._raw_config.get("color") or 127
            color_on = parse_color_definition(color_on_def, self)
            if not color_on:
                color_on = RgbColor(127)

            color_off_def = self._raw_config.get("off_color") or 1
            color_off = parse_color_definition(color_off_def, self)
            if not color_off:
                color_off = RgbColor(1)

            color_disabled_def = self._raw_config.get("disabled_color") or 0
            color_disabled = parse_color_definition(color_disabled_def, self)
            if not color_disabled:
                color_disabled = RgbColor(0)

            self._color_dict = {"on": color_on, "off": color_off, "disabled": color_disabled}

        except Exception as e:
            self.log(e, e.__class__.__name__)

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
        self.mapped_param_value_listener.subject = value

    def bind_to_active(self):

        try:

            try:
                if self._active_map is None:
                    map_success = False
                else:
                    map_success = self.map_self_to_par(self._active_map)
            except ConfigurationError:
                map_success = False
            except NumberedDeviceMissingError:
                self.device_list_listener.subject = self._mapped_track
                raise

            if map_success is not True:
                if self._log_failed_bindings:
                    self.log(f"Failed to bind to target: {self._active_map}")
                if self._unbind_on_fail:
                    if self._log_failed_bindings:
                        self.log(f'failed to find target, unmapping')
                    self.mapped_parameter = None
                    self._mapped_track = None
                    self._mapped_device = None
                    self.__disabled = True
                    self.update_feedback()
                return

            self.__disabled = False

        except Exception as e:
            self.__disabled = True
            self.update_feedback()
            self.log(f"{e.__class__.__name__}: {e}")
            if self._log_failed_bindings:
                self._parent_logger.error(f"Failed to bind to target: {self._active_map}")
        finally:
            dynamism = self.assess_dynamism(self._active_map)
            self.apply_listeners(dynamism)
            self.update_feedback()

    def apply_listeners(self, listen_dict):

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
        else:
            self.session_ring_track_listener.subject = None

        if listen_dict.get("selected_device"):
            self.selected_device_listener.subject = self.selected_device_watcher
        else:
            self.selected_device_listener.subject = None

        if listen_dict.get("mapped_device_selected") and self._mapped_track:
            self.mapped_device_is_selected_listener.subject = self._mapped_track.view
        else:
            self.mapped_device_is_selected_listener.subject = None

    def map_self_to_par(self, target_map):
        try:
            self._mapped_track = None
            self._mapped_device = None
            self.mapped_parameter = None
            par_type = target_map.get("parameter_type")
            if par_type is not None and par_type.lower() == "selp":
                self.mapped_parameter = self.song.view.selected_parameter
                if self.mapped_parameter:
                    self._mapped_device = self.song.view.selected_parameter.canoncial_parent
                return True

            if target_map.get("device") is None and target_map.get("chain_map") is None:
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
                        sends_count = len(list(self.root_cs.song.return_tracks))
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
                elif par_type == "xfader":
                    self.mapped_parameter = track_obj.mixer_device.crossfader
                    return True
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
                elif target_map.get('track_select'):
                    self.mapped_parameter = None
                    self.apply_track_param_listener(track_obj, "track_select")
                    return True
                elif target_map.get('play'):
                    self.mapped_parameter = None
                    self.apply_track_param_listener(track_obj, "play")
                    return True
                elif target_map.get('stop'):
                    self.mapped_parameter = None
                    self.apply_track_param_listener(track_obj, "stop")
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

                        track_num = int(ring_track_parsed) - 1

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
                            self._mapped_device = None
                            self.__disabled = True
                            raise NumberedDeviceMissingError()

                    if device_obj is None:
                        raise ConfigurationError(f"No device found for {device_def}")
                elif chain_map_def is not None:
                    device_obj = self.traverse_chain_map(track_obj, chain_map_def)

                    if hasattr(device_obj, "delete_device"): # todo: better test for chainy-ness
                        if par_type is None:
                            raise ConfigurationError("Missing parameter_type") # todo:

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
                    raise ConfigurationError("") # todo:

                self._mapped_device = device_obj

                if par_type is not None and par_type.lower() == "cs":
                    self.mapped_parameter = device_obj.chain_selector
                    return True

                par_num = target_map.get("parameter_number")
                par_name = target_map.get("parameter_name")

                bank_def = target_map.get("bank")
                if bank_def is not None:
                    bank_num = int(bank_def) - 1
                    banked_param_name = get_banked_parameter(device_obj.class_name, bank_num, int(par_num) - 1)
                    for param in list(device_obj.parameters):
                        if param.original_name == banked_param_name:
                            self.mapped_parameter = param
                            return True
                    raise RuntimeError(f"B{bank_num + 1} P{par_num} parameter not found")

                if par_type is not None and par_type.lower() == "sel":
                    return True

                if par_type is None and par_name is None and par_num is None:
                    self.mapped_parameter = device_obj.parameters[0] # bypass parameter
                    return True

                if isinstance(par_name, str):
                    if "${" in par_name:
                        parsed_par_name, status = (
                            self.action_resolver.parse_target_path(par_num)
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
                        parsed_par_num, status = self.action_resolver.parse_target_path(
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
            self.log(f"Error in map_self_to_par: {e}")
            self._mapped_track = None
            self._mapped_device = None
            raise


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
            listen_dict["device_list"] = False
        else:
            listen_dict["device_list"] = True
            par_type = target_map.get("parameter_type")
            if isinstance(par_type, str) and par_type.lower() == "sel":
                listen_dict["mapped_device_selected"] = True

        if device_def and device_def.lower() == "sel":
            listen_dict["selected_device"] = True
        else:
            listen_dict["selected_device"] = False

        chain_map = target_map.get("chain_map")
        if chain_map is None:
            pass
        else:
            listen_dict["chain_list"] = True

        sends_def = target_map.get("send_track")
        if sends_def is None:
            pass
        else:
            listen_dict["sends_list"] = True

        if target_map.get('ring_track') is not None:
            listen_dict["ring_tracks"] = True

        return listen_dict

    def rebind_from_dict(self, lookup_key: str):
        target_map = self._binding_dict.get(lookup_key)

        self._active_map = target_map
        self.bind_to_active()

    def refresh_binding(self):
        modes = self.mode_manager.current_modes
        self.modes_changed(modes)

    def bind_ad_hoc(self, binding_def):
        parsed_target_string, status = self.action_resolver.compile(
            binding_def,
            self._vars,
            self._context,
        )

        if status != 0:
            raise ConfigurationError(f"Unparseable binding definition: {binding_def}")

        target_map = self.action_resolver.parse_target_path(parsed_target_string)
        self._active_map = target_map
        self.bind_to_active()

    def override_binding_definition(self, binding_def, mode='default', refresh_binding=True):
        parsed_target_string, status = self.action_resolver.compile(
            binding_def,
            self._vars,
            self._context,
        )
        if status != 0:
            raise ConfigurationError(f"Unparseable binding definition: {binding_def}") # todo: error type
        target_map = self.action_resolver.parse_target_path(parsed_target_string)
        self._binding_dict[mode] = target_map
        if refresh_binding:
            self.refresh_binding()

    def get_track(self, track_def):
        tracklist = list(self.root_cs.song.tracks)
        try:
            track_num = int(track_def) - 1
            return tracklist[track_num]
        except (ValueError, IndexError):
            track_obj = None
            if track_def.lower() == "sel":
                return self.root_cs.song.view.selected_track
            elif track_def.lower() == "mst":
                return self.root_cs.song.master_track
            else:
                for track in tracklist:
                    if track.name == track_def:
                        return track
                if track_obj is None:
                    return None

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

    def update_feedback(self):
        try:
            if self.__disabled:
                return self.replace_color(self._color_dict["disabled"])

            if self.mapped_parameter:
                if self.mapped_parameter.value == self.mapped_parameter.max:
                    self.set_feedback(True)
                elif self.mapped_parameter.value == self.mapped_parameter.min:
                    self.set_feedback(False)
                else:
                    self.set_feedback(True)
            else:
                map = self._active_map
                if self._mapped_track and map.get("device") and map.get("parameter_type", "").lower() == "sel":
                    if self._mapped_device == self._mapped_track.view.selected_device:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                elif map.get('arm'):
                    if self._mapped_track.can_be_armed:
                        if self._mapped_track.arm:
                            self.set_feedback(True)
                        else:
                            self.set_feedback(False)
                elif map.get('monitor'):
                    monitoring_idx = self._mapped_track.current_monitoring_state
                    if ["in", "auto", "off"].index(self._active_map.get("monitor").lower()) == monitoring_idx:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                elif map.get('mute'):
                    if self._mapped_track.mute:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                elif map.get('solo'):
                    if self._mapped_track.solo:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                elif map.get('track_select'):
                    if self._mapped_track == self.root_cs.song.view.selected_track:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                elif map.get('play'):
                    raise NotImplementedError()
                elif map.get('stop'):
                    raise NotImplementedError()
                elif map.get('x_fade_assign'):
                    assignment_def = map.get('x_fade_assign')
                    current_assignment = self._mapped_track.mixer_device.crossfade_assign
                    assignment_def_int = ["a", "off", "b"].index(assignment_def.lower())

                    if current_assignment == assignment_def_int:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
        except Exception as e:
            self.log(e)

    def set_feedback(self, status: bool):
        color = self._color_dict["on"] if status else self._color_dict["off"]
        self.replace_color(color)

    def handle_gesture(self, gesture):
        super().handle_gesture(gesture)
        if gesture == "pressed" and self._will_toggle_param:
            self.toggle_mapped_parameter()

    def toggle_mapped_parameter(self):
        if self.mapped_parameter:
            if self.mapped_parameter.value == self.mapped_parameter.min:
                self.mapped_parameter.value = self.mapped_parameter.max
            elif self.mapped_parameter.value == self.mapped_parameter.max:
                self.mapped_parameter.value = self.mapped_parameter.min
            else:
                self.mapped_parameter.value = self.mapped_parameter.min
        elif self._active_map.get('arm'):
            if not self._mapped_track.can_be_armed:
                return
            self._mapped_track.arm = not self._mapped_track.arm
        elif self._active_map.get('monitor'):
            current_monitoring_idx = self._mapped_track.current_monitoring_state
            bound_idx = ["in", "auto", "off"].index(self._active_map.get("monitor").lower())
            if bound_idx in [0, 1]:
                if current_monitoring_idx == bound_idx:
                    self._mapped_track.current_monitoring_state = 2
                else:
                    self._mapped_track.current_monitoring_state = bound_idx
            else:
                if current_monitoring_idx == bound_idx:
                    self._mapped_track.current_monitoring_state = 1
                else:
                    self._mapped_track.current_monitoring_state = bound_idx

        elif self._active_map.get('mute'):
            self._mapped_track.mute = not self._mapped_track.mute
        elif self._active_map.get('solo'):
            self._mapped_track.solo = not self._mapped_track.solo
        elif self._active_map.get('track_select'):
            self.root_cs.song.view.selected_track = self._mapped_track
        elif self._active_map.get('play'):
            raise NotImplementedError()
        elif self._active_map.get('stop'):
            raise NotImplementedError()
        elif self._active_map.get('x_fade_assign'):
            current_cross_idx = self._mapped_track.mixer_device.crossfade_assign
            bound_idx = ["a", "off", "b"].index(self._active_map.get("x_fade_assign").lower())
            if bound_idx in [0, 2]:
                if current_cross_idx == bound_idx:
                    self._mapped_track.mixer_device.crossfade_assign = 1
                else:
                    self._mapped_track.mixer_device.crossfade_assign = bound_idx
            else:
                self._mapped_track.mixer_device.crossfade_assign = 1
        elif self._active_map.get("device") is not None:
            param_type = self._active_map["parameter_type"] or ""
            if param_type.lower() == "sel":
                self.root_cs.song.view.select_device(self._mapped_device)

    def apply_track_param_listener(self, track, param: str):
        self.solo_listener.subject = None
        self.mute_listener.subject = None
        self.arm_listener.subject = None
        self.crossfade_assign_listener.subject = None
        self.monitor_listener.subject = None

        match param:
            case "mute":
                self.mute_listener.subject = track
            case "arm":
                self.arm_listener.subject = track
            case "solo":
                self.solo_listener.subject = track
            case "monitor":
                self.monitor_listener.subject = track
            case "x_fade_assign":
                self.crossfade_assign_listener.subject = track.mixer_device

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

    @listens("selected_device")
    def mapped_device_is_selected_listener(self):
        self.update_feedback()

    @listens("devices")
    def device_list_listener(self):
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

    @listens("solo")
    def solo_listener(self):
        self.update_feedback()

    @listens("mute")
    def mute_listener(self):
        self.update_feedback()

    @listens("arm")
    def arm_listener(self):
        self.update_feedback()

    @listens("current_monitoring_state")
    def monitor_listener(self):
        self.update_feedback()

    @listens("selected_scene")
    def selected_scene_listener(self):
        self.update_feedback()

    @listens("playing_slot_index")
    def playing_slot_index_listener(self):
        self.update_feedback()

    @listens("crossfade_assign")
    def crossfade_assign_listener(self):
        self.update_feedback()

    @listens("value")
    def mapped_param_value_listener(self):
        self.update_feedback()

    @listens("current_modes")
    def modes_changed(self, _):
        super().modes_changed(_)
        if self._current_binding_mode_string == "":
            mode_string = "default"
        else:
            mode_string = self._current_binding_mode_string
        self.rebind_from_dict(mode_string)

    def update_mode_string(self, mode_states):
        super().update_mode_string(mode_states)
        if len(self._concerned_binding_modes) == 0:
            self._current_binding_mode_string = ""
            return

        active_concerned_modes = [
            mode for mode in self._concerned_binding_modes if mode_states.get(mode, False)
        ]
        if not active_concerned_modes:
            self._current_binding_mode_string = ""
        else:
            self._current_binding_mode_string = "__" + "__".join(active_concerned_modes)

class NumberedDeviceMissingError(Exception):
    pass
