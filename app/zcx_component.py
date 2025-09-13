import logging
from functools import partial
from typing import TYPE_CHECKING

from ableton.v2.base.event import EventObject
from ableton.v3.control_surface import Component, ControlSurface

from .zcx_core import ZCXCore


class ZCXComponent(Component, EventObject):

    canonical_parent: ZCXCore

    def __init__(
        self,
        name=None,
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        from . import PREF_MANAGER

        if TYPE_CHECKING:
            from .page_manager import PageManager
            self.canonical_parent: ZCXCore
            self.page_manager: 'PageManager'

        self._config_dir = PREF_MANAGER.config_dir
        from .yaml_loader import yaml_loader

        self.yaml_loader = yaml_loader
        self._logger = ROOT_LOGGER.getChild(self.__class__.__name__)

        self.error = partial(self.log, level='error')
        self.debug = partial(self.log, level='debug')
        self.warning = partial(self.log, level='warning')
        self.critical = partial(self.log, level='critical')

        self.component_map = self.canonical_parent.component_map


        self.debug(f'{self.name} created')

    def log(self, *msg, level='info'):
        method = getattr(self._logger, level)
        for m in msg:
            method(m)

    def set_logger_level(self, level):
        level = getattr(logging, level.upper())
        self._logger.setLevel(level)

    def setup(self):
        raise NotImplementedError("Setup() must be overridden")

    def _unload(self):
        from . import PREF_MANAGER
        self._config_dir = PREF_MANAGER.config_dir
        self.log(f"using config dir {self._config_dir}")
