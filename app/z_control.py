from functools import wraps

from ableton.v2.base import EventObject
from ableton.v3.base import listens
from ableton.v3.control_surface import ControlSurface
from .colors import parse_color_definition
from .z_element import ZElement


def only_in_view(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.in_view:
            return
        return func(self, *args, **kwargs)
    return wrapper


class ZControl(EventObject):

    root_cs: ControlSurface = None

    def __init__(
            self,
            root_cs,
            parent_section,
            raw_config,
    ):
        super().__init__()
        self.root_cs = root_cs
        self.parent_section = parent_section
        self.__state = None
        self.__parent_logger = self.parent_section._logger
        self.__in_view = False
        self.in_view_listener.subject = self.parent_section
        self.gesture_dict = {}
        self.__raw_config = raw_config
        self.__control_element: Optional[ZElement] = None
        self.__z_manager = self.root_cs.component_map['ZManager']
        self.__color = None
        self._feedback_type = None

    def setup(self):
        config = self.__raw_config
        color = config.get('color', 127)
        # self.log(f'trying to parse {color}')
        color_obj = parse_color_definition(color)
        self.__color = color_obj

    def log(self, *msg):
        for msg in msg:
            self.__parent_logger.info(f'({self.parent_section.name}) {msg}')

    @property
    def in_view(self):
        return self.__in_view

    def bind_to_state(self, state):
        state.register_z_control(self)
        self.__state = state
        self.__control_element = state._control_element
        self._feedback_type = self.__control_element._feedback_type

    def unbind_from_state(self):
        if self.__state is not None:
            self.__state.unregister_z_control(self)
            self.__control_element = None

    @only_in_view
    def forward_gesture(self, gesture):
        if gesture in self.gesture_dict:
            self.log(self.gesture_dict[gesture])

    @listens('in_view')
    def in_view_listener(self):
        self.__in_view = self.parent_section.in_view
        self.request_color_update()

    def set_color_to_base(self):
        self.__control_element.set_light(self.__control_element.color_swatch.base)

    @only_in_view
    def request_color_update(self):
        if self.__color is not None:
            self.__control_element.set_light(self.__color)
