from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ableton.v3.control_surface.elements import ButtonMatrixElement
    from ableton.v2.control_surface.control.control_list import MatrixControl

from .z_state import ZState
from .zcx_component import ZCXComponent


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
    def button_matrix_element(self) -> "ButtonMatrixElement":
        return self.__button_matrix_element

    @property
    def button_matrix_state(self) -> "MatrixControl.State":
        return self.button_matrix

    def handle_control_event(self, event, state: ZState.State):
        state.forward_gesture(event)

    def refresh_all_lights(self):
        count = 0
        for state_name in self.named_button_states.keys():
            element = getattr(self, f'_button_{state_name}')
            element.request_color_update()
            count += 1
        for state in self.button_matrix_state:
            state.request_color_update()
            count += 1

        self.debug(f'refreshed {count} lights')

    def black_out_lights(self):
        count = 0
        for state_name in self.named_button_states.keys():
            element = getattr(self, f'_button_{state_name}')
            element._control_element.set_light(0)
            count += 1
        for state in self.button_matrix_state:
            state._control_element.set_light(0)
            count += 1

    def setup(self):
        self.__button_matrix_element = self.canonical_parent.elements.button_matrix
        self.__page_manager = self.canonical_parent.component_map['PageManager']

    def _unload(self):
        super()._unload()
        for state_name in self.named_button_states.keys():
            element = getattr(self, f'_button_{state_name}')
            element._unload()
        for state in self.button_matrix_state:
            state._unload()
