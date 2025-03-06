from typing import TYPE_CHECKING, Optional

from ableton.v3.base import EventObject
from ableton.v3.base import listens_group, listens
from Push.sysex import *

from ableton.v2.base.task import TimerTask

if TYPE_CHECKING:
    from app.zcx_plugin import ZCXPlugin
    from app.z_encoder import ZEncoder
    from app.encoder_manager import EncoderManager

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

        self._line_bytes_cache = [None]*4

        self._line_bytes_cache[0] = WRITE_LINE1 + (32,)*68 + (247,)
        self._line_bytes_cache[1] = WRITE_LINE2 + (32,)*68 + (247,)
        self._line_bytes_cache[2] = WRITE_LINE3 + (32,)*68 + (247,)
        self._line_bytes_cache[3] = WRITE_LINE4 + (32,)*68 + (247,)

    def setup(self):
        super().setup()
        self.__encoder_manager = self.component_map['EncoderManager']
        for i in range(8):
            enc_name = f'{ENC_PREFIX}{i+1}'
            enc_obj = self.__encoder_manager.get_encoder(enc_name)
            self.__push_main_encoders[i] = enc_obj

        for i, enc in enumerate(self.__push_main_encoders):
            watcher = EncoderWatcher(self, enc, i)
            self.__encoder_watchers.append(watcher)

        self.write_message_to_line('                       welcome to  zcx for push 1', 2)

    def send_sysex(self, msg):
        self.debug(msg)
        self.__send_midi(msg)

    def refresh_feedback(self):
        wait_timer = DelayedDisplayRefreshTask(self)
        self.canonical_parent._task_group.add(wait_timer)
        wait_timer.restart()

    def _do_refresh_feedback(self):
        for line_bytes in self._line_bytes_cache:
            self.send_sysex(line_bytes)

    def write_message_to_line(self, msg: str, line_number: int):
        """
        Writes a message of up to 68 chars to a line on display.
        :param line_number:
        :param msg:
        :return:
        """
        ascii_message = self.string_to_ascii_bytes(msg)

        if len(ascii_message) < 68:
            ascii_message = ascii_message + tuple(32 for _ in range(68 - len(ascii_message)))

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

    def string_to_ascii_bytes(self, string):
        _bytes = []
        for char in string:
            _bytes.append(ord(char))

        return tuple(_bytes)

    def update_display_segment(self, line_num, seg_num, msg):
        if len(msg) > 8:
            raise ValueError(f'Message too long (segment is 8 chars):\n{msg}')

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
                raise ValueError(f'Invalid line number {line_number}')

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


class DelayedDisplayRefreshTask(TimerTask):

    def __init__(self, owner, duration=.2, **k):
        super().__init__(duration=duration)
        self._owner: ZCXCore = owner
        self.restart()

    def on_finish(self):
        self._owner.debug(f'timer finished')
        self._owner._do_refresh_feedback()

class EncoderWatcher(EventObject):

    def __init__(self, component, encoder, index):
        super().__init__()
        self._component: 'Push1Display' = component
        self._encoder = encoder
        self._index = index
        self.parameter_rebound.subject = encoder
        self.parameter_value.subject = encoder._control_element
        self._current_parameter = None

    @listens('mapped_parameter')
    def parameter_rebound(self, par):
        if par is None:
            self._current_parameter = None
            self._component.update_display_segment(0, self._index, '')
            self.parameter_value(None)
            return
        self._current_parameter = par
        par_name = par.name
        if par_name == 'Track Volume':
            par_name = par.canonical_parent.canonical_parent.name

        if len(par_name) > 8:
            par_name = par_name[:8]

        self._component.update_display_segment(0, self._index, par_name)

        self.parameter_value(None)

    @listens('value')
    def parameter_value(self, val):
        if self._current_parameter is None:
            self._component.update_display_segment(1, self._index, '')
            return
        par_val = self._current_parameter.__str__()
        if len(par_val) > 8:
            par_val = par_val[:8]
        self._component.update_display_segment(1, self._index, par_val)
