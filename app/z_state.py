from ableton.v3.control_surface.controls import ButtonControl
from ableton.v3.control_surface.display import Renderable


class ZState(ButtonControl):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    class State(ButtonControl.State, Renderable):

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.__registered_z_controls = set()

        def register_z_control(self, z_control):
            self.__registered_z_controls.add(z_control)

        def unregister_z_control(self, z_control):
            self.__registered_z_controls.remove(z_control)

        def forward_gesture(self, gesture):
            for z_control in self.__registered_z_controls:
                z_control.handle_gesture(gesture)

        def request_color_update(self):
            for z_control in self.__registered_z_controls:
                z_control.request_color_update()
