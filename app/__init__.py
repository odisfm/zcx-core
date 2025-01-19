from ableton.v3.control_surface import (
    ControlSurfaceSpecification,
    create_skin
)
from .elements import Elements
from .skin import Skin
from .zcx_core import ZCXCore

import logging

def create_mappings(arg) -> dict:
    return {}

class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    create_mappings_function = create_mappings

def create_instance(c_instance):
    return ZCXCore(Specification, c_instance=c_instance)
