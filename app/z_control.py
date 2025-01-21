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

    def log(self, *msg):
        for msg in msg:
            self.__parent_logger.log(f'({self.parent_section.name}) {msg}')

    def bind_to_state(self, state):
        state.register_z_control(self)
        self.__state = state

    def unbind_from_state(self):
        if self.__state is not None:
            self.__state.unregister_z_control(self)
