from copy import copy

from ableton.v2.base.event import EventObject, listenable_property
from ableton.v3.control_surface import Component, ControlSurface


class ModeManager(Component, EventObject):

    canonical_parent: ControlSurface

    def __init__(
        self,
        name="ModeManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        from . import CONFIG_DIR

        self.__config_dir = CONFIG_DIR
        from .yaml_loader import yaml_loader

        self.yaml_loader = yaml_loader
        self.__logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.log(f'{self.name} created')
        self.component_map = self.canonical_parent.component_map
        self.__all_modes = []
        self.__modes_state = {}

    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)

    def setup(self):
        config = self.yaml_loader.load_yaml(f'{self.__config_dir}/modes.yaml')
        self.__all_modes = config if config is not None else []
        self.__all_modes.sort()
        for mode in self.__all_modes:
            self.__modes_state[mode] = False
        self.log(self.__modes_state)
        self.log(f"Configured modes: {self.all_modes}")

    @property
    def all_modes(self):
        return copy(self.__all_modes)

    @listenable_property
    def current_modes(self):
        return copy(self.__modes_state)

    def add_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self.__config_dir}/modes.yaml')
        self.__modes_state[mode_name] = True
        self.notify_current_modes(self.current_modes)

    def remove_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self.__config_dir}/modes.yaml')
        self.__modes_state[mode_name] = False
        self.notify_current_modes(self.current_modes)

    def toggle_mode(self, mode_name):
        mode = self.__modes_state.get(mode_name)
        if mode is None:
            raise ValueError(f'Mode {mode_name} is not defined in {self.__config_dir}/modes.yaml')
        self.__modes_state[mode_name] = not self.__modes_state[mode_name]
        self.notify_current_modes(self.current_modes)

    def is_valid_mode(self, mode):
        return mode in self.__modes_state
