from functools import partial
from ableton.v3.control_surface.controls import ButtonControl, PlayableControl, ButtonControlBase
from ableton.v3.control_surface.display import Renderable
from ableton.v2.base import lazy_attribute, task

class ZState(PlayableControl):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    class State(PlayableControl.State, Renderable):

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            from . import ROOT_LOGGER
            self.log = partial(ROOT_LOGGER.info)
            self.set_mode(1)
            self.__registered_z_controls = set()
            self._default_delay_time = self._delay_time
            self._default_repeat_rate = ButtonControlBase.REPEAT_RATE
            self._repeat_rate = self._default_repeat_rate
            self._default_double_click_time = ButtonControlBase.DOUBLE_CLICK_TIME
            self._double_click_time = self._default_double_click_time

        def register_z_control(self, z_control):
            self.__registered_z_controls.add(z_control)

        def unregister_z_control(self, z_control):
            self.__registered_z_controls.remove(z_control)

        def forward_gesture(self, gesture):
            for z_control in self.__registered_z_controls:
                z_control.handle_gesture(gesture)

        def request_color_update(self):
            try:
                for z_control in self.__registered_z_controls:
                    if z_control._in_view and z_control._external_light is False:
                        color = z_control._color
                        self._control_element._force_next_send = True
                        self._control_element._do_draw(color)
            except Exception as e:
                try:
                    midi_type = "N" if self._control_element.message_type() == 0 else "CC"
                    self.log(f"Failed to draw color for button CH{self._control_element.message_channel()} {midi_type}{self._control_element.message_identifier()}")
                except:
                    ...
                self.log(e)

        def _unload(self):
            for z_control in self.__registered_z_controls:
                z_control.disconnect()
                del z_control
            self.__registered_z_controls = set()

        def _set_delay_time(self, delay_time):
            self._delay_time = delay_time
            self.__dict__.pop('_delay_task', None)
            self.__dict__.pop('_repeat_task', None)

        def _set_repeat_rate(self, repeat_rate):
            self._repeat_rate = repeat_rate
            self.__dict__.pop('_delay_task', None)
            self.__dict__.pop('_repeat_task', None)

        def _set_double_click_time(self, double_click_time):
            self._double_click_time = double_click_time
            self.__dict__.pop('_double_click_task', None)

        @lazy_attribute
        def _repeat_task(self):
            notify_pressed = partial(self._call_listener, "pressed")
            return self.tasks.add(task.sequence(task.wait(self._delay_time), task.loop(task.wait(self._repeat_rate), task.run(notify_pressed))))

        @lazy_attribute
        def _double_click_task(self):
            return self.tasks.add(task.wait(self._double_click_time))
