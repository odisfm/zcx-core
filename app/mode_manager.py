from copy import copy

from ableton.v2.base.event import listenable_property

from .zcx_component import ZCXComponent
from .errors import CriticalConfigurationError


class ModeManager(ZCXComponent):

    def __init__(
        self,
        name="ModeManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        self.__all_modes = []
        self.__mode_command_dict = {}
        self.__modes_state = {}
        self.__action_resolver = None
        self.__exclusive_modes: dict[str, list[str]] = {} # mode name: list of mode names this mode disables

    def setup(self):
        config = self.yaml_loader.load_yaml(f'{self._config_dir}/modes.yaml')
        self.parse_modes_config(config)

        for mode in self.__all_modes:
            self.__modes_state[mode] = False

        self.__action_resolver = self.component_map['ActionResolver']

        from . import PREF_MANAGER
        from . import STRICT_MODE
        user_prefs = PREF_MANAGER.user_prefs

        exclusive_modes_def = user_prefs.get("exclusive_modes", [])

        invalid_format_msg = (f"Preference `exclusive_modes` must be a list of lists."
                   f"\nProvided {exclusive_modes_def.__class__.__name__}:"
                   f"\n{exclusive_modes_def}")

        if not isinstance(exclusive_modes_def, list):

            if STRICT_MODE:
                raise CriticalConfigurationError(invalid_format_msg)
            else:
                self.critical(invalid_format_msg)
                self.critical("Ignoring exclusive_modes definition.")
                exclusive_modes_def = []

        if len(exclusive_modes_def) > 0:
            for e_group in exclusive_modes_def:
                if not isinstance(e_group, list):
                    raise CriticalConfigurationError(invalid_format_msg)

        modes_to_disabled_modes = {}
        for e_mode_list in exclusive_modes_def:
            for e_mode in e_mode_list:
                if e_mode not in modes_to_disabled_modes:
                    modes_to_disabled_modes[e_mode] = []
                for d_mode in e_mode_list:
                    if d_mode == e_mode:
                        continue
                    modes_to_disabled_modes[e_mode].append(d_mode)

        for key, value in modes_to_disabled_modes.items():
            modes_to_disabled_modes[key] = set(value)

        self.__exclusive_modes = modes_to_disabled_modes

        self.debug(f"Configured mdes: {self.all_modes}")
        self.debug(f"Exclusive modes:", modes_to_disabled_modes)

    def _unload(self):
        super()._unload()
        self.__all_modes = []
        self.__mode_command_dict = {}
        self.__modes_state = {}

    def parse_modes_config(self, raw_config):
        parsed_modes = []
        mode_command_dict = {}

        if not isinstance(raw_config, list):
            raise CriticalConfigurationError(f'`modes.yaml` must be a list')

        recognised_events = ['on_enter', 'on_leave', 'on_toggle']

        for mode_def in raw_config:
            if isinstance(mode_def, str):
                parsed_modes.append(mode_def)
            elif isinstance(mode_def, dict):
                mode_name = mode_def.get('mode')
                if mode_name is None:
                    raise CriticalConfigurationError(f'Error in `modes.yaml`: if mode is dict it must have `mode` key: {mode_def}')
                parsed_modes.append(mode_name)

                for event in recognised_events:
                    if mode_name not in mode_command_dict:
                        mode_command_dict[mode_name] = {}
                    if event in mode_def:
                        mode_command_dict[mode_name][event] = mode_def[event]

        self.__all_modes = parsed_modes
        self.__all_modes.sort()
        self.__mode_command_dict = mode_command_dict

    @property
    def all_modes(self):
        return copy(self.__all_modes)

    @listenable_property
    def current_modes(self):
        return copy(self.__modes_state)

    @property
    def active_modes(self) -> list:
        return [mode for mode, active in self.current_modes.items() if active]

    def add_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self._config_dir}/modes.yaml')
        if self.__modes_state[mode_name] is False:
            self.__modes_state[mode_name] = True
            self.notify_current_modes(self.current_modes)
            self.debug(f'Added mode {mode_name}')
            self._handle_exclusive_mode(mode_name)
            self.__execute_mode_change_command(mode_name, 'on_enter')

    def remove_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self._config_dir}/modes.yaml')
        if self.__modes_state[mode_name] is True:
            self.__modes_state[mode_name] = False
            self.notify_current_modes(self.current_modes)
            self.debug(f'Removed mode {mode_name}')
            self.__execute_mode_change_command(mode_name, 'on_leave')

    def toggle_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self._config_dir}/modes.yaml')
        self.__modes_state[mode_name] = not self.__modes_state[mode_name]
        self.notify_current_modes(self.current_modes)
        self.debug(f'Toggled mode {mode_name}')
        self.__execute_mode_change_command(mode_name, 'on_toggle')

    def is_valid_mode(self, mode):
        return mode in self.__modes_state

    def check_mode_state(self, mode):
        if self.is_valid_mode(mode):
            return self.__modes_state[mode]
        else:
            raise ValueError(f'check_mode_state: Invalid mode {mode}')

    def __execute_mode_change_command(self, mode_name, event):
        command_bundle = self.__mode_command_dict.get(mode_name, {}).get(event, None)
        if command_bundle is None:
            return

        self.__action_resolver.execute_command_bundle(
            calling_control=None,
            bundle=command_bundle,
            vars_dict={},
            context={}
        )

    def _handle_exclusive_mode(self, incoming_mode):
        modes_to_disable = self.__exclusive_modes.get(incoming_mode, [])
        for mode in modes_to_disable:
            self.remove_mode(mode)
