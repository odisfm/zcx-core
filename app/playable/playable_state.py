from typing import TYPE_CHECKING
from functools import partial
from ableton.v3.control_surface.controls import ButtonControl, PlayableControl
from ableton.v3.control_surface.display import Renderable

if TYPE_CHECKING:
    from melodic_component import MelodicComponent


class PlayableState(PlayableControl):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    class State(PlayableControl.State, Renderable):
        melodic_component: "MelodicComponent"


        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.set_mode(2)
            self._suppress_notifications = False
            self._original_id = None

        def _on_value(self, value, *a, **k):
            try:
                self.melodic_component._on_value(self._original_id, value)
            except Exception as e:
                self.log(e)

        def set_control_element(self, control_element):
            try:
                if control_element:
                    self._original_id = control_element.message_identifier()
            except Exception as e:
                self.log(e)
            super().set_control_element(control_element)
