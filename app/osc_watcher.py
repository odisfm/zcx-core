from ableton.v3.base import listens
from ableton.v2.base.event import EventObject

from .cxp_bridge import CxpBridge
from .z_encoder import ZEncoder
from .encoder_element import EncoderElement


def re_range_float_parameter(min_val, max_val, current):
    if max_val == min_val:
        return 0.0

    normalized = (current - min_val) / (max_val - min_val)

    return max(0.0, min(1.0, normalized))


def re_range_int_parameter(min_val, max_val, current):
    if max_val == min_val:
        return 0

    normalized = (current - min_val) / (max_val - min_val)
    clamped = max(0.0, min(1.0, normalized))

    return int(clamped * 127)

class OscWatcher(EventObject):

    address_prefix: str = 'zcx/'
    _osc_server = None

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)


class OscEncoderWatcher(OscWatcher):

    send_string = True
    send_float = True
    send_int = True
    send_name = True

    def __init__(self, z_encoder, *a, **kw):
        super().__init__(*a, **kw)
        self._z_encoder: ZEncoder = z_encoder
        self._base_element: EncoderElement = self._z_encoder._control_element

        self._base_osc_address = self.address_prefix + f'enc/{self._z_encoder._name}/'
        self._string_osc_address = self._base_osc_address + 'value/'
        self._float_osc_address = self._base_osc_address + 'float/'
        self._int_osc_address = self._base_osc_address + 'int/'
        self._name_osc_address = self._base_osc_address + 'name/'

        self.parameter_value_changed.subject = self._base_element
        if self.send_name:
            self.parameter_name_changed.subject = self._base_element

    @listens('parameter_value')
    def parameter_value_changed(self):
        if self._base_element.parameter is None:
            if self.send_string:
                self._osc_server.sendOSC(self._string_osc_address, '-')
            if self.send_float:
                self._osc_server.sendOSC(self._float_osc_address, 0.0)
            if self.send_int:
                self._osc_server.sendOSC(self._int_osc_address, 0)
        else:
            if self.send_string:
                self._osc_server.sendOSC(self._string_osc_address, self._base_element.parameter_value)
            if self.send_float:
                self._osc_server.sendOSC(self._float_osc_address, re_range_float_parameter(self._base_element.parameter.min, self._base_element.parameter.max, self._base_element.parameter.value))
            if self.send_int:
                self._osc_server.sendOSC(self._int_osc_address, re_range_int_parameter(self._base_element.parameter.min, self._base_element.parameter.max, self._base_element.parameter.value))

    @listens('parameter_name')
    def parameter_name_changed(self):
        if self._base_element.parameter is None:
            if self.send_string:
                self._osc_server.sendOSC(self._name_osc_address, '-')
        else:
            self._osc_server.sendOSC(self._name_osc_address, self._base_element.parameter_name)
