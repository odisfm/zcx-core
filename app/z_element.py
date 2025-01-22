from ableton.v3.control_surface.elements import ButtonElement


class ZElement(ButtonElement):

    def __init__(self, *a, **k):
        super(ZElement, self).__init__(*a, **k)
        self.__name = "unnamed_z_element"
        self.__color_swatch = None
        self._feedback_type = None

    @property
    def color_swatch(self):
        return self.__color_swatch
