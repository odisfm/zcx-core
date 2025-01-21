from ableton.v2.base import EventObject, listenable_property
from ableton.v2.base.event import listens


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
        self.__name = section_name
        self.__pages_in = pages_in
        self.__owned_coordinates = owned_coordinates
        self.__width = width
        self.__in_view = False
        self._logger = self.page_manager._logger.getChild(f'matrix_section__{section_name}')
        self.current_page_listener.subject = self.page_manager

        min_y, min_x = self.owned_coordinates[0]
        max_y, max_x = self.owned_coordinates[-1]
        self.__bounds = {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'width': max_x - min_x + 1,
            'height': max_y - min_y + 1
        }

    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)

    @property
    def name(self):
        return self.__name

    @property
    def owned_coordinates(self):
        return self.__owned_coordinates

    @property
    def width(self):
        return self.__width

    @listenable_property
    def in_view(self):
        return self.__in_view

    @listens('current_page')
    def current_page_listener(self):
        page = self.page_manager.current_page
        if page in self.__pages_in:
            self.__in_view = True
        else:
            self.__in_view = False
