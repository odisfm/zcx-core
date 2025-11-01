import time
from typing import TYPE_CHECKING, Optional
from collections import Counter

from ableton.v3.base import EventObject
from ableton.v3.base import listens_group, listens
from Push.sysex import *
from ableton.v2.base.task import TimerTask
from util import to_percentage

LIVE_MODE = (240, 71, 127, 21, 98, 0, 1, 0, 247)
USER_MODE = (240, 71, 127, 21, 98, 0, 1, 1, 247)

if TYPE_CHECKING:
    from app.zcx_core import ZCXCore
    from app.zcx_plugin import ZCXPlugin
    from app.z_encoder import ZEncoder
    from app.encoder_manager import EncoderManager
    from app.session_ring import SessionRing

ENC_PREFIX = "enc_"

SEGMENT_INDICES = [
    (0, 8),
    (9, 17),
    (17, 26),
    (26, 34),
    (34, 42),
    (43, 51),
    (51, 59),
    (60, 68),
]

DEFAULT_CONFIG = {
    "encoder_mapping": 1,
    "encoder_values": 2,
    "message": 3,
    "ring_tracks": 4,
}

PREFER_TRACK_NAME_FOR_VOLUME = True
USE_GRAPHICS = True


class Push1Display(ZCXPlugin):

    def __init__(self, name="Push1Display", *a, **k):
        super().__init__(name, *a, **k)
        self.__suppress_send = True
        self.__send_midi = self.canonical_parent._do_send_midi
        self.__push_main_encoders: "Optional[list[ZEncoder]]" = [None] * 8
        self.__encoder_manager: "EncoderManager" = None
        self.__encoder_watchers: "list[EncoderWatcher]" = []
        self.__session_ring: "SessionRing" = None

        # Use bytearray for efficient in-place modifications
        self._line_bytes_cache = [
            bytearray(WRITE_LINE1 + (32,) * 68 + (247,)),
            bytearray(WRITE_LINE2 + (32,) * 68 + (247,)),
            bytearray(WRITE_LINE3 + (32,) * 68 + (247,)),
            bytearray(WRITE_LINE4 + (32,) * 68 + (247,)),
        ]

        # Batching system - one timer per line
        self._dirty_lines = [False, False, False, False]
        self._line_timers = [None, None, None, None]

        self._encoder_mapping_line = False
        self._encoder_values_line = False
        self._message_line = False
        self._ring_tracks_line = False
        self._selected_line = False

        self._persistent_message = ""
        self.__force_send = False

    def setup(self):
        super().setup()
        self.__encoder_manager = self.component_map["EncoderManager"]
        self.__session_ring = self.canonical_parent._session_ring_custom

        config = self._user_config or DEFAULT_CONFIG

        global PREFER_TRACK_NAME_FOR_VOLUME
        if "prefer_track_name" in config:
            PREFER_TRACK_NAME_FOR_VOLUME = config["prefer_track_name"]
        global USE_GRAPHICS
        if "use_graphics" in config:
            USE_GRAPHICS = config["use_graphics"]

        if "encoder_mappings" in config and config["encoder_mappings"] is not None:
            self._encoder_mapping_line = config["encoder_mappings"] - 1
        if "encoder_values" in config and config["encoder_values"] is not None:
            self._encoder_values_line = config["encoder_values"] - 1
        if "message" in config and config["message"] is not None:
            self._message_line = config["message"] - 1
        if "ring_tracks" in config and config["ring_tracks"] is not None:
            self._ring_tracks_line = config["ring_tracks"] - 1
        if "selected" in config and config["selected"] is not None:
            self._selected_line = config["selected"] - 1

        if "force" in config and config["force"] is True:
            self.__force_send = True
        else:
            self._on_control_surfaces_changed()

        if (
            self._encoder_mapping_line is not False
            or self._encoder_values_line is not False
        ):
            watching_encoders = True
        else:
            watching_encoders = False

        if watching_encoders:
            for i in range(8):
                enc_name = f"{ENC_PREFIX}{i+1}"
                enc_obj = self.__encoder_manager.get_encoder(enc_name)
                self.__push_main_encoders[i] = enc_obj

            for i, enc in enumerate(self.__push_main_encoders):
                watcher = EncoderWatcher(self, enc, i)
                self.__encoder_watchers.append(watcher)

        if self._ring_tracks_line is not False:
            self.tracks_changed.subject = self.__session_ring
            self.tracks_changed()

        if self._selected_line is not False:
            self.selected_scene_changed.subject = self.song.view
            self.selected_track_changed()
            self.selected_device_changed.subject = self.song.view.selected_track.view

        if self._selected_line is not False or self._ring_tracks_line is not False:
            self.selected_track_changed.subject = self.song.view

        if self._message_line:
            self.write_message_to_line(
                "                       welcome to  zcx for push 1", timeout=5.0
            )

        self.add_api_method("write_display_message", self.receive_message_from_ua)
        self._on_control_surfaces_changed.subject = self.canonical_parent.application

    @property
    def suppress_send(self):
        if self.__force_send is True:
            return False
        else:
            return self.__suppress_send

    def receive_sysex(self, midi_bytes: tuple[int]):
        if midi_bytes == LIVE_MODE:
            self.__suppress_send = True
        elif midi_bytes == USER_MODE:
            self.__suppress_send = False

    def send_sysex(self, msg):
        # Suppressing write here, because even if we are not writing to display,
        # we still want to process and cache messages
        if self.suppress_send:
            return
        # Convert bytearray to tuple for MIDI sending
        if isinstance(msg, bytearray):
            msg = tuple(msg)
        self.__send_midi(msg)

    def _mark_line_dirty(self, line_num):
        """Mark a line as dirty and schedule its update"""
        if line_num is False or not (0 <= line_num <= 3):
            return

        self._dirty_lines[line_num] = True

        # Kill existing timer if it exists
        if self._line_timers[line_num] is not None:
            self._line_timers[line_num].kill()

        # Create new timer
        timer = DisplayUpdateDebounceTimer(self, line_num, duration=0.01)
        self._line_timers[line_num] = timer
        self.canonical_parent._task_group.add(timer)
        timer.restart()

    def _flush_line(self, line_num):
        """Send the cached line data to the display"""
        if not self._dirty_lines[line_num]:
            return

        self.send_sysex(self._line_bytes_cache[line_num])
        self._dirty_lines[line_num] = False
        self._line_timers[line_num] = None

    def refresh_feedback(self):
        wait_timer = DelayedDisplayRefreshTask(self)
        self.canonical_parent._task_group.add(wait_timer)
        wait_timer.restart()

    def _do_refresh_feedback(self):
        for line_bytes in self._line_bytes_cache:
            self.send_sysex(line_bytes)

    def write_message_to_line(self, msg: str, line_number=None, timeout: float = 0.0, immediate=False):
        """
        Writes a message of up to 68 chars to a line on display.
        :param line_number:
        :param msg:
        :param timeout:
        :param immediate: If True, bypass batching and send immediately
        :return:
        """
        if line_number is None:
            line_number = self._message_line
            if line_number is False:
                raise RuntimeError("line_number is required")

        if timeout == 0.0:
            self._persistent_message = msg

        if line_number not in {0, 1, 2, 3}:
            raise ValueError(f"Invalid line number {line_number}")

        # Get the line cache and modify it in place
        line_cache = self._line_bytes_cache[line_number]

        # Fill with spaces (ASCII 32) from position 8 onwards
        for i in range(8, 76):
            line_cache[i] = 32

        # Write the message bytes
        for i, char in enumerate(msg[:68]):
            line_cache[8 + i] = self.ascii_ord(char)

        if immediate:
            self.send_sysex(line_cache)
        else:
            self._mark_line_dirty(line_number)

        if timeout != 0.0:
            task = DeleteMessageTask(self, line_number, duration=timeout)
            self.canonical_parent._task_group.add(task)
            task.restart()

    def _clear_old_message(self, line_number):
        if len(self._persistent_message) > 0:
            self.write_message_to_line(self._persistent_message, line_number)
            return
        else:
            self.write_message_to_line("", line_number)

    def string_to_ascii_bytes(self, string):
        # More efficient: use generator expression
        return tuple(self.ascii_ord(char) for char in string)

    def update_display_segment(self, line_num, seg_num, msg, smart_truncate=True):
        if len(msg) > 8:
            if smart_truncate:
                msg = self.shorten_string_fast(msg)
            else:
                msg = msg[:8]

        line_bytes = self._line_bytes_cache[line_num]

        start_i, end_i = SEGMENT_INDICES[seg_num]
        # Adjust for the 8-byte prefix offset
        actual_start = start_i + 8
        actual_end = end_i + 8

        # Clear the segment with spaces
        for i in range(actual_start, actual_end):
            line_bytes[i] = 32

        # Write the message bytes
        for i, char in enumerate(msg):
            if actual_start + i >= actual_end:
                break
            line_bytes[actual_start + i] = self.ascii_ord(char)

        # Mark line as dirty instead of sending immediately
        self._mark_line_dirty(line_num)

    def multi_segment_message(self, line_num, start_segment, end_segment, msg):
        """
        Writes a message across a range of contiguous display segments on the same line.
        If the message is too long, it will only be truncated from the final segment.

        :param line_num: The line number (0-3) to write to
        :param start_segment: The starting segment index (0-7)
        :param end_segment: The ending segment index (0-7), inclusive
        :param msg: The message to write across the segments
        """
        if not (0 <= line_num <= 3):
            raise ValueError(f"Invalid line number {line_num}")

        if not (0 <= start_segment <= 7) or not (0 <= end_segment <= 7):
            raise ValueError(
                f"Invalid segment indices: start={start_segment}, end={end_segment}"
            )

        if start_segment > end_segment:
            raise ValueError(f"Start segment must be less than or equal to end segment")

        start_i, _ = SEGMENT_INDICES[start_segment]
        _, end_i = SEGMENT_INDICES[end_segment]

        line_bytes = self._line_bytes_cache[line_num]

        # Adjust for the 8-byte prefix offset
        actual_start = start_i + 8
        actual_end = end_i + 8
        max_length = actual_end - actual_start

        # Clear the range with spaces
        for i in range(actual_start, actual_end):
            line_bytes[i] = 32

        # Write the message (truncated if necessary)
        msg_to_write = msg[:max_length]
        for i, char in enumerate(msg_to_write):
            line_bytes[actual_start + i] = self.ascii_ord(char)

        # Mark line as dirty instead of sending immediately
        self._mark_line_dirty(line_num)

    @listens('control_surfaces')
    def _on_control_surfaces_changed(self):
        push_1_factory = False
        for cs in list(self.canonical_parent.application.control_surfaces):
            if cs.__class__.__name__ == "Push":
                push_1_factory = True
                break

        self.__force_send = not push_1_factory
        self.refresh_feedback()

    @classmethod
    def splice_tuple(cls, t, start_index, end_index, new) -> tuple:
        """
        Splices new values into an existing tuple.
        If the new portion is shorter than the replaced portion, ASCII char 32 (' ') is appended to new portion.

        NOTE: This method is now deprecated in favor of direct bytearray manipulation,
        but kept for backward compatibility.

        :param t: Original tuple
        :param start_index: Start index of the portion to be replaced
        :param end_index: End index (exclusive) of the portion to be replaced
        :param new: New values to insert (must be iterable)
        :return: A new tuple with the modifications
        """
        replacement_length = end_index - start_index
        if len(new) < replacement_length:
            new += (32,) * (replacement_length - len(new))

        return t[:start_index] + new + t[end_index:]

    @listens("tracks")
    def tracks_changed(self):
        offset = self.__session_ring.track_offset
        tracks = self.__session_ring.tracks_to_use()[offset:]
        for i in range(8):
            try:
                track = tracks[i]
                if track == self._song.view.selected_track:
                    self.update_display_segment(
                        self._ring_tracks_line, i, f"▶{track.name}"
                    )
                else:
                    self.update_display_segment(self._ring_tracks_line, i, track.name)
            except IndexError:
                self.update_display_segment(self._ring_tracks_line, i, "")

    @listens("selected_track")
    def selected_track_changed(self):
        if self._ring_tracks_line:
            self.tracks_changed()
        self.selected_device_changed.subject = self.song.view.selected_track.view
        self.update_selected_line()

    @listens("selected_scene")
    def selected_scene_changed(self):
        self.update_selected_line()

    @listens("selected_device")
    def selected_device_changed(self):
        self.update_selected_line()

    def update_selected_line(self):
        if self._selected_line is False:
            return

        track = self.song.view.selected_track
        scene = self.song.view.selected_scene
        scene_num = list(self.song.scenes).index(scene)
        device = track.view.selected_device

        track_name = track.name
        scene_name = scene.name

        if scene_name:
            if scene_name.startswith("["):
                end_bracket = scene_name.find("]")
                if end_bracket > 0:
                    scene_name = scene_name[1:end_bracket]
                elif scene_name == "[]":
                    scene_name = ""

        scene_name_format = "" if not scene_name else f"- {scene_name}"

        self.multi_segment_message(self._selected_line, 0, 3, f"t: {track_name}")
        if device:
            self.multi_segment_message(self._selected_line, 4, 5, f"d: {device.name}")
        else:
            self.multi_segment_message(self._selected_line, 4, 5, f"d: ---")
        self.multi_segment_message(
            self._selected_line, 6, 7, f"s: {scene_num + 1}{scene_name_format}"
        )

    def shorten_string_fast(self, s, max_len=8):
        if len(s) <= max_len:
            return s

        remove_set = set("AEIOYURSaeoyurs ")

        freq = Counter(s[0:])

        chars_to_remove = sorted(remove_set, key=lambda x: (x != " ", -freq.get(x, 0)))

        result = s[0]

        for char in s[1:]:
            if len(result) >= max_len:
                break
            if char not in chars_to_remove:
                result += char

        if len(result) > max_len:
            for char in chars_to_remove:
                if len(result) <= max_len:
                    break
                result = result[0] + result[1:].replace(char, "")

        return result[:max_len]

    def receive_message_from_ua(self, message: str, timeout=3.0) -> bool:
        try:
            message = str(message)
            self.write_message_to_line(
                message, line_number=self._message_line, timeout=timeout, immediate=True
            )

        except Exception as e:
            self.error(e)
            self.error(f"Failed to write message: {message}")
            return False

        return True

    def ascii_ord(self, char):
        SPECIAL_CHARS = {"│": 3, "┑": 4, "┃": 5, "┅": 6, "▶": 127}
        return SPECIAL_CHARS.get(char, min(ord(char), 127))

    def create_slider_graphic(self, _min, _max, current, bipolar=False):
        percentage = to_percentage(_min, _max, current)
        if not bipolar:
            if percentage < 12.5:  # 8 chars to a segment
                return "│┅┅┅┅┅┅┅"
            full_bars, remainder = divmod(percentage, 12.5)

            content = "┃┃┃┃┃┃┃┃"[0 : int(full_bars)]
            if remainder > 6.25:
                content += "│"
            while len(content) < 8:
                content += "┅"
            return content
        else:
            if percentage < 6.25:
                return "┃┃┃┃┅┅┅┅"
            elif percentage < 12.5:
                return "┑┃┃┃┅┅┅┅"
            elif percentage < 18.75:
                return "┅┃┃┃┅┅┅┅"
            elif percentage < 25:
                return "┅┑┃┃┅┅┅┅"
            elif percentage < 31.25:
                return "┅┅┃┃┅┅┅┅"
            elif percentage < 37.5:
                return "┅┅┑┃┅┅┅┅"
            elif percentage < 43.75:
                return "┅┅┅┃┅┅┅┅"
            elif percentage < 49:
                return "┅┅┅┑┅┅┅┅"
            elif 49 <= percentage <= 51:
                return "┅┅┅┑│┅┅┅"
            elif percentage < 56.25:
                return "┅┅┅┅│┅┅┅"
            elif percentage < 62.5:
                return "┅┅┅┅┃┅┅┅"
            elif percentage < 68.75:
                return "┅┅┅┅┃│┅┅"
            elif percentage < 75:
                return "┅┅┅┅┃┃┅┅"
            elif percentage < 87.5:
                return "┅┅┅┅┃┃┃┅"
            else:
                return "┅┅┅┅┃┃┃┃"


