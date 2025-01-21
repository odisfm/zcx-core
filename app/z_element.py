from ableton.v3.control_surface.elements import ButtonElement


class ZElement(ButtonElement):

    def __init__(self):
        super(ZElement, self).__init__()
        self.__name = 'unnamed_z_element'
