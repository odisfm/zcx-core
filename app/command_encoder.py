from typing import TYPE_CHECKING, Literal
from math import floor
from ableton.v3.base import EventObject

DEFAULT_COMMAND_ENC_STEPS = 10
NORMALIZE_FACTOR = 2

if TYPE_CHECKING:
    from .z_encoder import ZEncoder
    from .action_resolver import ActionResolver

class CommandEncoder(EventObject):

    def __init__(self, encoder_obj: "ZEncoder", config: dict, mode_string: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._encoder_obj = encoder_obj
        self._raw_config = config
        self._mode_string = mode_string
        self._counter = 0
        if "steps" in self._raw_config:
            steps_def = self._raw_config["steps"]
            if not isinstance(steps_def, int) or steps_def <= 0:
                self.log(f"Invalid `steps` option (`{steps_def}`), using `{DEFAULT_COMMAND_ENC_STEPS}`", level="error")
                self._steps_threshold = DEFAULT_COMMAND_ENC_STEPS
            else:
                self._steps_threshold = steps_def
        else:
            self._steps_threshold = DEFAULT_COMMAND_ENC_STEPS

        self.__label = None
        if "label" in self._raw_config:
            label_def = self._raw_config["label"]
            if isinstance(label_def, str) and "${" in label_def:
                parsed, status = self._encoder_obj.root_cs.component_map["ActionResolver"].compile(label_def, self._encoder_obj._vars, self._encoder_obj._context)
                if not status == 0:
                    self.log(f"Unparseable label `{label_def}`", level="error")
                else:
                    label_def = parsed
            self.__label = label_def

    def log(self, *msgs, level="info"):
        log_func = getattr(self._encoder_obj._logger, level)
        for msg in msgs:
            log_func(f'({self._encoder_obj._name}__{self._mode_string}) {msg}')

    @property
    def label(self):
        return self.__label

    def _receive_value(self, value: int):
        normalized_value = self._normalize_value(value)
        unsigned_normalized_value = abs(normalized_value)
        unsigned_counter = abs(self._counter)
        direction: Literal["up", "down"] = "down" if normalized_value <= 0 else "up"
        if (direction == "up" and self._counter < 0) or (direction == "down" and self._counter > 0):
            self._counter = 0
        commands_to_fire = 0
        if unsigned_normalized_value + unsigned_counter > self._steps_threshold:
            commands_to_fire = floor((unsigned_normalized_value + unsigned_counter) / self._steps_threshold)
            remaining_counter = floor(unsigned_normalized_value + unsigned_counter) % self._steps_threshold
            self._counter = remaining_counter if direction == "up" else remaining_counter * -1
        else:
            value = floor(unsigned_normalized_value + unsigned_counter)
            self._counter = value if direction == "up" else value * -1

        for i in range(commands_to_fire):
            self.fire_command(direction)

    def _normalize_value(self, value: int) -> int:
        if value < 25:
            return value * NORMALIZE_FACTOR
        elif value > 112:
            value = 126 if value == 127 else value
            return (127 - value) * -NORMALIZE_FACTOR
        elif value <= 64:
            inc = 64 - value
            return inc * -NORMALIZE_FACTOR
        elif value > 64:
            inc = 127 - value
            return inc * NORMALIZE_FACTOR
        else:
            return 0

    def fire_command(self, direction: Literal["up", "down"]):
        command_defs = []
        if "both" in self._raw_config:
            command_defs.append(self._raw_config["both"])

        if direction == "up":
            if "up" in self._raw_config:
                command_defs.append(self._raw_config["up"])
        else:
            if "down" in self._raw_config:
                command_defs.append(self._raw_config["down"])

        resolver: "ActionResolver" = self._encoder_obj.root_cs.component_map["ActionResolver"]
        for command_def in command_defs:
            resolver.execute_command_bundle(None, command_def, self._encoder_obj._vars, self._encoder_obj._context)
