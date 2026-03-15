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

ARP_TYPES = ["up", "down", "up_down", "up_down_2", "as_played", "random", "chord", "strum"]
ARP_RATES = ["1/4", "1/4t", "1/8", "1/8t", "1/16", "1/16t", "1/32", "1/32t"]
SCALE_BEHAVIORS = ["snap", "filter", "easy"]
TONES =      ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
TONES_FLAT = ["C", "DB", "D", "EB", "E", "F", "GB", "G", "AB", "A", "BB", "B"]
SCALE_NAMES = ["major", "minor", "dorian", "mixolydian", "lydian", "phrygian", "locrian",
               "whole tone", "half-whole dim.", "whole-half dim.", "minor blues", "minor pentatonic",
               "major pentatonic", "harmonic minor", "harmonic major", "dorian #4", "phrygian dominant",
               "melodic minor", "lydian augmented", "lydian dominant", "super locrian", "8-tone spanish",
               "bhairav", "hungarian minor", "hirajoshi", "in-sen", "iwato", "kumoi", "pelog selisir",
               "pelog tembung", ]

PAD_LAYOUTS = {"drum": 1, "daw": 2, "zcx": 2, "chords": 4, "cm1": 5, "cm2": 6, "cm3": 7, "cm4": 8, "arp": 13, "chord_map": 14}
ENCODER_LAYOUTS = {"mixer": 1, "plugin": 2, "sends": 4, "transport": 5, "zcx": 5, "cm1": 6, "cm2": 7, "cm3": 8, "cm4": 9}
FADER_LAYOUTS = {"volume": 1, "zcx": 1, "cm1": 6, "cm2": 7, "cm3": 8, "cm4": 9}

SAFE_MESSAGE_CHARS = 12


