from ableton.v3.control_surface import (
    ControlSurfaceSpecification,
    create_skin
)
from ableton.v3.control_surface.controls import (
    ButtonControl,
    EncoderControl,
    control_matrix,
)
from .elements import Elements
from .hardware_interface import HardwareInterface
from .skin import Skin
from .zcx_core import ZCXCore

import logging
from typing import Type

ROOT_LOGGER = None
NAMED_BUTTONS = None

def create_mappings(arg) -> dict:
    ROOT_LOGGER.info('Creating mappings')
    ROOT_LOGGER.info(NAMED_BUTTONS)

    named_button_names = NAMED_BUTTONS.keys()
    prepare_hardware_interface(named_button_names)

    hw_mapping_dict = {}
    naming_function = Elements.format_attribute_name

    for button_name in named_button_names:
        hw_mapping_dict[button_name] = naming_function(button_name)

    return {
        "HardwareInterface": hw_mapping_dict
    }

def prepare_hardware_interface(button_names) -> Type[HardwareInterface]:
    _hardware_interface = HardwareInterface
    events = ['pressed', 'pressed_delayed', 'released',
              'released_immediately', 'released_delayed', 'double_clicked']

    for button_name in button_names:
        button_state = ButtonControl()
        setattr(_hardware_interface, button_name, button_state)

        _hardware_interface.named_button_states[button_name] = button_state

        for event in events:
            def create_handler(event_type=event, name=button_name):
                def handler(self, button):
                    return self.handle_control_event(event_type, button)

                return handler

            handler_name = f"{button_name}_{event}"
            handler = create_handler()
            setattr(_hardware_interface, handler_name, handler)
            event_decorator = getattr(button_state, event)
            decorated_handler = event_decorator(handler)
            setattr(_hardware_interface, handler_name, decorated_handler)

    return _hardware_interface

class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    create_mappings_function = create_mappings

def create_instance(c_instance):
    global ROOT_LOGGER
    this_dir = __name__.split('.')[0].lstrip('_')
    ROOT_LOGGER = logging.getLogger(this_dir)
    ROOT_LOGGER.setLevel(logging.INFO)

    Specification.component_map = {
        'HardwareInterface': HardwareInterface
    }

    return ZCXCore(Specification, c_instance=c_instance)
