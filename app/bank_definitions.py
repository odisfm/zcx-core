from ableton.v3.control_surface.default_bank_definitions import BANK_DEFINITIONS


def get_banked_parameter(device_name, bank_num, param_num, skip_empty=True):

    device_def = BANK_DEFINITIONS[device_name]
    if not device_def:
        raise AttributeError(f"No bank definition for device `{device_name}`")
    bank_def = None
    bank_list = list(device_def.values())
    try:
        bank_def = list(device_def.values())[bank_num]
    except IndexError:
        raise AttributeError(f"`{device_name}` has no bank {bank_num} ({len(bank_list)} banks)")
    bank_params = bank_def.get("Parameters")

    idx = 0
    for param in bank_params:
        if skip_empty and param == "":
            continue
        if idx == param_num:
            if isinstance(param, str):
                return param
            return param._default_parameter_name
        idx += 1

    raise AttributeError(f"`{device_name}` has no param B{bank_num + 1} P{param_num + 1} ({len(bank_params)} params in bank)\n{bank_params}")
