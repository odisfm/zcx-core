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
        self.__in_view = False
        self.in_view_listener.subject = self.parent_section
        self.__raw_config = raw_config
        self.__control_element: Optional[ZElement] = None
        self.__z_manager = self.root_cs.component_map['ZManager']
        self.__color = None
        self.__color_dict = {}
        self.__context = {}
        self.__gesture_dict = {}
        self.__vars = {}
        self._feedback_type = None
        self.__trigger_action_list = partial(self.root_cs.component_map['CxpBridge'].trigger_action_list)
        self.__resolve_action_def = partial(self.root_cs.component_map['ActionResolver'].compile)

    def setup(self):
        config = self.__raw_config
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
        return self.__in_view

    @property
    def context(self):
        return self.__context

    @property
    def color(self):
        return self.__color

    def set_gesture_dict(self, gesture_dict):
        if type(gesture_dict) is not dict:
            raise ValueError(f'gesture_dict must be a dict: {gesture_dict}')
        self.__gesture_dict = gesture_dict
        self.log('logging gesture dict')
        self.log(self.__gesture_dict)

    def set_vars(self, vars):
        self.__vars = vars

    def __create_context(self, config: list[dict]) -> None:
        context = {k: v for d in config for k, v in d.items()}
        if 'index' not in context:
            if 'group_index' in context:
                context['index'] = context['group_index']
                context['Index'] = context['index'] + 1
            context['index'] = 0
        me_context = {'me': context}
        self.__context = me_context

    def bind_to_state(self, state):
        state.register_z_control(self)
        self.__state = state
        self.__control_element = state._control_element
        self._feedback_type = self.__control_element._feedback_type

    def unbind_from_state(self):
        if self.__state is not None:
            self.__state.unregister_z_control(self)
            self.__control_element = None

    @only_in_view
    def forward_gesture(self, gesture):
        if gesture in self.__gesture_dict:
            action_list = self.__gesture_dict[gesture]
            self.log(action_list)
            parsed = self.__resolve_action_def(
                action_list,
                self.__vars,
                self.__context,
                'live'
            )[0]
            self.log(parsed)
            self.__trigger_action_list(parsed)

    @listens('in_view')
    def in_view_listener(self):
        self.__in_view = self.parent_section.in_view
        self.request_color_update()

    def set_color_to_base(self):
        self.__control_element.set_light(self.__control_element.color_swatch.base)

    @only_in_view
    def request_color_update(self):
        if self.__color is not None:
            self.__control_element.set_light(self.__color)

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

        self.__color = base_color
        self.__color_dict = color_dict
