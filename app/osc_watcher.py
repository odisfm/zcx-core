from ableton.v3.base import listens
from ableton.v2.base.event import EventObject

from .cxp_bridge import CxpBridge
from .encoder_element import EncoderElement
from .pad_section import PadSection

def re_range_float_parameter(min_val, max_val, current):
   return (current - min_val) / (max_val - min_val)

def re_range_int_parameter(min_val, max_val, current):
   return int((current - min_val) * 127 / (max_val - min_val))

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
        self._z_encoder = z_encoder
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

class OscSectionWatcher(OscWatcher):

    def __init__(self, pad_section: PadSection, *a, **kw):
        super().__init__(*a, **kw)
        self._pad_section = pad_section
        self._base_osc_address = self.address_prefix + f'matrix/'
        self.pad_section_view_changed.subject = self._pad_section

    @listens('in_view')
    def pad_section_view_changed(self):
        in_view = self._pad_section.in_view
        if in_view:
            self.update_osc_labels()

    def update_osc_labels(self):
        for i, coord in enumerate(self._pad_section.owned_coordinates):
            control = self._pad_section.owned_controls[i]
            self._osc_server.sendOSC(f'{self._base_osc_address}{coord[0] + 1}/{coord[1] + 1}/', control.osc_label)
