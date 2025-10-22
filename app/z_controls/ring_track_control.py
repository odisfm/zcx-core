from ableton.v3.base import listens
from .track_control import TrackControl
from .session_ring_control import SessionRingControl
from ..colors import RgbColor
from ..z_control import only_in_view


class RingTrackControl(TrackControl, SessionRingControl):

    def __init__(self, *args, **kwargs):
        TrackControl.__init__(self, *args, **kwargs)
        SessionRingControl.__init__(self, *args, **kwargs)
        self.__current_scene_offset = -1
        self.__session_ring = None

    def setup(self):
        try:
            TrackControl.setup(self)
            SessionRingControl.setup(self)
            self.__session_ring = self.root_cs._session_ring_custom
            self.ring_offset_changed.subject = self.__session_ring
            self.ring_offset_changed()

            self._simple_feedback = False

            self.tracks_changed.subject = self.root_cs.song

        except Exception as e:
            self.log(e)

    @listens('offsets')
    @only_in_view
    def ring_offset_changed(self):
        scene_offset = self.__session_ring.offsets['scene_offset']
        if scene_offset == self.__current_scene_offset:
            return
        self.acquire_ring_track()

    @listens('tracks')
    @only_in_view
    def tracks_changed(self):
        self.acquire_ring_track()

    def _back_in_view(self):
        super()._back_in_view()
        self.ring_offset_changed()

    def acquire_ring_track(self):
        try:
            track = self.__session_ring.get_ring_track(self._ring_index)
            self.track = track
        except Exception as e:
            self.track = None
        finally:
            if self.track is None:
                self.replace_color(RgbColor(0))

