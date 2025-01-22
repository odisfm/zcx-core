from .z_controls import BasicZControl as Basic

def get_subclass(class_name):
    class_name = class_name.lower()
    match class_name:
        case 'basic':
            return Basic
        case 'blank':
            return Basic
        case _:
            return Basic
