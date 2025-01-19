from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import (
    ButtonControl,
    control_matrix
)


class HardwareInterface(Component):

    named_button_states = {}

    def __init__(
            self,
            name="HardwareInterface",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        self.__logger = ROOT_LOGGER.getChild(self.__class__.__name__)

    def log(self, *msg):
        self.__logger.info(*msg)

    def handle_control_event(self, event, button):
        self.log((f'{button._control_element._msg_type} {button._control_element._original_identifier}', event))

    def all_lights_full(self):
        for state in self.named_button_states.keys():
            element = getattr(self, state)
            self.log(dir(element))
            element._control_element.set_light(127)

    def setup(self):
        self.all_lights_full()
