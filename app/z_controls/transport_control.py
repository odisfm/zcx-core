from ableton.v2.base.event import listens

from ..z_control import ZControl
from ..errors import ConfigurationError

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

        swatch = self._control_element.color_swatch

        if True:
            if bound_function == 'play':
                self._playing_active_color = swatch.GREEN_BLINK_SLOW
                self._playing_inactive_color = swatch.WHITE
                self._stopped_active_color = swatch.WHITE
                self._stopped_inactive_color = swatch.WHITE
            elif bound_function == 'session_record':
                self._playing_active_color = swatch.RED_BLINK_SLOW
                self._playing_inactive_color = swatch.RED_HALF
                self._stopped_active_color = swatch.RED
                self._stopped_inactive_color = swatch.RED_HALF
            elif bound_function == 'metronome':
                self._playing_active_color = swatch.FULL_BLINK_SLOW
                self._playing_inactive_color = swatch.HALF
                self._stopped_active_color = swatch.FULL
                self._stopped_inactive_color = swatch.HALF

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
            return

        if self._bound_function == 'play':
            if self._song.is_playing:
                self._color = self._playing_active_color
            elif self._song.is_counting_in:
                self._color = self._playing_active_color
            else:
                self._color = self._stopped_active_color
        elif self._bound_function == 'session_record':
            if self._song.session_record:
                if self._song.is_playing:
                    self._color = self._playing_active_color
                else:
                    self._color = self._stopped_active_color
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
                pass
            else:
                pass

        self._control_element.set_light(self._color)

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
