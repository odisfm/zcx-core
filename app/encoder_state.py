from ableton.v3.control_surface.controls import EncoderControl, Connectable


class EncoderState(EncoderControl):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    class State(EncoderControl.State, Connectable):
        pass
