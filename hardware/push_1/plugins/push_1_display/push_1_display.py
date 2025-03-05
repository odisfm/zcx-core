from typing import TYPE_CHECKING

from Push.sysex import *

if TYPE_CHECKING:
    from app.zcx_plugin import ZCXPlugin


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

    def setup(self):
        super().setup()

    def send_sysex(self, unique_portion):
        msg = unique_portion + (247,)
        self.debug(msg)
        self.__send_midi(msg)

    def write_message_to_line(self, msg: str, line_number: int):
        """
        Writes a message of up to 68 chars to a line on display.
        :param line_number:
        :param msg:
        :return:
        """
        _bytes = []
        for char in msg:
            _bytes.append(ord(char))

        _bytes = tuple(_bytes)
        if len(_bytes) < 68:
            _bytes = _bytes + tuple(0 for _ in range(68 - len(_bytes)))

        line_start = None

        match line_number:
            case 1:
                line_start = WRITE_LINE1
            case 2:
                line_start = WRITE_LINE2
            case 3:
                line_start = WRITE_LINE3
            case 4:
                line_start = WRITE_LINE4

        final = line_start + _bytes

        self.send_sysex(final)
