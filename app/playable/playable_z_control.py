from ..z_control import ZControl


class PlayableZControl(ZControl):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._original_id = None
        self._pitch_class = None

    def handle_gesture(self, gesture, dry_run=False, testing=False):
        self.log(gesture)
