from functools import wraps

from ableton.v2.base import EventObject
from ableton.v2.base.task import TimerTask
from ableton.v3.base import listens

def only_in_view(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.in_view:
            return
        return func(self, *args, **kwargs)
    return wrapper


class ZControl(EventObject):

    root_cs = None

    def __init__(
            self,
            root_cs,
            parent_section
    ):
        super().__init__()
        self.root_cs = root_cs
        self.parent_section = parent_section
        self.__state = None
        self.__parent_logger = self.parent_section._logger
        self.__in_view = False
        self.in_view_listener.subject = self.parent_section
        self.gesture_dict = {}
        self.raw_config = {} # temp

    def log(self, *msg):
        for msg in msg:
            self.__parent_logger.info(f'({self.parent_section.name}) {msg}')

    @property
    def in_view(self):
        return self.__in_view

    def bind_to_state(self, state):
        state.register_z_control(self)
        self.__state = state

    def unbind_from_state(self):
        if self.__state is not None:
            self.__state.unregister_z_control(self)

    @only_in_view
    def forward_gesture(self, gesture):
        if gesture in self.gesture_dict:
            self.log(self.gesture_dict[gesture])

    @listens('in_view')
    def in_view_listener(self):
        self.__in_view = self.parent_section.in_view
