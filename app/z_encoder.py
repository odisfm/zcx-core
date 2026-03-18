from functools import partial

from ableton.v2.base import EventObject, listenable_property
from ableton.v2.base.task import TimerTask
from ableton.v3.base import listens
from ableton.v3.control_surface import ControlSurface
from .action_resolver import ActionResolver
from .bindings_mixin import BindingsMixin
from .command_encoder import CommandEncoder
from .encoder_element import EncoderElement
from .encoder_state import EncoderState
from .errors import ConfigurationError, CriticalConfigurationError
from .mode_manager import ModeManager
from .session_ring import SessionRing

ENCODER_UNDO_REFRESH = 2.0


class ZEncoder(EventObject, BindingsMixin):
    root_cs: ControlSurface = None
    mode_manager: ModeManager = None
    action_resolver: ActionResolver = None
    session_ring: SessionRing = None
    song = None
    selected_device_watcher = None
    _log_failed_bindings = True
    undo_duration = 0.50

    def __init__(self, root_cs, raw_config, name, *args, **kwargs):
        EventObject.__init__(self, *args, **kwargs)
        BindingsMixin.__init__(self, *args, **kwargs)
        self._control_element = None
        self.__is_encoder = True
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
        self._mapped_command = None
        self._concerned_modes = []
        self._current_binding_mode_string = ""
        self._binding_dict = {}
        self._active_map = {}
        self._unbind_on_fail = True
        self._prefer_left = True
        self._last_received_value = None
        self.modes_changed.subject = self.mode_manager
        self._undo_step_timer = UndoStepTask(self, duration=self.undo_duration)
        self._undo_step_timer.kill()
        self.root_cs._task_group.add(self._undo_step_timer)

        self.debug = partial(self.log, level="debug")
        self.warning = partial(self.log, level="warning")
        self.error = partial(self.log, level="error")
        self.critical = partial(self.log, level="critical")

    def log(self, *msgs, level="info"):
        log_func = getattr(self._logger, level)
        for msg in msgs:
            log_func(f'({self._name}) {msg}')

    def setup(self):
        self._context = self._raw_config["context"]
        self._vars = self._raw_config.get("vars", {})

        self._unbind_on_fail = self._raw_config.get("unbind_on_fail", self._unbind_on_fail)
        self._prefer_left = self._raw_config.get("prefer_left", self._prefer_left)
        if not isinstance(self._prefer_left, bool):
            self._prefer_left = True

        sens_def = self._raw_config.get("sensitivity")
        if sens_def:
            if isinstance(sens_def, int):
                sens_def = float(sens_def)
            elif isinstance(sens_def, float):
                pass
            else:
                raise CriticalConfigurationError(
                    f"Encoder `{self._name}`: invalid value for option `sensitivity`"
                    f" (`{sens_def}`). Must be positive number."
                )
            if sens_def <= 0:
                raise CriticalConfigurationError(
                    f"Encoder `{self._name}`: invalid value for option `sensitivity`"
                    f" (`{sens_def}`). Must be positive number."
                )
            self.log(f"setting sens to {sens_def}")
            self._control_element.mapping_sensitivity = sens_def
            self._control_element._original_sensitivity = sens_def

        bindings_raw = self._raw_config.get("binding")
        self._binding_dict, concerned_modes = self.setup_bindings(
            bindings_raw,
            self.mode_manager.all_modes,
            allow_command_encoder=True,
        )
        self._concerned_modes = concerned_modes

        self._default_map = self._binding_dict.get("default")
        if type(self._default_map) == CommandEncoder:
            self._mapped_command = self._default_map
        else:
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

    @property
    def is_encoder(self):
        return self.__is_encoder

    def bind_to_active(self):

        try:
            try:
                if self._mapped_command is not None:
                    return True
                if self._active_map is None:
                    map_success = False
                else:
                    map_success = self.map_self_to_par(self._active_map)
            except ConfigurationError:
                map_success = False

            self.debug(f'map_success: {map_success}')
            if map_success is not True:
                if self._log_failed_bindings and self._active_map and self._active_map["input_string"] != "NONE":
                    self.error(f"Failed to bind {self._name} to target: {self._active_map}")
                if self._unbind_on_fail:
                    if self._log_failed_bindings:
                        self.debug(f'{self._name} failed to find target, unmapping')
                    self.unbind_control()
                    self.mapped_parameter = None
                    self._mapped_track = None
                return

            self.bind_control()

        except Exception as e:
            if self._log_failed_bindings and self._active_map and self._active_map["input_string"] != "NONE":
                self.error(f"Failed to bind {self._name} to target: {self._active_map} ....")
            if self._unbind_on_fail:
                if self._log_failed_bindings:
                    self.debug(f'{self._name} failed to find target, unmapping')
                self.unbind_control()
                self.mapped_parameter = None
                self._mapped_track = None
            return
        finally:
            dynamism = self.assess_dynamism(self._active_map)
            self.apply_listeners(dynamism)

    def bind_control(self):
        if self._control_element is None:
            return
        self._control_element.connect_to(self.mapped_parameter)

    def unbind_control(self):
        if self._control_element is not None:
            self._control_element.release_parameter()

    def refresh_binding(self):
        self.rebind_from_dict(self._current_binding_mode_string)

    @listens("current_modes")
    def modes_changed(self, _):
        old_mode_string = self._current_binding_mode_string
        self.update_mode_string(_)
        if self._current_binding_mode_string == "":
            mode_string = "default"
        else:
            mode_string = self._current_binding_mode_string
        if self._current_binding_mode_string != old_mode_string:
            self.rebind_from_dict(mode_string)

    def update_mode_string(self, mode_states):
        if len(self._concerned_modes) == 0:
            self._current_binding_mode_string = ""
            return

        active_concerned_modes = [
            mode for mode in self._concerned_modes if mode_states.get(mode, False)
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

    def _on_element_value(self, value):
        self._last_received_value = value
        if self._mapped_command:
            self._mapped_command._receive_value(value)
        else:
            if self._undo_step_timer.is_running:
                self._undo_step_timer._reset_timer()
            else:
                self.song.begin_undo_step()
                self._undo_step_timer.restart()
        self.notify_received_value()

    @listenable_property
    def received_value(self):
        return self._last_received_value

    def _undo_timer_finished(self):
        self.song.end_undo_step()

    def _undo_timer_time_out(self):
        self.song.end_undo_step()
        self.song.begin_undo_step()
        self._undo_step_timer.restart()

    def refresh_feedback(self):
        return

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
        self.debug("device_list_listener")
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


class UndoStepTask(TimerTask):

    def __init__(self, encoder, duration, *a, **kw):
        super().__init__(duration)
        self._encoder = encoder
        self._accumulated_time = 0.0

    def on_finish(self):
        self._encoder._undo_timer_finished()

    def _reset_timer(self):
        elapsed = self.duration - self.remaining
        self._accumulated_time += elapsed

        if self._accumulated_time > ENCODER_UNDO_REFRESH:
            self._accumulated_time = 0.0
            self._encoder._undo_timer_time_out()
        else:
            self.restart()

    def restart(self):
        super().restart()
