from ableton.v3.control_surface import Component, ControlSurface
from ableton.v3.control_surface.controls import (
    ButtonControl,
    control_matrix
)
from .z_state import ZState
from .z_element import ZElement

class HardwareInterface(Component):

    named_button_states = {}
    canonical_parent: ControlSurface

    def __init__(
            self,
            name="HardwareInterface",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        self.__logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.__button_matrix_element = None
        self.__page_manager = None


    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)

    @property
    def button_matrix_element(self):
        return self.__button_matrix_element

    @property
    def button_matrix_state(self):
        return self.button_matrix

    def handle_control_event(self, event, state: ZState.State):
        state.forward_gesture(event)
        # temporary
        element: ZElement = state._control_element
        if element.original_identifier() == 46 and event == 'pressed':
            self.__page_manager.increment_page(1)
        elif element.original_identifier() == 47 and event == 'pressed':
            self.__page_manager.increment_page(-1)

    def all_lights_full(self):
        for state in self.named_button_states.keys():
            element = getattr(self, state)
            element._control_element.set_light(49)

        for control in self.__button_matrix_element.nested_control_elements():
            control.set_light(9)

    def refresh_all_lights(self):
        for state_name in self.named_button_states.keys():
            element = getattr(self, state_name)
            element.request_color_update()
        for state in self.button_matrix_state:
            state.request_color_update()

    def setup(self):
        self.__button_matrix_element = self.canonical_parent.elements.button_matrix
        self.__page_manager = self.canonical_parent.component_map['PageManager']
