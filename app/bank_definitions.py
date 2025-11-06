from ableton.v3.control_surface.default_bank_definitions import BANK_DEFINITIONS
from ClyphX_Pro.clyphx_pro import ParamUtils

from .yaml_loader import yaml_loader
from .errors import CriticalConfigurationError

class InvalidCustomBanksError(Exception):
    pass

DEF_FILE_NAME = "custom_banks.yaml"
PARAMS_PER_BANK = 8
DEFAULT_FALLBACK_BEHAVIOUR = True

custom_class_banks = {}
custom_instance_banks = {}

try:
    from . import ROOT_LOGGER
    from . import PREF_MANAGER

    custom_bank_definitions = yaml_loader.load_yaml(f"{PREF_MANAGER.config_dir}/{DEF_FILE_NAME}")

    if not custom_bank_definitions:
        custom_bank_definitions = []
    elif not isinstance(custom_bank_definitions, list):
        raise InvalidCustomBanksError(f"Custom bank definitions must be a list, ignoring {DEF_FILE_NAME}")

    for entry in custom_bank_definitions:
        device_class_name = entry.get("class_name")
        device_instance_name = entry.get("instance_name")

        entry_type = None
        entry_name = None

        if device_class_name and device_instance_name:
            raise InvalidCustomBanksError(f"Custom bank definitions must not have both class_name and instance_name")
        elif not device_class_name and not device_instance_name:
            raise InvalidCustomBanksError(f"Custom bank definitions must class_name or instance_name")
        elif device_class_name:
            entry_type = "class"
            entry_name = device_class_name
        elif device_instance_name:
            entry_type = "instance"
            entry_name = device_instance_name

        all_banks_def = entry.get("banks")
        if all_banks_def is None:
            raise InvalidCustomBanksError(
                f"Custom bank definition for {entry_type} {entry_name} missing `banks` key"
            )
        elif not isinstance(all_banks_def, list):
            raise InvalidCustomBanksError(
                f"Custom bank definition for {entry_type} {entry_name} must be a list of lists"
            )

        for i, bank_def in enumerate(all_banks_def):
            if not isinstance(bank_def, list):
                raise InvalidCustomBanksError(
                    f"Error in custom bank definition for {entry_type} {entry_name} must be a list of lists"
                )
            bank_len = len(bank_def)
            if bank_len > PARAMS_PER_BANK:
                raise InvalidCustomBanksError(
                    f'Custom bank definition for {entry_type} {entry_name} has more than {PARAMS_PER_BANK} entries'
                )
            elif bank_len < PARAMS_PER_BANK:
                bank_def.extend([None] * (PARAMS_PER_BANK - bank_len))

            for j, param_def in enumerate(bank_def):
                if param_def is not None and not isinstance(param_def, str):
                    raise InvalidCustomBanksError(
                        f'Error in custom bank definition for {entry_type} {entry_name} bank {i} param {j} must be a string (param name) or null'
                    )

        if entry_type == "class":
            custom_class_banks[entry_name] = entry
        elif entry_type == "instance":
            custom_instance_banks[entry_name] = entry

except FileNotFoundError:
    pass
except InvalidCustomBanksError as e:
    from . import STRICT_MODE
    if STRICT_MODE:
        raise CriticalConfigurationError(e)
    else:
        ROOT_LOGGER.error(e)


def get_banked_parameter(device_obj, device_name, bank_num, param_num, skip_empty=True):
    if param_num > PARAMS_PER_BANK:
        raise ValueError(f"Invalid banked parameter number {param_num}. {PARAMS_PER_BANK} parameters per bank.")

    custom_banked_param = get_custom_banked_parameter(device_obj, bank_num, param_num)
    if custom_banked_param or custom_banked_param is None:
        return custom_banked_param

    param, remaining_args = ParamUtils.get_instant_mapping_parameter(device_obj, [f"b{bank_num}", f"p{param_num}"])
    return param

def get_custom_banked_parameter(device_obj, bank_num, param_num):
    if device_obj.name in custom_instance_banks:
        bank_def = custom_instance_banks[device_obj.name]
    elif hasattr(device_obj, "class_display_name") and device_obj.class_display_name in custom_class_banks:
        bank_def = custom_class_banks[device_obj.class_display_name]
    else:
        return False

    fallback = bank_def.get("fallback", DEFAULT_FALLBACK_BEHAVIOUR)
    banks = bank_def["banks"]

    def fail():
        return False if fallback else None

    if bank_num > len(banks):
        return fail()

    this_bank = banks[bank_num - 1]
    this_param = this_bank[param_num - 1]

    if this_param is None:
        return fail()

    for param in device_obj.parameters:
        if param.name == this_param:
            return param

    return fail()
