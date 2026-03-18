from enum import Enum

from ableton.v2.base import listenable_property
from ableton.v2.base.task import TimerTask
from ableton.v3.base import listens
from ..bindings_mixin import BindingsMixin
from ..colors import parse_color_definition, RgbColor
from ..errors import ConfigurationError, CriticalConfigurationError, NumberedDeviceMissingError
from ..util import to_percentage
from ..z_control import ZControl, only_in_view

UPDATE_RATE = 1 / 3  # 3 times per second


class PressBehaviour(Enum):
    NONE = 0
    TOGGLE = 1
    MOMENTARY = 2


class ParamControl(ZControl, BindingsMixin):
    selected_device_watcher = None

    def __init__(self, *args, **kwargs):
        ZControl.__init__(self, *args, **kwargs)
        BindingsMixin.__init__(self, *args, **kwargs)
        self.__behaviour: PressBehaviour = PressBehaviour.NONE
        self.__is_encoder = False
        self._default_map = None
        self._mapped_parameter = None
        self._binding_dict = {}
        self._active_map = {}
        self._unbind_on_fail = True
        self._mapped_track = None
        self._mapped_device = None
        self.action_resolver = self.root_cs.component_map["ActionResolver"]
        self._log_failed_bindings = True
        self._disabled = True
        self._suppress_animations = True
        self._suppress_animations = True
        self._will_toggle_param = True
        self._concerned_binding_modes = []
        self._current_binding_mode_string = ""
        self._custom_midpoint = None
        self._prefer_left = True
        self.__debounce_feedback_update_task = DebounceFeedbackUpdateTask(self, UPDATE_RATE)
        self.root_cs._task_group.add(self.__debounce_feedback_update_task)

    def setup(self):
        super().setup()
        try:
            self._simple_feedback = False
            self._suppress_animations = True

            self.set_color(5)

            self._vars["me.next_value"] = "me.obj.preview_next_value()"
            self._vars["me.next_pct"] = "me.obj.preview_next_value_percentage()"
            self._vars["me.pct"] = "me.obj.get_current_percentage()"

            self._create_context(
                generated_contexts=
                [
                    self._raw_config.get('section_context', {}),
                    self._raw_config.get('group_context', {}),
                ],
                user_props=self._raw_config.get("props", {})
            )

            self._unbind_on_fail = self._raw_config.get("unbind_on_fail", self._unbind_on_fail)
            self._prefer_left = self._raw_config.get("prefer_left", self._prefer_left)

            behaviour_def = self._raw_config.get("toggle_param", True)
            if behaviour_def is True:
                behaviour = PressBehaviour.TOGGLE
            elif behaviour_def is False:
                behaviour = PressBehaviour.NONE
            elif behaviour_def == "momentary":
                behaviour = PressBehaviour.MOMENTARY
            else:
                self.error("Invalid option for param control `toggle_param`. Valid values are `true`, `false`, or `momentary`")
                behaviour = PressBehaviour.NONE

            self.__behaviour = behaviour

            def get_percentage_def(key):
                pct_def = self._raw_config.get(key)
                if pct_def is not None:
                    try:
                        if isinstance(pct_def, str):
                            if "${" in pct_def:
                                parsed, _status = self.action_resolver.compile(pct_def, self._vars, self._context)
                                if _status != 0:
                                    raise ValueError(f"Unparsable: {pct_def}")
                                pct_def = parsed
                            else:
                                raise ValueError()
                        pct_def = float(pct_def)
                        if pct_def < 0 or pct_def > 100:
                            raise ValueError()
                        return pct_def
                    except ValueError as e:
                        self.error("Option `midpoint` must be a number between 0 and 100.")
                        self.error(e)
                        return None

            self._custom_midpoint = get_percentage_def("midpoint")

            binding = self._raw_config.get("binding")
            if binding is None:
                raise CriticalConfigurationError(
                    f"Invalid binding config in {self.parent_section.name} control {self.name}"
                    f"\n`binding` option missing"
                )

            self._binding_dict, concerned_modes = self.setup_bindings(
                binding,
                self._mode_manager.all_modes,
                allow_command_encoder=False,
            )
            self._concerned_binding_modes = concerned_modes

            self._default_map = self._binding_dict.get("default")
            self._active_map = self._default_map

            color_on_def = self._raw_config.get("on_color") or self._raw_config.get("color")
            if color_on_def is None:
                color_on_def = 127
            color_on = parse_color_definition(color_on_def, self)
            if not color_on:
                color_on = RgbColor(127)

            color_off_def = self._raw_config.get("off_color")
            if color_off_def is None:
                color_off_def = 1
            color_off = parse_color_definition(color_off_def, self)
            if not color_off:
                color_off = RgbColor(1)

            color_disabled_def = self._raw_config.get("disabled_color") or 0
            color_disabled = parse_color_definition(color_disabled_def, self)
            if not color_disabled:
                color_disabled = RgbColor(0)

            self._color_dict = {"on": color_on, "off": color_off, "disabled": color_disabled}
            self._color = self._color_dict["disabled"]

        except Exception as e:
            self.critical(e, e.__class__.__name__)
            raise

    @property
    def song(self):
        return self.root_cs.song

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

    @property
    def is_encoder(self):
        return self.__is_encoder

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
                if self._log_failed_bindings and self._active_map and self._active_map["input_string"] != "NONE":
                    self.error(f"Failed to bind to target: {self._active_map}")
                if self._unbind_on_fail:
                    self.mapped_parameter = None
                    self._mapped_track = None
                    self._mapped_device = None
                    self._disabled = True
                    self.update_feedback()
                return

            self._disabled = False

        except Exception as e:
            self._disabled = True
            self.update_feedback()
            if self._log_failed_bindings and not isinstance(e, NumberedDeviceMissingError) and self._active_map and self._active_map["input_string"] != "NONE":
                self.error(f"{e.__class__.__name__}: {e}")
                self._parent_logger.error(f"Failed to bind to target: {self._active_map}")
        finally:
            dynamism = self.assess_dynamism(self._active_map)
            self.apply_listeners(dynamism)
            self.update_feedback()

    def refresh_binding(self):
        modes = self._mode_manager.current_modes
        self.modes_changed(modes)
        self.bind_to_active()

    def update_feedback(self):
        if self.__debounce_feedback_update_task.is_running:
            return
        self._do_update_feedback()
        self.__debounce_feedback_update_task.restart()

    def _do_update_feedback(self):
        try:
            if self._disabled:
                return self.replace_color(self._color_dict["disabled"])

            if self.mapped_parameter:
                if self._custom_midpoint:
                    current_pct = to_percentage(self.mapped_parameter.min, self.mapped_parameter.max, self.mapped_parameter.value)
                    if current_pct >= self._custom_midpoint:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                else:
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
                elif map.get('x_fade_assign'):
                    assignment_def = map.get('x_fade_assign')
                    current_assignment = self._mapped_track.mixer_device.crossfade_assign
                    assignment_def_int = ["a", "off", "b"].index(assignment_def.lower())

                    if current_assignment == assignment_def_int:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                elif map.get("play"):
                    track = self._mapped_track
                    sel_scene_index = list(self.root_cs.song.scenes).index(self.root_cs.song.view.selected_scene)
                    if track.playing_slot_index == sel_scene_index:
                        if track.fired_slot_index >= 0 and track.fired_slot_index != track.playing_slot_index:
                            self.set_feedback(True)
                        else:
                            self.set_feedback(False)
                    else:
                        if track.clip_slots[sel_scene_index].has_clip:
                            self.set_feedback(True)
                        else:
                            self.set_feedback(False)
                elif map.get("stop"):
                    if self._mapped_track.playing_slot_index >= 0 or self._mapped_track.fired_slot_index >= 0:
                        self.set_feedback(True)
                    else:
                        self.set_feedback(False)
                else:
                    self.replace_color(self._color_dict["disabled"])

        except Exception as e:
            self.error(e)

    def set_feedback(self, status: bool):
        color = self._color_dict["on"] if status else self._color_dict["off"]
        if color != self._color:
            self.replace_color(color)

    @only_in_view
    def handle_gesture(self, gesture, dry_run=False, testing=False):
        was_pressed = self._ZControl__is_pressed
        super().handle_gesture(gesture, dry_run, testing)
        if gesture == "pressed" and (
                self.__behaviour == PressBehaviour.TOGGLE or self.__behaviour == PressBehaviour.MOMENTARY) and self._control_element._last_received_value > self._on_threshold:
            self.toggle_mapped_parameter()
        elif gesture == "released" and self.__behaviour == PressBehaviour.MOMENTARY and was_pressed:
            self.toggle_mapped_parameter()

    def toggle_mapped_parameter(self, preview=False):
        try:
            if self.mapped_parameter:
                if self.mapped_parameter.value == self.mapped_parameter.min:
                    if preview:
                        return self.mapped_parameter.max
                    self.mapped_parameter.value = self.mapped_parameter.max
                elif self.mapped_parameter.value == self.mapped_parameter.max:
                    if preview:
                        return self.mapped_parameter.min
                    self.mapped_parameter.value = self.mapped_parameter.min
                else:
                    if self._custom_midpoint:
                        current_pct = to_percentage(self.mapped_parameter.min, self.mapped_parameter.max, self.mapped_parameter.value)
                        if current_pct > self._custom_midpoint:
                            target_val = self.mapped_parameter.min
                        else:
                            target_val = self.mapped_parameter.max
                        if preview:
                            return target_val
                        self.mapped_parameter.value = target_val
                    else:
                        if preview:
                            return self.mapped_parameter.min
                        self.mapped_parameter.value = self.mapped_parameter.min
            elif self._active_map.get('arm'):
                if not self._mapped_track.can_be_armed:
                    if preview:
                        return None
                    return
                if preview:
                    return not self._mapped_track.arm
                self._mapped_track.arm = not self._mapped_track.arm
            elif self._active_map.get('monitor'):
                current_monitoring_idx = self._mapped_track.current_monitoring_state
                monitoring_states = ["in", "auto", "off"]
                bound_idx = monitoring_states.index(self._active_map.get("monitor").lower())
                if bound_idx in [0, 1]:
                    if current_monitoring_idx == bound_idx:
                        new_idx = int(not bool(bound_idx))
                        if preview:
                            return monitoring_states[new_idx]
                        self._mapped_track.current_monitoring_state = new_idx
                    else:
                        if preview:
                            return monitoring_states[bound_idx]
                        self._mapped_track.current_monitoring_state = bound_idx
                else:
                    if current_monitoring_idx == bound_idx:
                        if preview:
                            return monitoring_states[1]
                        self._mapped_track.current_monitoring_state = 1
                    else:
                        if preview:
                            return monitoring_states[bound_idx]
                        self._mapped_track.current_monitoring_state = bound_idx

            elif self._active_map.get('mute'):
                if preview:
                    return not self._mapped_track.mute
                self._mapped_track.mute = not self._mapped_track.mute
            elif self._active_map.get('solo'):
                if preview:
                    return not self._mapped_track.solo
                self._mapped_track.solo = not self._mapped_track.solo
            elif self._active_map.get('track_select'):
                if preview:
                    return True
                self.root_cs.song.view.selected_track = self._mapped_track
            elif self._active_map.get('x_fade_assign'):
                current_cross_idx = self._mapped_track.mixer_device.crossfade_assign
                assign_states = ["a", "off", "b"]
                bound_idx = assign_states.index(self._active_map.get("x_fade_assign").lower())

                if bound_idx in [0, 2]:
                    if current_cross_idx == bound_idx:
                        new_idx = 2 if bound_idx == 0 else 0
                    else:
                        new_idx = bound_idx
                else:
                    if current_cross_idx == 1:
                        new_idx = 0
                    else:
                        new_idx = 1

                if preview:
                    return assign_states[new_idx]
                self._mapped_track.mixer_device.crossfade_assign = new_idx
            elif self._active_map.get("device") is not None:
                param_type = self._active_map["parameter_type"] or ""
                if param_type.lower() == "sel":
                    if preview:
                        return True
                    self.root_cs.song.view.select_device(self._mapped_device)
            elif self._active_map.get("stop"):
                self._mapped_track.stop_all_clips()
            elif self._active_map.get("play"):
                idx = list(self.root_cs.song.scenes).index(self.root_cs.song.view.selected_scene)
                slot = self._mapped_track.clip_slots[idx]
                slot.fire()
        except Exception as e:
            self.error("failed to toggle mapped param", e)

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

    @listens("playing_slot_index")
    def playing_slot_index_listener(self):
        self.update_feedback()

    @listens("fired_slot_index")
    def fired_slot_index_listener(self):
        self.update_feedback()

    @listens("current_modes")
    def modes_changed(self, _):
        old_mode_string = self._current_binding_mode_string
        super().modes_changed(_)
        if self._current_binding_mode_string == "":
            mode_string = "default"
        else:
            mode_string = self._current_binding_mode_string
        if self._current_binding_mode_string != old_mode_string:
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
            self._current_binding_mode_string = best_match[0]
        else:
            self._current_binding_mode_string = ""

    def preview_next_value(self):
        preview = self.toggle_mapped_parameter(preview=True)
        return preview

    def preview_next_value_percentage(self):
        preview = self.preview_next_value()
        if self.mapped_parameter:
            preview = to_percentage(self.mapped_parameter.min, self.mapped_parameter.max, preview)
        return preview

    def get_current_percentage(self):
        if not self.mapped_parameter:
            return None
        return to_percentage(self.mapped_parameter.min, self.mapped_parameter.max, self.mapped_parameter.value)

    def set_on_color(self, color):
        self._color_dict["on"] = color
        self.update_feedback()

    def set_off_color(self, color):
        self._color_dict["off"] = color
        self.update_feedback()

    def set_color(self, color):
        color_obj = parse_color_definition(color, self)
        self.set_on_color(color_obj)


class DebounceFeedbackUpdateTask(TimerTask):

    def __init__(self, owner, duration, **k):
        super().__init__(duration, **k)
        self.owner: ZControl = owner

    def on_finish(self):
        self.owner._do_update_feedback()
