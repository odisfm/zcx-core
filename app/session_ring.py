from typing import TYPE_CHECKING
from functools import partial

from ableton.v3.base import listenable_property, EventObject
from ableton.v2.control_surface.components import SessionRingComponent as SessionRingBase
from ableton.v3.base import listens

class SessionRing(SessionRingBase):

    def __init__(self, *a, **k):

        from . import ROOT_LOGGER
        self._logger = ROOT_LOGGER.getChild(self.__class__.__name__)

        self.error = partial(self.log, level='error')
        self.debug = partial(self.log, level='debug')
        self.warning = partial(self.log, level='warning')
        self.critical = partial(self.log, level='critical')

        from . import PREF_MANAGER
        user_prefs = PREF_MANAGER.user_prefs

        width = user_prefs.get('session_ring', {}).get('width', 1)
        height = user_prefs.get('session_ring', {}).get('height', 1)
        self.num_layers = 0

        if height <= 0 or width <= 0:
            height, width = (0, 0)

        super().__init__(num_tracks=width, num_scenes=height, always_snap_track_offset=False,*a, **k)

        from . import CONFIG_DIR

        if TYPE_CHECKING:
            from .page_manager import PageManager
            self.canonical_parent: ZCXCore
            self.page_manager: 'PageManager'

        self._config_dir = CONFIG_DIR
        from .yaml_loader import yaml_loader

        self.yaml_loader = yaml_loader

        self.component_map = self.canonical_parent.component_map

        self.api = RingAPI(self)

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
        if (x < 0 and self.track_offset == 0) or (y < 0 and self.scene_offset <= 0):
            return
        super().move(x, y)
        self.notify_offsets()

    def get_ring_track(self, _index):
        try:
            pos = self.track_offset + _index
            track = self.tracks_to_use()[pos]
            return track
        except IndexError:
            return None

    @listenable_property
    def offsets(self):
        return {
            'track_offset': self.track_offset,
            'scene_offset': self.scene_offset,
        }

class TrackLookup:

    def __init__(self, parent):
        self._parent = parent

    def __getitem__(self, item):
        return self._parent._ring_component.get_ring_track(item).name

class SceneLookup:

    def __init__(self, parent):
        self._parent = parent

    def __getitem__(self, item):
        return self._parent._ring_component.scene_offset + item


class RingAPI(EventObject):

    def __init__(self, component: SessionRing):
        self._ring_component = component
        self.tracks = TrackLookup(self)
        self.scenes = SceneLookup(self)
