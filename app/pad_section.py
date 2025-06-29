from copy import copy

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
            width,
            raw_template=None
    ):
        super().__init__()
        self.__name = section_name
        self.__pages_in = pages_in
        self.__owned_coordinates = owned_coordinates
        self.__width = width
        self.__in_view = False
        self._logger = self.page_manager._logger.getChild(
            f"matrix_section__{section_name}"
        )
        self.current_page_listener.subject = self.page_manager

        self.__bounds = None
        if self.__owned_coordinates is not None:
            min_y, min_x = self.owned_coordinates[0]
            max_y, max_x = self.owned_coordinates[-1]
            self.__bounds = {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y,
                "width": max_x - min_x + 1,
                "height": max_y - min_y + 1,
            }
        self.__owned_controls = []
        self._raw_template = raw_template if raw_template is not None else {}

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
    def owned_controls(self):
        return copy(self.__owned_controls)

    @property
    def bounds(self):
        return self.__bounds

    @property
    def width(self):
        return self.__width

    @listenable_property
    def in_view(self):
        return self.__in_view

    @listens("current_page")
    def current_page_listener(self):
        page = self.page_manager.current_page
        if page in self.__pages_in:
            if self.__in_view:
                return
            self.__in_view = True
            self.notify_in_view()
        else:
            if not self.in_view:
                return
            self.__in_view = False
            self.notify_in_view()

    def register_owned_control(self, control):
        self.__owned_controls.append(control)

    def get_row(self, row_num):
        start = row_num * self.__width
        end = start + self.__width
        return self.owned_controls[start:end]

    def get_column(self, column_num):
        controls = []

        if self.__bounds:
            height = self.__bounds["height"]
        else:
            height = len(self.__owned_coordinates) // self.__width

        for row in range(height):
            index = row * self.__width + column_num
            if index < len(self.__owned_coordinates):
                controls.append(self.__owned_controls[index])

        return controls
