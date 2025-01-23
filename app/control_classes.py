from .z_controls import BasicZControl as Basic
from .z_controls import PageControl as Page


def get_subclass(class_name):
    class_name = class_name.lower()
    match class_name:
        case "basic":
            return Basic
        case "blank":
            return Basic
        case "page":
            return Page
        case _:
            return Basic
