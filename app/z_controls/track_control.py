from ableton.v2.base.event import listens

from ..z_control import ZControl
from ..errors import ConfigurationError
from ..colors import parse_color_definition


class TrackControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self._track = None
        self._track_color_dict = {}

    def setup(self):
        super().setup()
        raw_config = self._raw_config

        if 'track' not in raw_config:
            return

        track = raw_config['track']
        if '${' in track:
            parse, status = self.action_resolver.compile(track, self._vars, self._context)
            if status != 0:
                raise ConfigurationError(f'Unparseable track definition: {track}\n'
                                         f'{self._raw_config}')
            track = parse

        self.set_track_by_name(track)

    def set_track(self, track_obj):
        if track_obj is None:
            self._track = None
            return
        self._track = track_obj
        self.build_color_dict()
        self.set_listeners()
        self._context['me']['track'] = track_obj.name
        self.request_color_update()

    def set_listeners(self):
        if self._track is not None:
            self.selected_track_listener.subject = self.root_cs.song.view
            self.playing_slot_listener.subject = self._track
            self.fired_slot_listener.subject = self._track
            self.arm_listener.subject = self._track
            self.color_index_listener.subject = self._track
            if self._track.playing_slot_index >= 0:
                slot = self._track.playing_slot_index
                clip = self._track.clip_slots[slot].clip
                self.is_recording_listener.subject = clip
            else:
                self.is_recording_listener.subject = None
        else:
            self.selected_track_listener.subject = None
            self.playing_slot_listener.subject = None
            self.fired_slot_listener.subject = None
            self.arm_listener.subject = None
            self.is_recording_listener.subject = None
            self.color_index_listener.subject = None

        self.is_playing_listener.subject = self.root_cs.song

    def set_track_by_name(self, track_name):
        if isinstance(track_name, str) and '${' in track_name:
            parse, status = self.action_resolver.compile(track_name, self._vars, self._context)
            if status != 0:
                raise ConfigurationError(f'Unparseable track definition: {track_name}\n'
                                         f'{self._raw_config}')
            track_name = parse
        try:
            track_num = int(track_name)
            track_obj = list(self.root_cs.song.tracks)[track_num]
        except ValueError:
            track_obj = self.get_track_by_name(track_name)
        self.set_track(track_obj)

    def get_track_by_name(self, name):
        tracklist = list(self.root_cs.song.tracks)
        for track in tracklist:
            if track.name == name:
                return track
        return None

    def build_color_dict(self):
        color_dict = {}
        base_index = self._track.color_index
        base_color = parse_color_definition({"live": base_index})
        if base_color is None:
            raise ConfigurationError(f'Unknown color definition: {self._raw_config}') # todo

        color_dict['selected'] = parse_color_definition('white')
        color_dict['base'] = base_color
        color_dict['low'] = base_color

        color_dict['stopped'] = base_color
        color_dict['playing'] = parse_color_definition({'pulse': {
            'a': 'play_green',
            'b': base_color.midi_value,
            'speed': 1
        }})
        color_dict['fired'] = parse_color_definition({'blink': {
            'a': base_index,
            'b': 'grey',
            'speed': 1
        }})
        color_dict['recording'] = parse_color_definition({'pulse': {
            'a': base_index,
            'b': 'red',
            'speed': 1
        }})
        color_dict['stopping'] = parse_color_definition({'blink': {
            'a': base_index,
            'b': 0,
            'speed': 1
        }})
        color_dict['armed'] = parse_color_definition('red')
        color_dict['selected_armed'] = parse_color_definition({'pulse': {
            'a': 'white',
            'b': 'pink',
            'speed': 1
        }})
        color_dict['selected_recording'] = parse_color_definition({'pulse': {
            'a': 'white',
            'b': 'red',
            'speed': 1
        }})
        color_dict['selected_playing'] = parse_color_definition({'pulse': {
            'a': 'play_green',
            'b': 'white',
            'speed': 1
        }})
        color_dict['selected_fired'] = parse_color_definition({'blink': {
            'a': 'white',
            'b': base_index,
            'speed': 1
        }})
        color_dict['selected_stopping'] = parse_color_definition({'blink': {
            'a': 'white',
            'b': 'off',
            'speed': 1
        }})
        color_dict['success'] = parse_color_definition({'pulse': {
            'a': base_index,
            'b': 'play_green',
        }})
        color_dict['attention'] = base_color

        self._color_dict = color_dict

    def determine_status(self):
        if self._track is None:
            return False

        if not self.root_cs.song.is_playing:
            if self._track == self.root_cs.song.view.selected_track:
                self._color = self._color_dict['selected']
            else:
                self._color = self._color_dict['base']
            return True

        playing_index = self._track.playing_slot_index
        fired_index = self._track.fired_slot_index

        is_stopping = False

        if playing_index >= 0:
            playing_clip = self._track.clip_slots[playing_index].clip
            is_playing = True
            is_recording = playing_clip.is_recording
        else:
            playing_clip = None
            is_playing = False
            is_recording = False
        if fired_index >= 0:
            fired_clip = self._track.clip_slots[fired_index].clip
            is_fired = True
        else:
            fired_clip = None
            is_fired = False
            if is_playing and fired_index < -1:
                is_stopping = True

        is_armed = self._track.can_be_armed and self._track.arm

        if self._track == self.root_cs.song.view.selected_track:
            if is_armed:
                if is_recording:
                    self._color = self._color_dict['selected_recording']
                    return True
                elif is_stopping:
                    self._color = self._color_dict['selected_stopping']
                    return True
                elif is_playing:
                    self._color = self._color_dict['selected_playing']
                    return True
                elif is_fired:
                    self._color = self._color_dict['selected_fired']
                    return True

                else:
                    self._color = self._color_dict['selected_armed']
                    return True
            else:
                if is_playing:
                    self._color = self._color_dict['selected_playing']
                    return True
                elif is_fired:
                    self._color = self._color_dict['selected_fired']
                    return True
                elif is_stopping:
                    self._color = self._color_dict['selected_stopping']
                    return True
                else:
                    self._color = self._color_dict['selected']
                    return True
        else:
            if is_armed:
                self._color = self._color_dict['armed']
                return True
            elif is_stopping:
                self._color = self._color_dict['stopping']
                return True
            elif is_playing:
                self._color = self._color_dict['playing']
                return True
            elif is_fired:
                self._color = self._color_dict['fired']
                return True
            else:
                self._color = self._color_dict['stopped']
                return True

    def request_color_update(self):
        if self._track is None:
            super().request_color_update()
        else:
            self.determine_status()
            super().request_color_update()

    @listens('color_index')
    def color_index_listener(self):
        self.build_color_dict()
        self.request_color_update()

    @listens('arm')
    def arm_listener(self):
        self.request_color_update()

    @listens('selected_track')
    def selected_track_listener(self):
        self.request_color_update()

    @listens('playing_slot_index')
    def playing_slot_listener(self):
        slot = self._track.playing_slot_index
        clip = self._track.clip_slots[slot].clip
        if slot >= 0:
            self.is_recording_listener.subject = clip
        else:
            self.is_recording_listener.subject = None
        self.request_color_update()

    @listens('fired_slot_index')
    def fired_slot_listener(self):
        self.request_color_update()

    @listens('is_recording')
    def is_recording_listener(self):
        self.request_color_update()

    @listens('is_playing')
    def is_playing_listener(self):
        self.request_color_update()
