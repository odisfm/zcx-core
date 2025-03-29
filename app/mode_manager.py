from copy import copy

from ableton.v2.base.event import listenable_property

from .zcx_component import ZCXComponent


class ModeManager(ZCXComponent):

    def __init__(
        self,
        name="ModeManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        self.__all_modes = []
        self.__modes_state = {}

    def setup(self):
        config = self.yaml_loader.load_yaml(f'{self._config_dir}/modes.yaml')
        self.__all_modes = config if config is not None else []
        self.__all_modes.sort()
        for mode in self.__all_modes:
            self.__modes_state[mode] = False
        self.debug(f"Configured modes: {self.all_modes}")

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
        self.__modes_state[mode_name] = True
        self.notify_current_modes(self.current_modes)
        self.debug(f'Added mode {mode_name}')

    def remove_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self._config_dir}/modes.yaml')
        self.__modes_state[mode_name] = False
        self.notify_current_modes(self.current_modes)
        self.debug(f'Removed mode {mode_name}')

    def toggle_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self._config_dir}/modes.yaml')
        self.__modes_state[mode_name] = not self.__modes_state[mode_name]
        self.notify_current_modes(self.current_modes)
        self.debug(f'Toggled mode {mode_name}')

    def is_valid_mode(self, mode):
        return mode in self.__modes_state
