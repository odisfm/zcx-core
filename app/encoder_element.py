from ableton.v3.control_surface.elements import EncoderElement as Element
from ableton.v3.live import application
from ableton.v3.control_surface import MapMode
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE


class EncoderElement(Element):

    def __init__(
            self,
            identifier,
            map_mode,
            is_feedback_enabled,
            channel,
            *a,
            **k
    ):
        super(EncoderElement, self).__init__(
            identifier,
            map_mode=map_mode,
            is_feedback_enabled=is_feedback_enabled,
            channel=channel,
            msg_type=MIDI_CC_TYPE,
            *a,
            **k
        )
        self.name = 'unnamed_encoder_element'


    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)
