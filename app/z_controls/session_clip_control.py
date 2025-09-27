from ..z_control import ZControl
from ableton.v3.base import listens


class SessionClipControl(ZControl):

    session_view_component = None
    empty_color_dict = None

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.__clip_slot = None
        self.__clip = None
        self._color_dict = self.empty_color_dict
        self._color = self.empty_color_dict['base']
        self._suppress_animations = True
        self._suppress_attention_animations = True

    def setup(self):
        self._vars['track_name'] = 'me.obj.track_name'
        self._vars['clip_target'] = 'me.obj.clip_target'
        self._vars['user_clip_target'] = 'me.obj.user_clip_target'
        self._vars['scene_number'] = 'me.obj.scene_number'
        self._create_context(generated_contexts=[], user_props=self._raw_config.get('props', {}))

        gesture_config = self._raw_config.get('gestures')
        if gesture_config is not None:
            self.set_gesture_dict(gesture_config)

    def set_clip_slot(self, clip_slot):
        if clip_slot is not None and clip_slot == self.__clip_slot:
            return

        try:
            self.__clip_slot = clip_slot
            self.__set_listeners()
            self._on_clip_color_index_changed()

        except:
            pass
        self.update_status()

    @listens('has_clip')
    def _on_has_clip_changed(self):
        if self.__clip_slot.has_clip:
            self.__clip = self.__clip_slot.clip
        else:
            self.__clip = None
        self.__set_listeners()
        self._on_clip_color_index_changed()
        self.update_status()

    def __set_listeners(self):
        self._on_has_clip_changed.subject = self.__clip_slot

        self.__clip = None if not self.__clip_slot.has_clip else self.__clip_slot.clip

        self._on_is_playing_changed.subject = self.__clip
        self._on_is_recording.subject = self.__clip
        self._on_is_triggered.subject = self.__clip_slot
        self._on_clip_color_index_changed.subject = self.__clip

        track = self.__clip_slot.canonical_parent

        if track.can_be_armed:
            self._on_track_arm_changed.subject = track
        else:
            self._on_track_arm_changed.subject = None

    @listens('playing_status')
    def _on_is_playing_changed(self):
        self.update_status()

    @listens('is_recording')
    def _on_is_recording(self):
        self.update_status()

    @listens('is_triggered')
    def _on_is_triggered(self):
        self.update_status()

    @listens('color_index')
    def _on_clip_color_index_changed(self):
        if self.__clip is not None:
            self._color_dict = self.session_view_component.get_color_dict(self.__clip.color_index)
        else:
            self._color_dict = self.empty_color_dict
        self.update_status()

    @listens('arm')
    def track_arm_changed(self):
        self.update_status()

    def update_status(self):
        if self.__clip_slot is None:
            self._color = self.empty_color_dict['base']
        else:
            if self.__clip is not None:
                if self.__clip.is_recording:
                    self._color = self._color_dict['recording']
                elif self.__clip_slot.is_playing:
                    self._color = self._color_dict['playing']
                elif self.__clip_slot.is_triggered:
                    self._color = self._color_dict['triggered_to_play']
                else:
                    self._color = self._color_dict['base']
            else:
                if self.__clip_slot.is_triggered:
                    track = self.__clip_slot.canonical_parent
                    if track.can_be_armed and track.arm:
                        self._color = self._color_dict['triggered_to_record']
                    else:
                        self._color = self._color_dict['triggered_to_play']
                else:
                    if self.__clip_slot.has_stop_button and self.__clip_slot.canonical_parent.can_be_armed and self.__clip_slot.canonical_parent.arm:
                        self._color = self._color_dict['arm']
                    else:
                        self._color = self.empty_color_dict['base']

        self.request_color_update()
        
    def request_color_update(self):
        super().request_color_update()

    @property
    def clip_slot(self):
        return self.__clip_slot

    @property
    def clip(self):
        return self.__clip

    @property
    def scene_index(self):
        if self.__clip_slot is None:
            return 0
        idx = list(self.__clip_slot.canonical_parent.clip_slots).index(self.__clip_slot)
        return idx

    @property
    def scene_number(self):
        return self.scene_index + 1

    @property
    def track_name(self):
        if self.__clip_slot is None:
            return 'NONE'
        else:
            return self.__clip_slot.canonical_parent.name

    @property
    def clip_target(self):
        if self.__clip_slot is None:
            return 'NONE / CLIP(NONE)'
        else:
            return f'"{self.track_name}" / CLIP({self.scene_number})'

    @property
    def user_clip_target(self):
        if self.__clip_slot is None:
            return 'NONE / CLIP(NONE)'
        else:
            return f'"{self.track_name}" / USER_CLIP({self.scene_number})'
