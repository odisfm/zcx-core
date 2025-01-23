from functools import wraps, partial

from ableton.v2.base import EventObject
from ableton.v3.base import listens
from ableton.v3.control_surface import ControlSurface
from .colors import parse_color_definition, simplify_color, Pulse, Blink, RgbColor
from .defaults import BUILT_IN_COLORS
from .z_element import ZElement
from .template_manager import TemplateManager
from .errors import ConfigurationError
from .cxp_bridge import CxpBridge


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
    ):
        super().__init__()
        self.root_cs = root_cs
        self.parent_section = parent_section
        self.__state = None
        self.__parent_logger = self.parent_section._logger
        self._in_view = False
        self.in_view_listener.subject = self.parent_section
        self._raw_config = raw_config
        self._control_element: Optional[ZElement] = None
        self.__z_manager = self.root_cs.component_map['ZManager']
        self._color = None
        self._color_dict = {}
        self._context = {}
        self._gesture_dict = {}
        self._vars = {}
        self._feedback_type = None
        self._trigger_action_list = partial(self.root_cs.component_map['CxpBridge'].trigger_action_list)
        self._resolve_command_bundle = partial(
            self.root_cs.component_map['ActionResolver'].execute_command_bundle,
            calling_control=self,  # calling_control
        )

    def setup(self):
        config = self._raw_config
        color = config.get('color', 127)
        self.set_color(color)
        self.__create_context([
            config.get('section_context', {}),
            config.get('group_context', {}),
        ])
        self.set_gesture_dict(config.get('gestures', {}))
        self.set_vars(config.get('vars', {}))

    def log(self, *msg):
        for msg in msg:
            self.__parent_logger.info(f'({self.parent_section.name}) {msg}')

    @property
    def in_view(self):
        return self._in_view

    @property
    def context(self):
        return self._context

    @property
    def color(self):
        return self._color

    def set_gesture_dict(self, gesture_dict):
        if type(gesture_dict) is not dict:
            raise ValueError(f'gesture_dict must be a dict: {gesture_dict}')
        self._gesture_dict = gesture_dict

    def set_vars(self, vars):
        self._vars = vars

    def __create_context(self, config: list[dict]) -> None:
        context = {k: v for d in config for k, v in d.items()}
        if 'index' not in context:
            if 'group_index' in context:
                context['index'] = context['group_index']
            else:
                context['index'] = 0
        context['Index'] = context['index'] + 1
        me_context = {'me': context}
        self._context = me_context

    def bind_to_state(self, state):
        state.register_z_control(self)
        self.__state = state
        self._control_element = state._control_element
        self._feedback_type = self._control_element._feedback_type

    def unbind_from_state(self):
        if self.__state is not None:
            self.__state.unregister_z_control(self)
            self._control_element = None

    @only_in_view
    def handle_gesture(self, gesture):
        if gesture in self._gesture_dict:
            command_bundle = self._gesture_dict[gesture]
            self._resolve_command_bundle(
                bundle=command_bundle,
                vars_dict=self._vars,
                context=self._context
            )

    @listens('in_view')
    def in_view_listener(self):
        self._in_view = self.parent_section.in_view
        self.request_color_update()

    def set_color_to_base(self):
        self._control_element.set_light(self._control_element.color_swatch.base)

    @only_in_view
    def request_color_update(self):
        if self._color is not None:
            self._control_element.set_light(self._color)

    def set_color(self, color):
        try:
            base_color = parse_color_definition(color)
        except Exception as e:
            self.log(e)
            base_color = parse_color_definition(127)

        simplified_color = simplify_color(base_color)
        white = parse_color_definition('white')
        green = parse_color_definition('green')
        red = parse_color_definition('red')
        off = parse_color_definition('0')

        if self._feedback_type == 'rgb':
            attention_color = Pulse(simplified_color, white, 48)
            animate_success = Blink(simplified_color, white, 12)
            animate_failure = Blink(simplified_color, red, 48)
        elif self._feedback_type == 'basic':
            attention_color = base_color
            animate_success = Blink(simplified_color, off, 48)
            animate_failure = Blink(simplified_color, off, 12)
        elif self._feedback_type == 'biled':
            attention_color = base_color
            animate_success = Blink(simplified_color, green, 48)
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
        self._color_dict = color_dict

    @only_in_view
    def force_color(self, color):
        self.log(f'forcing light change')
        self._color = color
        self._control_element.set_light(color)
        self._control_element.send_value(127)
        self.log(f'finished')
