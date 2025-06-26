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

    def setup(self):
        config = self.yaml_loader.load_yaml(f'{self._config_dir}/modes.yaml')
        self.parse_modes_config(config)

        for mode in self.__all_modes:
            self.__modes_state[mode] = False

        self.__action_resolver = self.component_map['ActionResolver']

        self.debug(f"Configured modes: {self.all_modes}")

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
