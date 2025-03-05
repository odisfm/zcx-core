from typing import TYPE_CHECKING, Optional

from ableton.v3.base import listens_group
from Push.sysex import *

from ableton.v2.base.task import TimerTask

if TYPE_CHECKING:
    from app.zcx_plugin import ZCXPlugin
    from app.z_encoder import ZEncoder
    from app.encoder_manager import EncoderManager

ENC_PREFIX = 'enc_'

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

        self.debug(self.__push_main_encoders)
        self.parameter_remapped.replace_subjects(self.__push_main_encoders)

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
            case 1:
                line_start = WRITE_LINE1
            case 2:
                line_start = WRITE_LINE2
            case 3:
                line_start = WRITE_LINE3
            case 4:
                line_start = WRITE_LINE4
            case _:
                raise ValueError(f'Invalid line number {line_number}')

        final = line_start + ascii_message + (247,)

        self.send_sysex(final)

        self._line_bytes_cache[line_number - 1] = final

    def string_to_ascii_bytes(self, string):
        _bytes = []
        for char in string:
            _bytes.append(ord(char))

        return tuple(_bytes)

    @listens_group('mapped_parameter')
    def parameter_remapped(self, enc_obj):
        self.debug(f'{enc_obj} remapped: {enc_obj.mapped_parameter.name}')
        self.debug(self.__push_main_encoders)


class DelayedDisplayRefreshTask(TimerTask):

    def __init__(self, owner, duration=.2, **k):
        super().__init__(duration=duration)
        self._owner: ZCXCore = owner
        self.restart()

    def on_finish(self):
        self._owner.debug(f'timer finished')
        self._owner._do_refresh_feedback()
