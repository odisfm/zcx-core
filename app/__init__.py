from ableton.v3.control_surface import (
    ControlSurfaceSpecification,
    create_skin
)
from .elements import Elements
from .skin import Skin
from .zcx_core import ZCXCore

import logging

ROOT_LOGGER = None

def create_mappings(arg) -> dict:
    return {}

class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    create_mappings_function = create_mappings

def create_instance(c_instance):
    global ROOT_LOGGER
    this_dir = __name__.split('.')[0].lstrip('_')
    ROOT_LOGGER = logging.getLogger(this_dir)
    ROOT_LOGGER.setLevel(logging.INFO)
    return ZCXCore(Specification, c_instance=c_instance)
