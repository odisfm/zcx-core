from functools import wraps, partial
from typing import Optional

from ableton.v2.base import EventObject
from ableton.v2.base.task import TimerTask
from ableton.v3.base import listens
from ableton.v3.control_surface import ControlSurface

from .colors import parse_color_definition, simplify_color, Pulse, Blink
from .consts import SUPPORTED_GESTURES, DEFAULT_ON_THRESHOLD, ON_GESTURES, OFF_GESTURES
from .errors import ConfigurationError
from .z_element import ZElement
from .z_state import ZState
from .pseq import Pseq


def only_in_view(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.in_view:
            return
        return func(self, *args, **kwargs)
    return wrapper


class ZControl(EventObject):

    root_cs: ControlSurface = None

    def __init__(
            self,
            root_cs,
            parent_section,
            raw_config,
            button_name
    ):
        super().__init__()
        self.root_cs = root_cs
        self.parent_section = parent_section
        if button_name:
            self.__name = button_name
        else:
            x = raw_config.get('section_context', {}).get('x', -1)
            y = raw_config.get('section_context', {}).get('y', -1)
            self.__name = f"{self.parent_section.name}_{x}_{y}"
        self.__state: Optional[ZState] = None
        self._parent_logger = self.parent_section._logger
        self._in_view = False
        self.in_view_listener.subject = self.parent_section
        self._raw_config = raw_config
        self._control_element: ZElement = None
        self.__z_manager = self.root_cs.component_map['ZManager']
        self._color = None
        self._simple_feedback = False
        self._hold_color = None
        self._initial_color_def = None
        self._color_swatch = None
        self._color_dict = {}
        self._context = {}
        self._gesture_dict = {}
        self._concerned_modes = []
        self._vars = {}
        self._feedback_type = None
        self._mode_manager = self.root_cs.component_map['ModeManager']
        self.modes_changed.subject = self._mode_manager
        self._is_animating = False
        self._suppress_animations = False
        self._suppress_attention_animations = False
        self._animate_on_release = False
        self._current_animation_task = None
        self._current_mode_string = ''
        self._cascade_direction = False
        self._fake_momentary = False
        self._last_received_value = 0
        self._repeat = False
        self._trigger_action_list = partial(self.root_cs.component_map['CxpBridge'].trigger_action_list)
        self._on_threshold = DEFAULT_ON_THRESHOLD
        self._resolve_command_bundle = partial(
            self.root_cs.component_map['ActionResolver'].execute_command_bundle,
            calling_control=self,
        )
        self.parent_section.register_owned_control(self)

    def setup(self):
        config = self._raw_config
        self._create_context([
            config.get('section_context', {}),
            config.get('group_context', {}),
            config.get('props', {})
        ])
        color = config.get('color', 127)
        self.set_gesture_dict(config.get('gestures', {}))
        self.set_vars(config.get('vars', {}))
        self.set_color(color)
        on_threshold = int(config.get('threshold', DEFAULT_ON_THRESHOLD))
        self._on_threshold = on_threshold
        suppress_animations = config.get('suppress_animations', False)
        simple_feedback_color_def = config.get('hold_color', False)
        if simple_feedback_color_def:
            self._simple_feedback = True
            self._animate_on_release = False
            simple_feedback_color = parse_color_definition(simple_feedback_color_def, self)
            self._hold_color = simple_feedback_color

        self._suppress_animations = suppress_animations
        self._fake_momentary = config.get('tog_to_mom', False)
        self._repeat = config.get('repeat', False)

        self._cascade_direction = config.get('cascade', False)
        if self._cascade_direction not in [False, "up", "down"]:
            self.log(f"Invalid cascade direction `{self._cascade_direction}`, disabling cascade.")
            self._cascade_direction = False

    def log(self, *msg):
        for msg in msg:
            self._parent_logger.info(f'({self.parent_section.name}) {msg}')

    @property
    def in_view(self):
        return self._in_view

    @property
    def context(self):
        return self._context

    @property
    def color(self):
        return self._color

    @property
    def name(self):
        return self.__name

    def set_gesture_dict(self, gesture_config):
        if type(gesture_config) is not dict:
            raise ValueError(f'gesture_config must be a dict: {gesture_config}')

        processed_dict = {}
        all_modes = []

        has_off_gestures = False
        has_on_gestures = False

        for trigger, definition in gesture_config.items():
            split = trigger.split('__')
            gesture = split[0]
            if gesture not in SUPPORTED_GESTURES:
                # todo: replace with ConfigError
                raise ValueError(f"'{gesture}' is not a valid gesture ({SUPPORTED_GESTURES})")
            if gesture in OFF_GESTURES:
                has_off_gestures = True
            elif gesture in OFF_GESTURES:
                has_on_gestures = True
            modes = split[1:] if len(split) > 1 else []
            modes.sort()
            for mode in modes:
                if not self._mode_manager.is_valid_mode(mode):
                    raise ValueError(f"'{mode}' is not configured in config/modes.yaml")
                if mode not in all_modes:
                    all_modes.append(mode)

            new_key = gesture if not modes else f"{gesture}__{('__'.join(modes))}"

            if isinstance(definition, dict):
                first_key = next(iter(definition.keys()))
                first_val = definition[first_key]
                pseq_obj = None

                if first_key == 'pseq':
                    pseq_obj = Pseq(first_val, False)
                elif first_key == 'rpseq':
                    pseq_obj = Pseq(first_val, True)

                definition = pseq_obj or definition

            processed_dict[new_key] = definition

        if has_off_gestures and not has_on_gestures:
            self._animate_on_release = True

        all_modes.sort()
        self._concerned_modes = all_modes
        self._gesture_dict = processed_dict

    def set_vars(self, vars):
        self._vars = vars

    def _create_context(self, config: list[dict]) -> None:
        context = {k: v for d in config for k, v in d.items()}
        if 'index' not in context:
            if 'group_index' in context:
                context['index'] = context['group_index']
            else:
                context['index'] = 0
        context['Index'] = context['index'] + 1
        me_context = {'me': context}
        self._context = me_context

        self.set_prop('vel', 0)
        self.set_prop('velp', 0.0)
        self.set_prop('velps', 0.0)

        self.set_prop('obj', self)

    def bind_to_state(self, state):
        state.register_z_control(self)
        self.__state = state
        self._control_element = state._control_element
        self._feedback_type = self._control_element._feedback_type
        self._color_swatch = self._control_element.color_swatch

    def unbind_from_state(self):
        if self.__state is not None:
            self.__state.unregister_z_control(self)
            self._control_element = None

    @classmethod
    def re_range_percent(cls, val, _min, _max):
        if val <= _min:
            return 0
        if val >= _max:
            return 100
        return (val - _min) / (_max - _min) * 100

    @only_in_view
    def handle_gesture(self, gesture):
        val = self._control_element._last_received_value
        self._last_received_value = val
        if self._fake_momentary:
            if gesture in ['pressed', 'released']:
                gesture = 'pressed'
            else:
                return
        elif 'pressed' in gesture and val < self._on_threshold:
            return

        if self._simple_feedback:
            if gesture == 'pressed':
                self._do_simple_feedback_held()
            elif gesture == 'released':
                self._do_simple_feedback_release()

        elif gesture in ['pressed', 'double_clicked']:
            self.set_prop('vel', val)
            vel_p = round((val / 127) * 100, 1)
            vel_p_s = round(self.re_range_percent(val, self._on_threshold, 127), 1)
            self.set_prop('velp', vel_p)
            self.set_prop('velps', vel_p_s)

        lookup_key = gesture + self._current_mode_string
        matching_actions = []

        if not self._cascade_direction:
            if action := self._gesture_dict.get(lookup_key):
                matching_actions.append(action)
        else:
            candidates = []

            for key, action in self._gesture_dict.items():
                parts = key.split("__")
                if parts[0] != gesture:
                    continue

                if len(parts) == 1:
                    mode_count = 0
                    candidates.append((action, mode_count))
                    continue

                mode_part = "__" + "__".join(parts[1:])

                if mode_part in self._current_mode_string:
                    mode_count = len(parts) - 1
                    candidates.append((action, mode_count))

            matching_actions = [action for action, _ in
                                sorted(candidates, key=lambda x: x[1], reverse=self._cascade_direction == "up")]

        if len(matching_actions) == 0:
            return

        for command in matching_actions:

            if self.is_pseq(command):
                command = command.get_next_command()

            self._resolve_command_bundle(
                bundle=command,
                vars_dict=self._vars,
                context=self._context
            )

        if not self._simple_feedback and (gesture in ON_GESTURES or (gesture in OFF_GESTURES and self._animate_on_release)) and self._suppress_animations is False:
            self.animate_success()

    @listens('in_view')
    def in_view_listener(self):
        back_in_view = not self.in_view and self.parent_section.in_view
        self._in_view = self.parent_section.in_view
        if back_in_view:
            self._back_in_view()

    def _back_in_view(self):
        self.request_color_update()
        if self._simple_feedback:
            if not self._control_element.is_pressed:
                self._do_simple_feedback_release()
        self.__state._repeat = self._repeat

    def set_color_to_base(self):
        self._control_element.set_light(self._control_element.color_swatch.base)

    @only_in_view
    def request_color_update(self):
        if self._color is not None:
            self._control_element.set_light(self._color)
        else:
            self.log(f'cant update color, it is None')

    def set_color(self, color):
        try:
            base_color = parse_color_definition(color, self)
        except Exception as e:
            self.log(e)
            base_color = parse_color_definition(127, self)

        simplified_color = simplify_color(base_color)
        white = parse_color_definition('white', self)
        green = parse_color_definition('green', self)
        play_green = parse_color_definition('play_green', self)
        red = parse_color_definition('red', self)
        off = parse_color_definition('0', self)

        if self._feedback_type == 'rgb':
            attention_color = Pulse(simplified_color, white, 48)
            animate_success = Blink(simplified_color, play_green, 12)
            animate_failure = Blink(simplified_color, red, 4)
        elif self._feedback_type == 'basic':
            attention_color = base_color
            animate_success = Blink(simplified_color, off, 48)
            animate_failure = Blink(simplified_color, off, 12)
        elif self._feedback_type == 'biled':
            attention_color = base_color
            animate_success = Pulse(simplified_color, green, 48)
            animate_failure = Blink(simplified_color, red, 12)
        else:
            raise ConfigurationError(f'Unknown feedback type: {self._feedback_type}')

        color_dict = {
            "base": base_color,
            "simple": simplified_color,
            "success": animate_success,
            "failure": animate_failure,
            "attention": attention_color,
            "hold": attention_color, # todo
        }

        self._color = base_color
        if self._initial_color_def is None:
            self._initial_color_def = color
        self._color_dict = color_dict

    def change_color(self, *a, **k):
        self.set_color(*a, **k)
        self.request_color_update()

    def replace_color(self, color):
        # todo: needs to have the full dict set like in `set_color`
        self._color = color
        self._color_dict['base'] = color
        self.request_color_update()

    def reset_color_to_initial(self):
        if self._initial_color_def is None:
            return
        self.set_color(self._initial_color_def)

    @only_in_view
    def force_color(self, color):
        self._color = color
        self._control_element.set_light(color)

    @listens('current_modes')
    def modes_changed(self, _):
        self.update_mode_string(_)

    @only_in_view
    def update_mode_string(self, mode_states):
        if not self._concerned_modes:
            self._current_mode_string = ''
            return
        active_concerned_modes = [mode for mode in self._concerned_modes if mode_states.get(mode, False)]
        if not active_concerned_modes:
            self._current_mode_string = ""
            if (not self._suppress_animations) and (self._suppress_attention_animations is False):
                self._color = self._color_dict['base']
                self.request_color_update()
        else:
            self._current_mode_string = "__" + "__".join(active_concerned_modes)
            if (not self._suppress_animations) and (self._suppress_attention_animations is False):
                self._color = self._color_dict['attention']
                self.request_color_update()

    @only_in_view
    def animate_success(self, duration=0.4):
        if self._suppress_animations:
            return
        self._is_animating = True
        timer = AnimationTimer(self, duration)
        self._color = self._color_dict['success']
        self.request_color_update()
        self.task_group.add(timer)

    @only_in_view
    def animate_failure(self, duration=0.7):
        if self._suppress_animations:
            return
        self._is_animating = True
        timer = AnimationTimer(self, duration)
        self._color = self._color_dict['failure']
        self.request_color_update()
        self.task_group.add(timer)

    @only_in_view
    def _do_simple_feedback_held(self):
        self.force_color(self._hold_color)

    @only_in_view
    def _do_simple_feedback_release(self):
        self.force_color(self._color_dict['base'])

    def set_prop(self, prop_name, value):
        self._context['me'][prop_name] = value

    def get_prop(self, prop_name):
        return self._context['me'].get(prop_name)

    @staticmethod
    def is_pseq(obj):
        return isinstance(obj, Pseq)

class AnimationTimer(TimerTask):

    def __init__(self, owner, duration, **k):
        super().__init__(duration, **k)
        self.owner: ZControl = owner
        old_task = self.owner._current_animation_task
        if old_task is not None:
            old_task.kill()
            self.owner._current_animation_task = self
        self.restart()

    def on_finish(self):
        self.owner._is_animating = False
        self.owner._color = self.owner._color_dict['base']
        self.owner.request_color_update()
        self.owner.current_animation_task = None
