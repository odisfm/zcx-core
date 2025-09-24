from enum import Enum
from unittest import case

from ableton.v3.base import listens
from ..z_control import ZControl
from ..errors import CriticalConfigurationError, ConfigurationError
from ..consts import NOTE_NAMES, NOTE_NAMES_FLAT, SCALE_NAMES, REPEAT_RATES
from ..colors import parse_color_definition

note_names_lower = [name.lower() for name in NOTE_NAMES]
note_names_flat_lower = [name.lower() for name in NOTE_NAMES_FLAT]
scale_names_lower = [scale_name.lower() for scale_name in SCALE_NAMES]
repeat_rates_lower = [rate.lower() for rate in REPEAT_RATES]

def get_index_from_note_name(note_name):
    note_name = note_name.lower()
    if note_name in note_names_lower:
        return note_names_lower.index(note_name)
    elif note_name in note_names_flat_lower:
        return note_names_flat_lower.index(note_name)
    else:
        return None

def validate_scale_name(scale_name):
    if scale_name in scale_names_lower:
        return SCALE_NAMES[scale_names_lower.index(scale_name)]
    else:
        return None

class KeyboardFunction(Enum):
    IN_KEY = 0
    OCTAVE_DOWN = 1
    OCTAVE_UP = 2
    FULL_VELO = 3
    REPEAT_RATE = 4
    NOTE_LAYOUT = 5
    SCALE_TONIC = 6
    SCALE_NAME = 7
    SCALE_NAME_AND_TONIC = 8


class KeyboardControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self.__melodic_component = self.root_cs.component_map["MelodicComponent"]
        self.__keyboard_function: KeyboardFunction = None
        self.__scale_name: str = None
        self.__scale_root: int = None
        self.__repeat_rate: int = None
        self.action_resolver = self.root_cs.component_map["ActionResolver"]

    def setup(self):
        super().setup()
        self._color = parse_color_definition(0, self)
        self._simple_feedback = False
        self._suppress_animations = True
        self.request_color_update()

    def finish_setup(self):
        raw_config = self._raw_config
        item_def = raw_config.get("function")

        active_color_def = raw_config.get("active_color") or raw_config.get("color") or 127
        inactive_color_def = raw_config.get("inactive_color") or 1
        active_color = parse_color_definition(active_color_def, self)
        if not active_color:
            raise ConfigurationError(f"Invalid color definition: {active_color_def}")
        self._color_dict["active"] = active_color
        inactive_color = parse_color_definition(inactive_color_def, self)
        if not inactive_color:
            raise ConfigurationError(f"Invalid color definition: {inactive_color_def}")
        self._color_dict["inactive"] = self._color_dict["base"] = inactive_color

        if item_def is None:
            raise CriticalConfigurationError(f"Missing required option `function`: {raw_config}")
        if isinstance(item_def, dict):
            fn_def = list(item_def.keys())[0]
            match fn_def.lower():
                case "layout":
                    raise NotImplementedError()
                case "repeat_rate":
                    self.__keyboard_function = KeyboardFunction.REPEAT_RATE
                    rate_def = list(item_def.values())[0]
                    if not isinstance(rate_def, str):
                        raise ConfigurationError(f"Invalid repeat rate `{rate_def}`")
                    if "${" in rate_def:
                        parsed, status = self.action_resolver.compile(rate_def, self._vars, self._context)
                        if status != 0:
                            raise ConfigurationError(f"Unparseable repeat rate `{rate_def}`")
                        rate_def = parsed
                    if not rate_def.lower() in repeat_rates_lower:
                        raise ConfigurationError(f"Invalid repeat rate `{rate_def}`")
                    self.__repeat_rate = repeat_rates_lower.index(rate_def.lower())
                case "scale":
                    if isinstance(item_def["scale"], dict):
                        scale_def = item_def["scale"]
                        if "root" in scale_def and "name" in scale_def:
                            self.__keyboard_function = KeyboardFunction.SCALE_NAME_AND_TONIC
                        elif "name" in scale_def:
                            self.__keyboard_function = KeyboardFunction.SCALE_NAME
                        elif "root" in scale_def:
                            self.__keyboard_function = KeyboardFunction.SCALE_TONIC
                        else:
                            raise ConfigurationError(f"Invalid scale definition `{scale_def}`. Must be dict with keys root and/or name")

                        root_def = scale_def.get("root")
                        if root_def is not None:
                            if isinstance(root_def, int):
                                if 0 <= root_def < len(NOTE_NAMES):
                                    self.__scale_root = root_def
                                else:
                                    idx = root_def % len(NOTE_NAMES)
                                    self.warning(f"Wrapped root def {root_def} to {idx} ({NOTE_NAMES[idx]})")
                                    self.__scale_root = idx
                            elif isinstance(root_def, str):
                                if "${" in root_def:
                                    parsed, status = self.action_resolver.compile(root_def, self._vars, self._context)
                                    if status != 0:
                                        raise ConfigurationError(f"Unparseable root def: `{root_def}`")
                                    root_def = parsed
                                idx = get_index_from_note_name(root_def)
                                if idx is None:
                                    raise ConfigurationError(f"Invalid root def: `{root_def}`")
                                self.__scale_root = idx

                        name_def = scale_def.get("name")
                        if name_def is not None:
                            if not isinstance(name_def, str):
                                raise ConfigurationError(f"Invalid scale name `{name_def}`. Must be in: {scale_names_lower}")
                            if "${" in name_def:
                                parsed, status = self.action_resolver.compile(name_def, self._vars, self._context)
                                if status != 0:
                                    raise ConfigurationError(f"Unparseable name def: `{name_def}`")
                                name_def = parsed
                            valid = validate_scale_name(name_def)
                            if not valid:
                                raise ConfigurationError(f"Invalid scale name `{name_def}`. Must be in: {scale_names_lower}")
                            self.__scale_name = name_def
                    else:
                        raise ConfigurationError(f"Invalid scale definition `{item_def}`. Must be dict with keys root and/or name")
        elif isinstance(item_def, str):
            if "${" in item_def:
                parsed, status = self.action_resolver.compile(item_def, self._vars, self._context)
                if status != 0:
                    raise CriticalConfigurationError(f"Unparseable `{item_def}`")
                item_def = parsed

            match item_def.lower():
                case "in_key":
                    self.__keyboard_function = KeyboardFunction.IN_KEY
                case "octave_down":
                    self.__keyboard_function = KeyboardFunction.OCTAVE_DOWN
                case "octave_up":
                    self.__keyboard_function = KeyboardFunction.OCTAVE_UP
                case "full_velo":
                    self.__keyboard_function = KeyboardFunction.FULL_VELO

        else:
            raise CriticalConfigurationError(f"Invalid datatype for option `function`. Must be `dict` or `str`.\n{raw_config}")

        melodic_inst = self.root_cs.component_map["MelodicComponent"]

        match self.__keyboard_function:
            case KeyboardFunction.SCALE_TONIC:
                self._listener_root_note.subject = self.root_cs.song
            case KeyboardFunction.SCALE_NAME:
                self._listener_scale_name.subject = self.root_cs.song
            case KeyboardFunction.SCALE_NAME_AND_TONIC:
                self._listener_root_note.subject = self.root_cs.song
                self._listener_scale_name.subject = self.root_cs.song
            case KeyboardFunction.FULL_VELO:
                self._listener_full_velo.subject = melodic_inst
            case KeyboardFunction.REPEAT_RATE:
                self._listener_repeat_rate.subject = melodic_inst
            case KeyboardFunction.OCTAVE_DOWN:
                self._listener_octave.subject = melodic_inst
            case KeyboardFunction.OCTAVE_UP:
                self._listener_octave.subject = melodic_inst
            case KeyboardFunction.NOTE_LAYOUT:
                self._listener_note_layout.subject = melodic_inst
            case KeyboardFunction.IN_KEY:
                self._listener_chromatic.subject = melodic_inst

        self.update_feedback()
        self.request_color_update()
        self.log("finished kb control setup")

    def _back_in_view(self):
        super()._back_in_view()
        self.update_feedback()
        self.log(f"my repeat rate: {self.__repeat_rate}")

    @listens("chromatic")
    def _listener_chromatic(self, _):
        self.update_feedback()

    @listens("octave")
    def _listener_octave(self, _):
        self.update_feedback()

    @listens("full_velo")
    def _listener_full_velo(self, _):
        self.update_feedback()

    @listens("repeat")
    def _listener_repeat_rate(self, _):
        self.update_feedback()

    @listens("repeat_rate")
    def _listener_repeat_rate(self, _):
        self.update_feedback()

    @listens("note_layout")
    def _listener_note_layout(self, _):
        self.update_feedback()

    @listens("root_note")
    def _listener_root_note(self):
        self.update_feedback()

    @listens("scale_name")
    def _listener_scale_name(self):
        self.update_feedback()

    def set_feedback(self, feedback=True):
        if feedback:
            color = self._color_dict["active"]
        else:
            color = self._color_dict["inactive"]
        self.replace_color(color)

    def update_feedback(self):
        match self.__keyboard_function:
            case KeyboardFunction.SCALE_TONIC:
                self.set_feedback(self.__scale_root == self.root_cs.song.root_note)
            case KeyboardFunction.SCALE_NAME:
                self.set_feedback(self.__scale_name == self.root_cs.song.scale_name)
            case KeyboardFunction.SCALE_NAME_AND_TONIC:
                self.set_feedback(
                    self.__scale_root == self.root_cs.song.root_note
                    and
                    self.__scale_name == self.root_cs.song.scale_name
                )
            case KeyboardFunction.FULL_VELO:
                self.set_feedback(self.__melodic_component.full_velo)
            case KeyboardFunction.REPEAT_RATE:
                self.set_feedback(self.__melodic_component.repeat_rate == self.__repeat_rate)
            case KeyboardFunction.OCTAVE_DOWN:
                self.set_feedback(self.__melodic_component.octave > 0)
            case KeyboardFunction.OCTAVE_UP:
                self.set_feedback(self.__melodic_component.octave < 9)
            case KeyboardFunction.NOTE_LAYOUT:
                raise NotImplementedError()
            case KeyboardFunction.IN_KEY:
                self.set_feedback(not self.__melodic_component.chromatic)

        self.request_color_update()
