from .z_controls import *


def get_subclass(class_name):
    class_name = class_name.lower()
    match class_name:
        case "basic":
            return BasicZControl
        case "standard":
            return BasicZControl
        case "blank":
            return BasicZControl
        case "page":
            return PageControl
        case "mode":
            return ModeControl
        case "transport":
            return TransportControl
        case "track":
            return TrackControl
        case "ring_track":
            return RingTrackControl
        case "param":
            return ParamControl
        case "keyboard":
            return KeyboardControl
        case _:
            return BasicZControl