class LaunchkeyMk4Plugin(ZCXPlugin):

    def __init__(self, name="LaunchkeyMk4Plugin", *a, **k):
        super().__init__(name, *a, **k)
        self._is_mini = False
        self._follow_live_key = False

    def setup(self):
        super().setup()
        self.add_api_method("write_display_message", self.receive_message_from_ua)
        if not isinstance(self._user_config, dict):
            self._user_config = {}
        if "mini" in self._user_config:
            mini_def = self._user_config["mini"]
            if not isinstance(mini_def, bool):
                self.error(f'Invalid option for `mini` (`{mini_def}`. Using `false`')
                self._is_mini = False
            else:
                self._is_mini = mini_def
        if "follow_key" in self._user_config:
            follow_key_def = self._user_config["follow_key"]
            if not isinstance(follow_key_def, bool):
                self.error(f"Invalid value for option `follow_key` (`{follow_key_def}`. Using `{self._follow_live_key}`")
            else:
                self._follow_live_key = follow_key_def
        if self._follow_live_key:
            self._on_live_root_note.subject = self.song
            self._on_live_scale_name.subject = self.song
            self._on_live_root_note()
            self._on_live_scale_name()
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

    def set_feature(self, cc_num: int, value: int):
        self.canonical_parent._do_send_midi((182, cc_num, value))

    def launchkey_user_action(self, action_def, args):
        args = args.split("lk ")[1]
        _args = args.split()

        try:
            command = _args.pop(0)
            subcommand = _args.pop(0)
        except IndexError:
            raise ValueError(f"Invalid launchkey command: {args}")

        match command:
            case "layout":
                layout_def = _args.pop(0)
                match subcommand:
                    case "pad":
                        try:
                            layout_idx = PAD_LAYOUTS[layout_def]
                        except KeyError:
                            raise ValueError(f"Invalid pad layout `{layout_def}`. Must be one of {list(PAD_LAYOUTS.keys())}")
                        self.set_feature(29, layout_idx)
                    case "enc":
                        try:
                            layout_idx = ENCODER_LAYOUTS[layout_def]
                        except KeyError:
                            raise ValueError(f"Invalid enc layout `{layout_def}`. Must be one of {list(ENCODER_LAYOUTS.keys())}")
                        self.set_feature(30, layout_idx)
                    case "fader":
                        try:
                            layout_idx = FADER_LAYOUTS[layout_def]
                        except KeyError:
                            raise ValueError(f"Invalid fader layout `{layout_def}`. Must be one of {list(FADER_LAYOUTS.keys())}")
                        self.set_feature(31, layout_idx)
                    case _:
                        raise ValueError(f"Invalid launchkey command: {args}")

            case "midich":
                if subcommand not in ["a", "b", "chord", "drum"]:
                    raise ValueError(f"Invalid midich subcommand: {subcommand}. Must be one of `a`, `b`, `chord`, `drum`")
                try:
                    midi_channel = int(_args.pop(0)) - 1
                    if not 0 <= midi_channel < 16:
                        raise ValueError()
                except IndexError:
                    raise ValueError(f"Invalid midich command: {args}")
                except ValueError:
                    raise ValueError(f"Invalid midich command: {args}. Channel must be between 1 and 16")
                match subcommand:
                    case "a":
                        cc_num = 100
                    case "b":
                        cc_num = 101
                    case "chord":
                        cc_num = 102
                    case "drum":
                        cc_num = 103
                self.set_feature(cc_num, midi_channel)

            case "zone":
                match subcommand:
                    case "a":
                        zone_idx = 0
                    case "b":
                        zone_idx = 1
                    case "split":
                        zone_idx = 2
                    case "layer":
                        zone_idx = 3
                    case _:
                        raise ValueError(f"Invalid zone: {subcommand}. Must be one of `a`, `b`, `split`, `layer`")
                self.set_feature(77, zone_idx)
            case "split":
                try:
                    split_note = int(subcommand)
                    if not 0 <= split_note <= 127:
                        raise ValueError()
                except ValueError:
                    raise ValueError(f"Invalid split note: {args}. Must be between 0 and 127")
                self.set_feature(78, split_note)
            case "arp":
                match subcommand:
                    case "on":
                        self.set_feature(73, 127)
                    case "off":
                        self.set_feature(73, 0)
                    case "type":
                        arp_type = _args.pop(0)
                        try:
                            arp_type = int(arp_type)
                            if 0 < arp_type <= len(ARP_TYPES):
                                arp_type -= 1
                            else:
                                raise RuntimeError(f"Invalid arp type: {arp_type}. Must be between 1 and {len(ARP_TYPES)}")
                        except ValueError:
                            if arp_type not in ARP_TYPES:
                                raise ValueError(f"Invalid arp type: {arp_type}. Valid arp types are: {ARP_TYPES}")
                            arp_type = ARP_TYPES.index(arp_type)

                        self.set_feature(85, arp_type)

                    case "rate":
                        arp_rate = _args.pop(0)
                        try:
                            arp_rate = int(arp_rate)
                            if 0 < arp_rate <= len(ARP_RATES):
                                arp_rate -= 1
                            else:
                                raise RuntimeError(f"Invalid arp type: {arp_rate}. Must be between 1 and {len(ARP_TYPES)}")
                        except ValueError:
                            if arp_rate not in ARP_RATES:
                                raise ValueError(f"Invalid arp type: {arp_rate}. Valid arp types are: {ARP_RATES}")
                            arp_rate = ARP_RATES.index(arp_rate)

                        self.set_feature(86, arp_rate)
                    case "octave":
                        arp_octave = _args.pop(0)
                        try:
                            arp_octave = int(arp_octave)
                            if not 0 < arp_octave <= 4:
                                raise ValueError()
                        except ValueError:
                            raise ValueError(f"Invalid arp octave: {arp_octave}. Must be between 1 and 4")
                        self.set_feature(87, arp_octave)
                    case "latch":
                        arp_latch = _args.pop(0)
                        if arp_latch == "on":
                            self.set_feature(88, 127)
                        elif arp_latch == "off":
                            self.set_feature(88, 0)
                        else:
                            raise ValueError(f"Invalid arp latch: {arp_latch}. Must be `on` or `off`")
                    case "gate":
                        arp_gate = _args.pop(0)
                        try:
                            arp_gate = int(arp_gate)
                            if arp_gate < 0:
                                self.warning(f"Invalid arp gate: {arp_gate}. Must be between 0 and 95")
                                arp_gate = 0
                            elif arp_gate > 95:
                                self.warning(f"Invalid arp gate: {arp_gate}. Must be between 0 and 95")
                                arp_gate = 95
                        except ValueError:
                            raise ValueError(f"Invalid arp gate: {arp_gate}. Must be between 0 and 95")
                        self.set_feature(89, arp_gate)
                    case "mutate":
                        arp_mutate = _args.pop(0)
                        try:
                            arp_mutate = int(arp_mutate)
                        except ValueError:
                            raise ValueError(f"Invalid arp mutate: {arp_mutate}. Must be between 0 and 127")
                        self.set_feature(92, max(0, min(arp_mutate, 127)))

                    case "vel":
                        arp_vel = _args.pop(0)
                        if arp_vel == "full":
                            self.set_feature(93, 0)
                        elif arp_vel == "note":
                            self.set_feature(93, 127)
                        else:
                            raise ValueError(f"Invalid arp vel: {arp_vel}. Must be `full` or `note`")

                    case _:
                        raise ValueError(f"Unknown subcommand 'ARP {str(subcommand).upper()}'")
            case "scale":
                match subcommand:
                    case "on":
                        self.set_feature(74, 127)
                    case "off":
                        self.set_feature(74, 0)
                    case "bhv":
                        scale_behavior = _args.pop(0)
                        if not scale_behavior in SCALE_BEHAVIORS:
                            raise ValueError(f"Invalid scale behavior, must be one of: {SCALE_BEHAVIORS}")
                        scale_behavior = SCALE_BEHAVIORS.index(scale_behavior)
                        self.set_feature(60, scale_behavior)
                    case "root":
                        scale_root = _args.pop(0)
                        try:
                            scale_root = int(scale_root)
                        except ValueError:
                            ...
                        if isinstance(scale_root, int):
                            if not 0 < scale_root <= 127:
                                raise ValueError(f"Invalid root scale: {scale_root}. Must be between 0 and 127")
                            scale_idx = scale_root
                        else:
                            if scale_root == "match":
                                scale_idx = self.song.root_note
                            else:
                                root_upper = scale_root.upper()
                                if root_upper in TONES:
                                    scale_idx = TONES.index(root_upper)
                                elif root_upper in TONES_FLAT:
                                    scale_idx = TONES_FLAT.index(root_upper)
                                else:
                                    raise ValueError(f"Invalid scale root: {scale_root}. Must be in: {TONES} (or flat equivalent)")

                        self.set_feature(61, scale_idx)


                    case "name":
                        scale_name = " ".join(_args)
                        scale_idx = None
                        try:
                            scale_idx = int(scale_name)
                        except ValueError:
                            ...
                        if scale_idx is not None:
                            if not 0 < scale_idx < len(SCALE_NAMES):
                                raise ValueError(f"Invalid scale name: {scale_name}. Must be between 1 and {len(SCALE_NAMES)-1}")
                        else:
                            if scale_name == "match":
                                live_scale_name = str(self.song.scale_name).lower()
                                if live_scale_name not in SCALE_NAMES:
                                    raise ValueError(f"Live scale `{live_scale_name}` is not available on Launchkey.")
                                scale_idx = SCALE_NAMES.index(live_scale_name) + 1
                            else:
                                if scale_name not in SCALE_NAMES:
                                    raise ValueError(f"Invalid scale name: {scale_name}. Must be one of {SCALE_NAMES}")
                                scale_idx = SCALE_NAMES.index(scale_name) + 1

                        self.set_feature(62, scale_idx)

                    case _:
                        raise ValueError(f"Unknown subcommand '{str(subcommand).upper()}'")

            case "chord":
                match subcommand:
                    case "adv": # adventure
                        try:
                            adv_idx = int(_args.pop(0))
                            if not 0 < adv_idx <= 5:
                                raise ValueError()
                        except ValueError:
                            raise ValueError(f"Invalid chord adv index: {args}. Must be between 1 and 5")
                        except IndexError:
                            raise ValueError(f"Missing chord adv index: {args}. Must be between 1 and 5")
                        self.set_feature(122, adv_idx)

                    case "explore":
                        try:
                            explore_idx = int(_args.pop(0))
                            if not 0 < explore_idx <= 8:
                                raise ValueError()
                        except ValueError:
                            raise ValueError(f"Invalid chord explore index: {args}. Must be between 1 and 8")
                        except IndexError:
                            raise ValueError(f"Missing chord explore index: {args}. Must be between 1 and 8")

                        self.set_feature(123, explore_idx)

                    case "spread":
                        try:
                            spread_idx = int(_args.pop(0))
                            if not 0 < spread_idx <= 3:
                                raise ValueError()
                        except ValueError:
                            raise ValueError(f"Invalid chord spread index: {args}. Must be between 1 and 3")
                        except IndexError:
                            raise ValueError(f"Missing chord spread index: {args}. Must be between 1 and 3")

                        self.set_feature(124, spread_idx - 1)

                    case "roll":
                        try:
                            roll_idx = int(_args.pop(0))
                            if not 0 <= roll_idx <= 100:
                                raise ValueError()
                        except ValueError:
                            raise ValueError(f"Invalid chord roll index: {args}. Must be between 0 and 100")
                        except IndexError:
                            raise ValueError(f"Missing chord roll index: {args}. Must be between 0 and 100")

                        self.set_feature(125, roll_idx)

                    case _:
                        raise ValueError(f"Unknown subcommand '{str(subcommand).upper()}'")

            case "shift":
                if subcommand == "on":
                    self.set_feature(63, 127)
                elif subcommand == "off":
                    self.set_feature(63, 0)
                else:
                    raise ValueError(f"Unknown subcommand '{str(subcommand).upper()}'")


    @listens("root_note")
    def _on_live_root_note(self):
        self.launchkey_user_action({}, "lk scale root match")

    @listens("scale_name")
    def _on_live_scale_name(self):
        self.launchkey_user_action({}, "lk scale name match")
