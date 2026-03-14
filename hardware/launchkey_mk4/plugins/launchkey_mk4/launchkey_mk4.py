from typing import TYPE_CHECKING, Literal
from math import floor

from ableton.v3.base import EventObject, listens_group, listens
from util import to_percentage

if TYPE_CHECKING:
    from zcx_plugin import ZCXPlugin
    from z_encoder import ZEncoder

SYSEX_HEADER = (0, 32, 41, 2, 20)
SYSEX_HEADER_MINI = (0, 32, 41, 2, 19)
SPECIAL_CHARS = {"□": 27, "■": 28, "♭": 29, "♥": 30}
FADER_NAMES = [
    "fader_1", "fader_2", "fader_3", "fader_4", "fader_5", "fader_6", "fader_7", "fader_8", "fader_9"
]
KNOB_NAMES = [
    "enc_1", "enc_2", "enc_3", "enc_4", "enc_5", "enc_6", "enc_7", "enc_8"
]

SAFE_MESSAGE_CHARS = 12

class LaunchkeyMk4Plugin(ZCXPlugin):

    def __init__(self, name="LaunchkeyMk4Plugin", *a, **k):
        super().__init__(name, *a, **k)
        self._is_mini = False

    def setup(self):
        super().setup()
        self.add_api_method("write_display_message", self.receive_message_from_ua)
        if "mini" in self._user_config:
            mini_def = self._user_config["mini"]
            if not isinstance(mini_def, bool):
                self.error(f'Invalid option for `mini` (`{mini_def}`. Using `false`')
                self._is_mini = False
            else:
                self._is_mini = mini_def
        self._encoder_received_value.replace_subjects(self.canonical_parent.component_map["EncoderManager"]._encoders.values())
        self._on_current_page.subject = self.canonical_parent.component_map["PageManager"]
        self._on_selected_track.subject = self.song.view
        self._on_selected_track()


    def song_ready(self):
        super().song_ready()
        self.enable_zcx_mode()

    def refresh_feedback(self):
        try:
            self.enable_zcx_mode()
            self.write_main_display_message()
        except Exception as e:
            self.critical(f"{e.__class__.__name__}: {e}")

    def enable_zcx_mode(self):
        self.set_encoder_mode(4)
        self.set_pad_mode(1)

    def set_encoder_mode(self, mode: Literal[0, 1, 2, 3, 4, 5, 6, 7]):
        """
        modes: mixer, plugin, sends, transport, custom 1, custom 2, custom 3, custom 4
        """
        self.canonical_parent._do_send_midi((182, 30, mode + 1))

    def set_pad_mode(self, mode: Literal[0, 1, 2, 3, 4, 5, 6, 7]):
        """
        modes: drum, DAW, user chords, custom 1, custom 2, custom 3, custom 4, arp, chord map
        """
        self.canonical_parent._do_send_midi((182, 29, mode + 1))

    def write_display_message(self,
                              line_1: str | int | float | None = None,
                              line_2: str | int | float | None = None,
                              line_3: str | int | float | None = None,
                              temporary=True,
                              encoder_name: str | None = None,
                              ):
        header = SYSEX_HEADER_MINI if self._is_mini else SYSEX_HEADER
        if not encoder_name:
            target = 33 if temporary else 32
        else:
            if encoder_name in KNOB_NAMES:
                target = KNOB_NAMES.index(encoder_name) + 21
            elif encoder_name in FADER_NAMES:
                target = FADER_NAMES.index(encoder_name) + 5
            else:
                raise ValueError(f"Unknown encoder name: {encoder_name}")

        config_msg = (240,) + header + (4, target, 2, 247)

        line_1_msg = (240,) + header + (6, target, 0) + self.string_to_ascii_tuple(line_1) + (247,) if line_1 is not None else None
        line_2_msg = (240,) + header + (6, target, 1) + self.string_to_ascii_tuple(line_2) + (
            247,) if line_2 is not None else None
        line_3_msg = (240,) + header + (6, target, 2) + self.string_to_ascii_tuple(line_3) + (
            247,) if line_3 is not None else None

        trigger_msg = (240,) + header + (4, target, 127, 247)

        self.canonical_parent._do_send_midi(config_msg)
        if line_1_msg:
            self.canonical_parent._do_send_midi(line_1_msg)
        if line_2_msg:
            self.canonical_parent._do_send_midi(line_2_msg)
        if line_3_msg:
            self.canonical_parent._do_send_midi(line_3_msg)
        self.canonical_parent._do_send_midi(trigger_msg)


    def string_to_ascii_tuple(self, message: str):
        chars = []
        message = str(message)
        for c in message:
            if c in SPECIAL_CHARS:
                chars.append(SPECIAL_CHARS[c])
            else:
                chars.append(ord(c))
        return tuple(chars)

    @listens_group("received_value")
    def _encoder_received_value(self, enc: "ZEncoder"):
        try:
            if enc.mapped_parameter:
                param = enc.mapped_parameter
                param_value = param.__str__()
                is_quantized = param.is_quantized
                track_name = None
                if param.name in ["Track Volume", "Track Panning"]:
                    track_name = param.canonical_parent.canonical_parent.name

                value_graphic = ""
                is_bipolar = param.min < 0
                value_pct = to_percentage(param.min, param.max, param.value)
                pct_tens = floor(value_pct / 10)

                if not is_quantized:
                    if not is_bipolar:
                        value_graphic = "■■■■■■■■■■"[:pct_tens] + "□□□□□□□□□□"[:10 - pct_tens]
                    else:
                        if 49 <= value_pct <= 51:
                            value_graphic = "-----□□-----"
                        elif value_pct < 50:
                            blocks = 5 - floor(value_pct / 10)
                            value_graphic = ("■" * blocks).rjust(5, "□") + "-----"
                        else:
                            blocks = min(floor(value_pct / 10) - 4, 5)
                            value_graphic = "-----" + ("■" * blocks).ljust(5, "□")
                else:

                    if param.is_quantized:
                        value_items = list(param.value_items)
                        if value_items == ["Off", "On"]:
                            value_graphic = "□" if param_value == "Off" else "■"
                        else:
                            value_idx = value_items.index(param_value)
                            value_graphic = "□" * value_idx + "■" + "□" * (len(value_items) - value_idx - 1)

                if param_value.endswith("dB"):
                    number_part = param_value.split(" dB")[0]
                    number_round = round(float(number_part), 1)
                    param_value = f"{number_round} dB"

                self.write_display_message(
                    line_1 = track_name or enc.mapped_parameter.name,
                    line_2 = param_value,
                    line_3 = value_graphic,
                    temporary=True,
                    encoder_name= enc._name,
                )
            elif enc._mapped_command:
                if enc._mapped_command.label:
                    label = enc._mapped_command.label
                else:
                    label = "---"
                self.write_display_message(
                    line_1 = "command encoder",
                    line_2 = label,
                    line_3 = "",
                    temporary=True,
                    encoder_name= enc._name,
                )

            else:
                self.write_display_message(
                    line_1= enc._name,
                    line_2= "not bound!",
                    line_3= "---",
                    temporary=True,
                    encoder_name= enc._name,
                )
        except Exception as e:
            self.error(f"{e.__class__.__name__}: {e}")

    def write_main_display_message(self):
        line_1 = self.canonical_parent.component_map["PageManager"].current_page_name
        selected_track = self.song.view.selected_track
        line_2 = selected_track.name
        selected_device = selected_track.view.selected_device
        line_3 = selected_device.name if selected_device else "---"
        self.write_display_message(line_1, line_2, line_3, temporary=True) # needed to overwrite a currently displayed enc message
        self.write_display_message(line_1, line_2, line_3, temporary=False)

    @listens("selected_track")
    def _on_selected_track(self):
        self.write_main_display_message()
        self._on_selected_device.subject = self.song.view.selected_track.view

    @listens("selected_device")
    def _on_selected_device(self):
        self.write_main_display_message()

    @listens("current_page")
    def _on_current_page(self):
        self.write_main_display_message()

    def receive_message_from_ua(self, message: str):
        line_1 = ""
        line_2 = ""
        line_3 = ""

        if len(message) > SAFE_MESSAGE_CHARS:
            words = message.split()
            lines = []
            current = ""

            for word in words:
                if len(current) + len(word) + (1 if current else 0) > SAFE_MESSAGE_CHARS:
                    lines.append(current)
                    current = word
                else:
                    current += (" " if current else "") + word
            if current:
                lines.append(current)

            if len(lines) >= 3:
                line_1 = lines[0]
                line_2 = lines[1]
                remainder = " ".join(lines[2:])
                if len(remainder) > SAFE_MESSAGE_CHARS:
                    remainder = remainder[:SAFE_MESSAGE_CHARS - 2] + ".."
                line_3 = remainder
            elif len(lines) == 2:
                line_2 = lines[0]
                line_3 = lines[1]
            else:
                line_2 = lines[0]
        else:
            line_2 = message

        self.write_display_message(line_1=line_1, line_2=line_2, line_3=line_3, temporary=True)


