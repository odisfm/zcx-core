from ..z_control import ZControl
from ableton.v3.base import listens


class SessionClipControl(ZControl):

    session_view_component = None
    empty_color_dict = None

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.__clip_slot = None
        self.__clip = None
        self.__color_dict = self.empty_color_dict
        self._color = self.empty_color_dict['base']

    def setup(self):
        pass

    def handle_gesture(self, gesture):
        self.log(f'gesture: {gesture}')
        self.session_view_component.handle_gesture(gesture, self.__clip_slot)
        self.log(f'notified session view component')

    def set_clip_slot(self, clip_slot):
        if clip_slot is not None and clip_slot == self.__clip_slot:
            return

        try:
            self.__clip_slot = clip_slot
            self.__set_listeners()
            self.color_index_changed()

            self.log(f'updated clip slot')
        except:
            pass
        self.update_status()

    @listens('has_clip')
    def has_clip_changed(self):
        if self.__clip_slot.has_clip:
            self.__clip = self.__clip_slot.clip
            self.__set_listeners()
        else:
            self.__clip = None
            self.__set_listeners()

    def __set_listeners(self):
        self.__clip = None if not self.__clip_slot.has_clip else self.__clip_slot.clip

        self.is_playing_changed.subject = self.__clip
        self.is_recording.subject = self.__clip
        self.is_triggered.subject = self.__clip_slot
        self.color_index_changed.subject = self.__clip

        track = self.__clip_slot.canonical_parent

        if track.can_be_armed:
            self.track_arm_changed.subject = track
        else:
            self.track_arm_changed.subject = None

    @listens('playing_status')
    def is_playing_changed(self):
        self.update_status()

    @listens('is_recording')
    def is_recording(self):
        self.log(f'im recording')
        self.update_status()

    @listens('is_triggered')
    def is_triggered(self):
        self.update_status()

    @listens('color_index')
    def color_index_changed(self):
        if self.__clip is not None:
            self.__color_dict = self.session_view_component.get_color_dict(self.__clip.color_index)
        else:
            self.__color_dict = self.empty_color_dict

    @listens('arm')
    def track_arm_changed(self):
        self.update_status()

    def update_status(self):
        if self.__clip_slot is None:
            self._color = self.empty_color_dict['base']
        else:
            if self.__clip is not None:
                if self.__clip.is_recording:
                    self._color = self.__color_dict['recording']
                    self.log(f'clip is recording')
                elif self.__clip_slot.is_playing:
                    self._color = self.__color_dict['playing']
                elif self.__clip_slot.is_triggered:
                    self._color = self.__color_dict['triggered_to_play']
                else:
                    self._color = self.__color_dict['base']
            else:
                if self.__clip_slot.is_triggered:
                    track = self.__clip_slot.canonical_parent
                    if track.can_be_armed and track.arm:
                        self._color = self.__color_dict['triggered_to_record']
                    else:
                        self._color = self.__color_dict['triggered_to_play']
                else:
                    if self.__clip_slot.canonical_parent.can_be_armed and self.__clip_slot.canonical_parent.arm:
                        self._color = self.__color_dict['arm']
                    else:
                        self._color = self.empty_color_dict['base']

        self.request_color_update()
        
    def request_color_update(self):
        # self.log(f'doing color update')
        # self.log(self.__color_dict)
        # self.log(self._color)
        super().request_color_update()
        # self.log(f'finished color update')
        # self.log(f'my clip: {self.__clip}')
        # self._control_element.set_light(self._color)

