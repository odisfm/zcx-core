import time
from typing import TYPE_CHECKING

from ableton.v3.base import listens_group, listens
from ableton.v2.base.task import TimerTask

if TYPE_CHECKING:
    from z_control import ZControl
    from z_encoder import ZEncoder
    from zcx_plugin import ZCXPlugin

MIDI_CC_STATUS = 176

KNOB_IDS = { # these are the IDs to change the LED type. they are different to the actual IDs used to send/receive data
    "track_1": 56,
    "track_2": 57,
    "track_3": 58,
    "track_4": 59,
    "track_5": 60,
    "track_6": 61,
    "track_7": 62,
    "track_8": 63,
    "device_1": 24,
    "device_2": 25,
    "device_3": 26,
    "device_4": 27,
    "device_5": 28,
    "device_6": 29,
    "device_7": 30,
    "device_8": 31,
}

MODE_BUTTON_NAMES = ["pan", "sends", "user", "shift", "bank_lock"]


class Apc40Mk2Plugin(ZCXPlugin):

    def __init__(self, name="Apc40Mk2Plugin", *a, **k):
        super().__init__(name, *a, **k)
        self._mode_controls: "list[ZControl]" = []
        self._encoders: "list[ZEncoder]" = []
        self._prefer_full_led = False
        self._knob_style_overrides = {}

    def setup(self):
        super().setup()
        z_manager = self.canonical_parent.component_map["ZManager"]
        all_controls = z_manager.all_controls
        for control in all_controls:
            for name in MODE_BUTTON_NAMES:
                if control.name.startswith(name): # overlay controls are different objects: we need to listen to them too
                    self._mode_controls.append(control)
                    break

        self.on_mode_buttons_gesture_received.replace_subjects(self._mode_controls)
        self.on_encoder_param_changed.replace_subjects(self._encoders)

        encoder_manager = self.canonical_parent.component_map["EncoderManager"]
        for enc_name in KNOB_IDS.keys():
            self._encoders.append(encoder_manager.get_encoder(enc_name))

        config = self._user_config
        if "prefer_full_led" in config:
            prefer_full_led = config["prefer_full_led"]
            if not isinstance(prefer_full_led, bool):
                self.error(f"Invalid value for `prefer_full_led`: `{prefer_full_led}`")
            else:
                self._prefer_full_led = prefer_full_led

        if "force_style" in config:
            force_style_def = config["force_style"]
            if not isinstance(force_style_def, dict):
                self.error(f"Invalid value for `force_style`. Must be of type dict: `{force_style_def}`")
            else:
                for key, value in force_style_def.items():
                    if value not in ["off", "single", "volume", "pan"]:
                        self.error(f"Invalid value for `force_style` (`{key}`): `{value}`")
                        del force_style_def[key]
                self._knob_style_overrides = force_style_def
                self.debug("knob style overrides", self._knob_style_overrides)

    def song_ready(self):
        self.update_all_encoders()

    def update_encoder(self, encoder: "ZEncoder"):
        self.debug(f"updating encoder {encoder._name}. mapped_param is {encoder.mapped_parameter.name if encoder.mapped_parameter else None}, mapped_dev is {encoder.mapped_parameter.canonical_parent if encoder.mapped_parameter else None}")
        mapped_param = encoder.mapped_parameter
        if encoder._name in self._knob_style_overrides:
            led_type = self._knob_style_overrides[encoder._name]
        elif mapped_param is None:
            led_type = "off"
        elif self.is_bipolar(mapped_param):
            led_type = "pan"
        elif "volume" in mapped_param.name.lower() or self._prefer_full_led:
            led_type = "volume"
        else:
            led_type = "single"

        midi_message: tuple = self.create_led_type_message(encoder._name, led_type)

        self.debug(f"midi_message: {midi_message}")

        self.canonical_parent._do_send_midi(tuple(midi_message))
        encoder.refresh_feedback()

    def update_all_encoders(self):
        for encoder in self._encoders:
            self.update_encoder(encoder)

    @listens_group("gesture_received")
    def on_mode_buttons_gesture_received(self, gesture, control):
        if gesture == "pressed":
            timer_task = RefreshAllTask(owner=self)
            self.canonical_parent._task_group.add(timer_task)
            timer_task.restart()

    @listens_group("mapped_parameter")
    def on_encoder_param_changed(self, mapped_parameter, encoder):
        self.update_encoder(encoder)

    def create_led_type_message(self, encoder_name, led_type):
        match led_type:
            case "off":
                data_byte = 0
            case "single":
                data_byte = 1
            case "volume":
                data_byte = 2
            case "pan":
                data_byte = 3
            case _:
                raise ValueError(f"Invalid LED type: {led_type}")

        return MIDI_CC_STATUS, KNOB_IDS[encoder_name], data_byte

    def is_bipolar(self, parameter):
        return parameter.min < 0


class RefreshAllTask(TimerTask):
    def __init__(self, owner: Apc40Mk2Plugin, duration=0.2,  *a, **k):
        super().__init__(*a, **k)
        self.duration = duration
        self._owner = owner

    def on_finish(self):
        self._owner.debug("timer task finished, updating encoders")
        self._owner.update_all_encoders()
