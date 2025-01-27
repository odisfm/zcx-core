from .z_controls import BasicZControl as Basic
from .z_controls import PageControl as Page
from .z_controls import ModeControl as Mode
from .z_controls import TransportControl as Transport


def get_subclass(class_name):
    class_name = class_name.lower()
    match class_name:
        case "basic":
            return Basic
        case "blank":
            return Basic
        case "page":
            return Page
        case "mode":
            return Mode
        case "transport":
            return Transport
        case _:
            return Basic
