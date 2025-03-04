from typing import TYPE_CHECKING
from functools import partial

from ableton.v2.control_surface.components import SessionRingComponent as SessionRingBase
from ableton.v3.base import listens

class SessionRing(SessionRingBase):

    def __init__(self, *a, **k):

        from . import PREF_MANAGER
        user_prefs = PREF_MANAGER.user_prefs

        width = user_prefs.get('session_ring', {}).get('width', 0)
        height = user_prefs.get('session_ring', {}).get('height', 0)
        self.num_layers = 0

        if height <= 0 or width <= 0:
            raise RuntimeError('session_ring: width and height must be positive')

        super().__init__(num_tracks=width, num_scenes=height, *a, **k)

        from . import ROOT_LOGGER
        from . import CONFIG_DIR

        if TYPE_CHECKING:
            from .page_manager import PageManager
            self.canonical_parent: ZCXCore
            self.page_manager: 'PageManager'

        self._config_dir = CONFIG_DIR
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

    def move(self, x=0, y=0):
        super().move(x, y)
