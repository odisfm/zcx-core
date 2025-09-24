from ableton.v3.control_surface.controls import ButtonControl, PlayableControl
from ableton.v3.control_surface.display import Renderable


class ZState(PlayableControl):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    class State(PlayableControl.State, Renderable):

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.set_mode(1)
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
                if z_control._in_view:
                    color = z_control._color
                    self._control_element._force_next_send = True
                    self._control_element._do_draw(color)

        def _unload(self):
            for z_control in self.__registered_z_controls:
                z_control.disconnect()
                del z_control
            self.__registered_z_controls = set()

