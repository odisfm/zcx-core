from ableton.v2.base.event import listens

from ..colors import parse_color_definition
from ..errors import ConfigurationError
from ..z_control import ZControl

AVAILABLE_FUNCTIONS = [
    'play', 'session_record', 'loop', 'metronome'
]


class TransportControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self._suppress_animations = True
        self._song = None
        self._bound_function = None
        self._playing_active_color = None
        self._playing_inactive_color = None
        self._stopped_active_color = None
        self._stopped_inactive_color = None
        
    def setup(self):
        super().setup()

        bound_function = self._raw_config.get('transport')
        
        if bound_function is None:
            raise ConfigurationError('Transport control defined with no `transport` key')

        feedback = self._feedback_type

        if feedback == 'rgb':
            if bound_function == 'play':
                self._playing_active_color = parse_color_definition('play_green', self)
                self._playing_inactive_color = self._playing_active_color
                self._stopped_inactive_color = parse_color_definition('white', self)
                self._stopped_active_color = parse_color_definition({
                    'blink': {
                        'a': 'green',
                        'b': 'white',
                        'speed': 1
                    }
                }, self)
            elif bound_function == 'session_record':
                self._playing_active_color = parse_color_definition('red', self)
                self._playing_inactive_color = parse_color_definition('white', self)
                self._stopped_active_color = parse_color_definition({
                    'blink': {
                        'a': 'red',
                        'b': 'white',
                        'speed': 1
                    }
                }, self)
                self._stopped_inactive_color = parse_color_definition('white', self)
            elif bound_function == 'metronome':
                self._playing_active_color = parse_color_definition({
                    'blink': {
                        'a': 'white',
                        'b': 'grey',
                        'speed': 1
                    }
                }, self)
                self._playing_inactive_color = parse_color_definition('white', self)
                self._stopped_active_color = parse_color_definition('white', self)
                self._stopped_inactive_color = parse_color_definition('white', self)
            elif bound_function == 'loop':
                self._playing_active_color = parse_color_definition("white", self)
                self._playing_inactive_color = self._playing_active_color
                self._stopped_active_color = parse_color_definition('dark_grey', self)
                self._stopped_inactive_color = self._stopped_active_color
        elif feedback == 'biled':
            if bound_function == 'play':
                self._playing_active_color = parse_color_definition('green', self)
                self._playing_inactive_color = parse_color_definition('green', self)
                self._stopped_active_color = parse_color_definition('green_blink_slow', self)
                self._stopped_inactive_color = parse_color_definition('white', self)
            elif bound_function == 'session_record':
                self._playing_active_color = parse_color_definition('red', self)
                self._playing_inactive_color = parse_color_definition('yellow_half', self)
                self._stopped_active_color = parse_color_definition('yellow_half', self)
                self._stopped_inactive_color = parse_color_definition('yellow_half', self)
            elif bound_function == 'metronome':
                self._playing_active_color = parse_color_definition('yellow_blink_slow', self)
                self._playing_inactive_color = parse_color_definition('yellow', self)
                self._stopped_active_color = parse_color_definition('yellow', self)
                self._stopped_inactive_color = parse_color_definition('yellow_half', self)
            elif bound_function == 'loop':
                self._playing_active_color = parse_color_definition('yellow_blink_slow', self)
                self._playing_inactive_color = parse_color_definition('yellow', self)
                self._stopped_active_color = parse_color_definition('yellow', self)
                self._stopped_inactive_color = parse_color_definition('yellow_half', self)
        elif feedback == 'basic':
            if bound_function in ['play', 'session_record', 'loop']:
                self._playing_active_color = parse_color_definition('full', self)
                self._playing_inactive_color = parse_color_definition('half', self)
                self._stopped_active_color = parse_color_definition('full', self)
                self._stopped_inactive_color = parse_color_definition('half', self)
            elif bound_function == 'metronome':
                self._playing_active_color = parse_color_definition('full_blink_slow', self)
                self._playing_inactive_color = parse_color_definition('half', self)
                self._stopped_active_color = parse_color_definition('full', self)
                self._stopped_inactive_color = parse_color_definition('half', self)

        stopped_active_def = self._raw_config.get('active_color')
        if stopped_active_def is not None:
            try:
                active_color_obj = parse_color_definition(stopped_active_def, self)
                playing_active_def = self._raw_config.get('playing_active_color')
                self._stopped_active_color = active_color_obj
                if playing_active_def is not None:
                    playing_color_obj = parse_color_definition(playing_active_def, self)
                    self._playing_active_color = playing_color_obj
                else:
                    self._playing_active_color = self._stopped_active_color
            except Exception as e:
                self.log(e)

        stopped_inactive_def = self._raw_config.get('inactive_color')
        if stopped_inactive_def is not None:
            try:
                inactive_color_obj = parse_color_definition(stopped_inactive_def, self)
                playing_inactive_def = self._raw_config.get('playing_inactive_color')
                self._stopped_inactive_color = inactive_color_obj
                if playing_inactive_def is not None:
                    playing_color_obj = parse_color_definition(playing_inactive_def, self)
                    self._playing_inactive_color = playing_color_obj
                else:
                    self._playing_inactive_color = self._stopped_inactive_color
            except Exception as e:
                self.log(e)

        self._bound_function = bound_function

        self._song = self.root_cs.song

        self._is_playing_listener.subject = self._song
        self._session_record_listener.subject = self._song
        self._metronome_listener.subject = self._song
        self._is_counting_in_listener.subject = self._song
        self._loop_listener.subject = self._song

        self.request_color_update()


    def request_color_update(self):
        if self._bound_function is None:
            self._control_element.set_light(self._color)
        elif self._bound_function == 'play':
            if self._song.is_playing:
                self._color = self._playing_active_color
            elif self._song.is_counting_in:
                self._color = self._stopped_active_color
            else:
                self._color = self._stopped_inactive_color
        elif self._bound_function == 'session_record':
            if self._song.session_record:
                if self._song.is_playing:
                    self._color = self._playing_active_color
                elif song.is_counting_in:
                    self._color = self._stopped_active_color
                else:
                    self._color = self._stopped_inactive_color
            else:
                self._color = self._stopped_inactive_color
        elif self._bound_function == 'metronome':
            if self._song.metronome:
                if self._song.is_playing:
                    self._color = self._playing_active_color
                else:
                    self._color = self._stopped_active_color
            else:
                if self._song.is_playing:
                    self._color = self._playing_inactive_color
                else:
                    self._color = self._stopped_inactive_color
        elif self._bound_function == 'loop':
            if self._song.loop:
                self._color = self._playing_active_color
            else:
                self._color = self._playing_inactive_color

        super().request_color_update()

    @listens('is_playing')
    def _is_playing_listener(self):
        self.request_color_update()

    @listens('session_record')
    def _session_record_listener(self):
        self.request_color_update()

    @listens('is_counting_in')
    def _is_counting_in_listener(self):
        self.request_color_update()

    @listens('loop')
    def _loop_listener(self):
        self.request_color_update()

    @listens('metronome')
    def _metronome_listener(self):
        self.request_color_update()
