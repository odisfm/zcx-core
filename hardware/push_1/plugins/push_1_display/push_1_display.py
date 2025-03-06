from typing import TYPE_CHECKING, Optional
from collections import Counter

from ableton.v3.base import EventObject
from ableton.v3.base import listens_group, listens
from Push.sysex import *

from ableton.v2.base.task import TimerTask

if TYPE_CHECKING:
    from app.zcx_core import ZCXCore
    from app.zcx_plugin import ZCXPlugin
    from app.z_encoder import ZEncoder
    from app.encoder_manager import EncoderManager
    from app.session_ring import SessionRing

ENC_PREFIX = 'enc_'

SEGMENT_INDICES = [
    (0, 8),
    (9, 18),

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
    "ring_tracks": 4
}

class Push1Display(ZCXPlugin):

    def __init__(
            self,
            name="Push1Display",
            *a,
            **k
    ):
        super().__init__(name, *a, **k)
        self.set_logger_level('debug')
        self.__send_midi = self.canonical_parent._do_send_midi
        self.__push_main_encoders: 'Optional[list[ZEncoder]]' = [None]*8
        self.__encoder_manager: 'EncoderManager' = None
        self.__encoder_watchers: 'list[EncoderWatcher]' = []
        self.__session_ring: 'SessionRing' = None

        self._line_bytes_cache = [
            WRITE_LINE1 + (32,) * 68 + (247,),
            WRITE_LINE2 + (32,) * 68 + (247,),
            WRITE_LINE3 + (32,) * 68 + (247,),
            WRITE_LINE4 + (32,) * 68 + (247,)
        ]

        self._encoder_mapping_line = False
        self._encoder_values_line = False
        self._message_line = False
        self._ring_tracks_line = False

        self._persistent_message = ''

    def setup(self):
        super().setup()
        self.__encoder_manager = self.component_map['EncoderManager']
        self.__session_ring = self.canonical_parent._session_ring_custom

        config = self._user_config or DEFAULT_CONFIG

        if 'encoder_mapping' in config and config['encoder_mapping']:
            self._encoder_mapping_line = config['encoder_mapping'] - 1
        if 'encoder_values' in config and config['encoder_values'] > 0:
            self._encoder_values_line = config['encoder_values'] - 1
        if 'message' in config and config['message']:
            self._message_line = config['message'] - 1
        if 'ring_tracks' in config and config['ring_tracks']:
            self._ring_tracks_line = config['ring_tracks'] - 1

        if self._encoder_mapping_line is not False or self._encoder_values_line is not False:
            watching_encoders = True
        else:
            watching_encoders = False

        if watching_encoders:
            for i in range(8):
                enc_name = f'{ENC_PREFIX}{i+1}'
                enc_obj = self.__encoder_manager.get_encoder(enc_name)
                self.__push_main_encoders[i] = enc_obj

            for i, enc in enumerate(self.__push_main_encoders):
                watcher = EncoderWatcher(self, enc, i)
                self.__encoder_watchers.append(watcher)

        if self._ring_tracks_line is not False:
            self.tracks_changed.subject = self.__session_ring
            self.tracks_changed()

        if self._message_line:
            self.write_message_to_line('                       welcome to  zcx for push 1', timeout=5.0)

    def send_sysex(self, msg):
        self.__send_midi(msg)

    def refresh_feedback(self):
        wait_timer = DelayedDisplayRefreshTask(self)
        self.canonical_parent._task_group.add(wait_timer)
        wait_timer.restart()

    def _do_refresh_feedback(self):
        for line_bytes in self._line_bytes_cache:
            self.send_sysex(line_bytes)

    def write_message_to_line(self, msg: str, line_number=None, timeout: float=0.0):
        """
        Writes a message of up to 68 chars to a line on display.
        :param line_number:
        :param msg:
        :param timeout:
        :return:
        """
        ascii_message = self.string_to_ascii_bytes(msg)

        if line_number is None:
            line_number = self._message_line
            if line_number is False:
                raise RuntimeError('line_number is required')

        if timeout == 0.0:
            self._persistent_message = msg

        if len(ascii_message) < 68:
            ascii_message = ascii_message + tuple(32 for _ in range(68 - len(ascii_message)))

        if line_number not in {0, 1, 2, 3}:
            raise ValueError(f'Invalid line number {line_number}')

        match line_number:
            case 0:
                line_start = WRITE_LINE1
            case 1:
                line_start = WRITE_LINE2
            case 2:
                line_start = WRITE_LINE3
            case 3:
                line_start = WRITE_LINE4
            case _:
                raise ValueError(f'Invalid line number {line_number}')

        final = line_start + ascii_message + (247,)

        self.send_sysex(final)

        self._line_bytes_cache[line_number] = final

        if timeout != 0.0:
            task = DeleteMessageTask(self, line_number, duration=timeout)
            self.canonical_parent._task_group.add(task)
            task.restart()

    def _clear_old_message(self, line_number):
        if len(self._persistent_message) > 0:
            self.write_message_to_line(self._persistent_message, line_number)
            return
        else:
            self.write_message_to_line('', line_number)

    def string_to_ascii_bytes(self, string):
        _bytes = []
        for char in string:
            _bytes.append(ord(char))

        return tuple(_bytes)

    def update_display_segment(self, line_num, seg_num, msg, smart_truncate=True):
        if len(msg) > 8:
            if smart_truncate:
                msg = self.shorten_string_fast(msg)
            else:
                msg = msg[:8]

        line_bytes = self._line_bytes_cache[line_num]
        message_portion = line_bytes[8:77]

        start_i, end_i = SEGMENT_INDICES[seg_num]

        new_portion_bytes = self.string_to_ascii_bytes(msg)

        new_message_portion = self.splice_tuple(message_portion, start_i, end_i, new_portion_bytes)

        match line_num:
            case 0:
                line_start = WRITE_LINE1
            case 1:
                line_start = WRITE_LINE2
            case 2:
                line_start = WRITE_LINE3
            case 3:
                line_start = WRITE_LINE4
            case _:
                raise ValueError(f'Invalid line number {line_num}')

        final = line_start + new_message_portion

        self.send_sysex(final)

        self._line_bytes_cache[line_num] = final

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
            raise ValueError(f'Invalid line number {line_num}')

        if not (0 <= start_segment <= 7) or not (0 <= end_segment <= 7):
            raise ValueError(f'Invalid segment indices: start={start_segment}, end={end_segment}')

        if start_segment > end_segment:
            raise ValueError(f'Start segment must be less than or equal to end segment')

        start_i, _ = SEGMENT_INDICES[start_segment]
        _, end_i = SEGMENT_INDICES[end_segment]

        line_bytes = self._line_bytes_cache[line_num]
        message_portion = line_bytes[8:77]

        msg_bytes = self.string_to_ascii_bytes(msg)

        if len(msg_bytes) > (end_i - start_i):
            msg_bytes = msg_bytes[:end_i - start_i - 1]

        new_message_portion = self.splice_tuple(message_portion, start_i, end_i, msg_bytes)

        match line_num:
            case 0:
                line_start = WRITE_LINE1
            case 1:
                line_start = WRITE_LINE2
            case 2:
                line_start = WRITE_LINE3
            case 3:
                line_start = WRITE_LINE4
            case _:
                raise ValueError(f'Invalid line number {line_num}')

        final = line_start + new_message_portion

        self.send_sysex(final)
        self._line_bytes_cache[line_num] = final

    @classmethod
    def splice_tuple(cls, t, start_index, end_index, new) -> tuple:
        """
        Splices new values into an existing tuple.
        If the new portion is shorter than the replaced portion, ASCII char 32 (' ') is appended to new portion.

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

    @listens('tracks')
    def tracks_changed(self):
        offset = self.__session_ring.track_offset
        tracks = self.__session_ring.tracks_to_use()[offset:]
        for i in range(8):
            try:
                track = tracks[i]
                self.update_display_segment(self._ring_tracks_line, i, track.name)
            except IndexError:
                self.update_display_segment(self._ring_tracks_line, i, '')

    def shorten_string_fast(self, s, max_len=8):
        if len(s) <= max_len:
            return s

        remove_set = set('AEIOYURSaeoyurs ')

        freq = Counter(s[0:])

        chars_to_remove = sorted(remove_set, key=lambda x: (x != ' ', -freq.get(x, 0)))

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
                result = result[0] + result[1:].replace(char, '')

        return result[:max_len]

class DelayedDisplayRefreshTask(TimerTask):

    def __init__(self, owner, duration=.2, **k):
        super().__init__(duration=duration)
        self._owner: ZCXCore = owner
        self.restart()

    def on_finish(self):
        self._owner.debug(f'timer finished')
        self._owner._do_refresh_feedback()

class DeleteMessageTask(TimerTask):

    def __init__(self, owner, line_number: int, duration=3.0, **k):
        super().__init__(duration=duration, **k)
        self._owner: ZCXCore = owner
        self._line_number: int = line_number
        self.restart()

    def on_finish(self):
        self._owner._clear_old_message(line_number=self._line_number)

class EncoderWatcher(EventObject):

    def __init__(self, component, encoder, index):
        super().__init__()
        self._component: 'Push1Display' = component
        self._encoder = encoder
        self._index = index
        self.parameter_rebound.subject = encoder
        self.parameter_value.subject = None
        self._current_parameter = None

    @listens('mapped_parameter')
    def parameter_rebound(self, par):
        if par is None:
            self._current_parameter = None
            self._component.update_display_segment(self._component._encoder_mapping_line, self._index, '')
            self.parameter_value(None)
            return
        self._current_parameter = par
        par_name = par.name
        if par_name == 'Track Volume':
            par_name = par.canonical_parent.canonical_parent.name

        self._component.update_display_segment(self._component._encoder_mapping_line, self._index, par_name)

        self.parameter_value.subject = self._current_parameter
        self.parameter_value(None)

    @listens('value')
    def parameter_value(self, val=None):
        if self._current_parameter is None:
            self._component.update_display_segment(self._component._encoder_values_line, self._index, '')
            return
        par_val = self._current_parameter.__str__()

        self._component.update_display_segment(self._component._encoder_values_line, self._index, par_val)
