from ableton.v3.control_surface.default_bank_definitions import BANK_DEFINITIONS
from ClyphX_Pro.clyphx_pro import ParamUtils

def get_banked_parameter(device_obj, device_name, bank_num, param_num, skip_empty=True):
    param, remaining_args = ParamUtils.get_instant_mapping_parameter(device_obj, [f"b{bank_num}", f"p{param_num}"])
    return param
