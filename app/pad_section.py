from ableton.v2.base import EventObject, listenable_property


class PadSection(EventObject):

    root_cs = None
    page_manager = None

    def __init__(
            self,
            section_name,
            owned_coordinates,
            pages_in,
            width
    ):
        super().__init__()
        self.__pages_in = pages_in
        self.__owned_coordinates = owned_coordinates
        self.__width = width
        self.__in_view = False
        self._logger = self.page_manager._logger.getChild(f'matrix_section__{section_name}')
        self.log(f'I appear in pages {pages_in}')

    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)

    @property
    def owned_coordinates(self):
        return self.__owned_coordinates

    @property
    def width(self):
        return self.__width

    @property
    def in_view(self):
        return self.__in_view

