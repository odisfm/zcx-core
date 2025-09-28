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

        self.__height = height
        self.__width = width

        from . import PREF_MANAGER

        if TYPE_CHECKING:
            from .page_manager import PageManager
            self.canonical_parent: ZCXCore
            self.page_manager: 'PageManager'

        self._config_dir = PREF_MANAGER.config_dir
        from .yaml_loader import yaml_loader

        self.yaml_loader = yaml_loader

        self.component_map = self.canonical_parent.component_map

        self.api = RingAPI(self)

        self.__osc_server = None
        self.__osc_address_base_prefix = None
        self.__osc_address_track_prefix = None
        self.__osc_address_pos_x_address = None
        self.__osc_address_pos_y_address = None
        self.__does_send_osc_tracks = False
        self.__does_send_osc_positions = False

        self.debug(f'{self.name} created')

    def log(self, *msg, level='info'):
        method = getattr(self._logger, level)
        for m in msg:
            method(m)

    def set_logger_level(self, level):
        level = getattr(logging, level.upper())
        self._logger.setLevel(level)

    def setup(self):
        from . import PREF_MANAGER
        user_prefs = PREF_MANAGER.user_prefs
        osc_prefs = user_prefs.get('osc_output', {})

        if not isinstance(osc_prefs, dict):
            osc_prefs = {}

        self.__does_send_osc_tracks = osc_prefs.get('ring_tracks', False)
        self.__does_send_osc_positions = osc_prefs.get('ring_pos', False)

        self.__osc_server = self.component_map['CxpBridge']._osc_server
        self.__osc_address_base_prefix = f'/zcx/{self.canonical_parent.name}/ring/'
        self.__osc_address_track_prefix = self.__osc_address_base_prefix + f'track/'
        self.__osc_address_pos_x_address = self.__osc_address_base_prefix + f'pos_x/'
        self.__osc_address_pos_y_address = self.__osc_address_base_prefix + f'pos_y/'

        self.update_osc()

    def _unload(self):
        from . import PREF_MANAGER
        self._config_dir = PREF_MANAGER.config_dir
        self.__osc_server = None
        self.__osc_address_base_prefix = None
        self.__osc_address_track_prefix = None
        self.__osc_address_pos_x_address = None
        self.__osc_address_pos_y_address = None

    def move(self, x=0, y=0):
        current_x = self.track_offset
        current_y = self.scene_offset

        if x < 0:
            x = max(x, -current_x)
        if y < 0:
            y = max(y, -current_y)

        if x + current_x >= self.track_count - self.__width:
            x = self.track_count - self.__width - current_x
        if y + current_y >= self.scene_count - self.__height:
            y = self.scene_count - self.__height - current_y

        super().move(x, y)
        new_x = self.track_offset
        new_y = self.scene_offset
        if new_x != current_x or new_y != current_y:
            self.notify_offsets()
            self.update_osc()

    def go_to_track(self, track_id):
        self.log(f'go_to_track {track_id}')
        if isinstance(track_id, int):
            self.set_offsets(track_id, self.scene_offset)
        else:
            for i, track in enumerate(self.tracks_to_use()):
                if track.name == track_id:
                    self.set_offsets(i, self.scene_offset)
                    return True

    def go_to_scene(self, scene_id):

        def parse_scene_ident(scene_full_name):
            if scene_full_name.startswith('['):
                end_bracket = scene_full_name.find(']')
                if end_bracket > 0:
                    return scene_full_name[1:end_bracket]
                elif scene_full_name == '[]':
                    return scene_full_name

        if isinstance(scene_id, int):
            self.set_offsets(self.track_offset, scene_id)
        else:
            scenelist = list(self.song.scenes)
            for i, scene in enumerate(scenelist):
                if scene.name == scene_id or parse_scene_ident(scene.name) == scene_id:
                    self.set_offsets(self.track_offset, i)

    def get_ring_track(self, _index):
        try:
            pos = self.track_offset + _index
            track = self.tracks_to_use()[pos]
            return track
        except IndexError:
            return None

    def update_osc(self):
        if self.__osc_server is None:
            return

        if self.__does_send_osc_tracks:
            for i, track in enumerate(self.tracks_in_view):
                self.__osc_server.sendOSC(f'{self.__osc_address_track_prefix}{i}', track.name)

        if self.__does_send_osc_positions:
            self.__osc_server.sendOSC(self.__osc_address_pos_x_address, self.scene_offset)
            self.__osc_server.sendOSC(self.__osc_address_pos_y_address, self.track_offset)

    @listenable_property
    def offsets(self):
        return {
            'track_offset': self.track_offset,
            'scene_offset': self.scene_offset,
        }

    @property
    def track_count(self):
        return len(self.tracks_to_use())

    @property
    def scene_count(self):
        return len(self.song.scenes)

    @property
    def tracks_in_view(self):
        return self.tracks_to_use()[self.track_offset:self.track_offset + self.num_tracks]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    """
    When using ClyphX Pro script linking, cxp will
    attempt to set these properties and error if there is no setter
    """

    @height.setter
    def height(self, height):
        return

    @width.setter
    def width(self, width):
        return

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
