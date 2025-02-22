from .zcx_component import ZCXComponent
from .z_element import ZElement
from .z_state import ZState
from .encoder_state import EncoderState


class HardwareInterface(ZCXComponent):

    named_button_states = {}
    encoder_states = {}

    def __init__(
            self,
            name="HardwareInterface",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        self.__button_matrix_element = None
        self.__page_manager = None

    @property
    def button_matrix_element(self):
        return self.__button_matrix_element

    @property
    def button_matrix_state(self):
        return self.button_matrix

    def handle_control_event(self, event, state: ZState.State):
        state.forward_gesture(event)

    def handle_encoder_event(self, encoder_name: str, value: int):
        pass # this might be useful in future for plugins

    def all_lights_full(self):
        for state in self.named_button_states.keys():
            element = getattr(self, state)
            element._control_element.set_light(49)

        for control in self.__button_matrix_element.nested_control_elements():
            control.set_light(9)

    def refresh_all_lights(self):
        count = 0
        for state_name in self.named_button_states.keys():
            element = getattr(self, state_name)
            element.request_color_update()
            count += 1
        for state in self.button_matrix_state:
            state.request_color_update()
            count += 1

        self.log(f'refreshed {count} lights')

    def black_out_lights(self):
        count = 0
        for state_name in self.named_button_states.keys():
            element = getattr(self, state_name)
            element._control_element.set_light(0)
            count += 1
        for state in self.button_matrix_state:
            state._control_element.set_light(0)
            count += 1

    def setup(self):
        self.__button_matrix_element = self.canonical_parent.elements.button_matrix
        self.__page_manager = self.canonical_parent.component_map['PageManager']