class DelayedDisplayRefreshTask(TimerTask):

    def __init__(self, owner, duration=0.2, **k):
        super().__init__(duration=duration)
        self._owner: ZCXCore = owner
        self.restart()

    def on_finish(self):
        self._owner.debug(f"timer finished")
        self._owner._do_refresh_feedback()


class DeleteMessageTask(TimerTask):

    def __init__(self, owner, line_number: int, duration=3.0, **k):
        super().__init__(duration=duration, **k)
        self._owner: ZCXCore = owner
        self._line_number: int = line_number
        self.restart()

    def on_finish(self):
        self._owner._clear_old_message(line_number=self._line_number)


class DisplayUpdateDebounceTimer(TimerTask):

    def __init__(self, owner, line_num, duration=0.01, **k):
        super().__init__(duration=duration, **k)
        self._owner: Push1Display = owner
        self._line_num: int = line_num

    def on_finish(self):
        self._owner._flush_line(self._line_num)


class EncoderWatcher(EventObject):

    def __init__(self, component, encoder, index):
        super().__init__()
        self._component: "Push1Display" = component
        self._encoder = encoder
        self._index = index
        self.parameter_rebound.subject = encoder
        self.parameter_value.subject = None
        self._current_parameter = None

    @listens("mapped_parameter")
    def parameter_rebound(self, par):
        if par is None:
            self._current_parameter = None
            self._component.update_display_segment(
                self._component._encoder_mapping_line, self._index, ""
            )
            self.parameter_value(None)
            return
        self._current_parameter = par
        par_name = par.name
        if par_name == "Track Volume":
            if PREFER_TRACK_NAME_FOR_VOLUME:
                par_name = par.canonical_parent.canonical_parent.name
            else:
                par_name = "Volume"
        elif par_name == "Track Panning":
            par_name = "Pan"

        if self._component._encoder_mapping_line is not False:
            self._component.update_display_segment(
                self._component._encoder_mapping_line, self._index, par_name
            )

        self.parameter_value.subject = self._current_parameter
        self.parameter_value(None)

    @listens("value")
    def parameter_value(self, val=None):
        if not self._component._encoder_values_line:
            return

        par_val = ""

        try:
            if self._current_parameter is None:
                self._component.update_display_segment(
                    self._component._encoder_values_line, self._index, ""
                )
                return
            if USE_GRAPHICS and (
                self._current_parameter.canonical_parent.__class__.__name__
                == "MixerDevice"
                and self._current_parameter.__str__().endswith("dB")
            ):
                par_val = self._component.create_slider_graphic(
                    self._current_parameter.min,
                    self._current_parameter.max,
                    self._current_parameter.value,
                )
            elif self._current_parameter.name == "Track Panning" and USE_GRAPHICS:
                par_val = self._component.create_slider_graphic(
                    self._current_parameter.min,
                    self._current_parameter.max,
                    self._current_parameter.value,
                    True,
                )
            else:
                par_val = self._current_parameter.__str__()
        except Exception as e:
            self._component.error(e)

        self._component.update_display_segment(
            self._component._encoder_values_line, self._index, par_val
        )
