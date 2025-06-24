import logging
import os
from pathlib import Path
from typing import Type

from ableton.v3.control_surface import (
    ControlSurfaceSpecification,
    create_skin
)
from ableton.v3.control_surface.controls import (
    control_matrix,
)

from .action_resolver import ActionResolver
from .api_manager import ApiManager
from .consts import SUPPORTED_GESTURES
from .cxp_bridge import CxpBridge
from .elements import Elements
from .encoder_manager import EncoderManager
from .encoder_state import EncoderState
from .hardware_interface import HardwareInterface
from .mode_manager import ModeManager
from .page_manager import PageManager
from .plugin_loader import PluginLoader
from .skin import Skin
from .z_manager import ZManager
from .z_state import ZState
from .zcx_core import ZCXCore
from .preference_manager import PreferenceManager
from .session_ring import SessionRing


ROOT_LOGGER = None
NAMED_BUTTONS = None
ENCODERS = None
CONFIG_DIR = '_config'
SAFE_MODE = False
PREF_MANAGER = None

plugin_loader: 'Optional[PluginLoader]' = None

def create_mappings(arg) -> dict:
    ROOT_LOGGER.debug('Creating mappings')

    named_button_names = NAMED_BUTTONS.keys()
    encoder_names = ENCODERS.keys()
    prepare_hardware_interface(named_button_names, encoder_names)

    hw_mapping_dict = {}
    naming_function = Elements.format_attribute_name

    for button_name in named_button_names:
        button_name_formatted = naming_function(button_name)
        hw_mapping_dict[button_name_formatted] = button_name_formatted

    for encoder_name in encoder_names:
        encoder_name_formatted = f'_encoder_{encoder_name}'
        hw_mapping_dict[encoder_name_formatted] = encoder_name_formatted

    hw_mapping_dict['button_matrix'] = 'button_matrix'

    mappings = {
        "HardwareInterface": hw_mapping_dict,
        "SessionRingComponent": {},
        "PageManager": {},
        "ModeManager": {},
        "CxpBridge": {},
        "ActionResolver": {},
        "ZManager": {},
        "EncoderManager": {},
        "ApiManager": {},
    }

    def add_plugin_mappings(plugin_dict):
        for plugin_name in plugin_dict.keys():
            mappings[plugin_name] = {}

    add_plugin_mappings(plugin_loader.hardware_plugins)
    add_plugin_mappings(plugin_loader.user_plugins)

    return mappings

def prepare_hardware_interface(button_names, encoder_names) -> Type[HardwareInterface]:
    _hardware_interface: Type[HardwareInterface] = HardwareInterface
    events = SUPPORTED_GESTURES

    for button_name in button_names:
        button_state = ZState()
        button_name_prefixed = f'_button_{button_name}'
        setattr(_hardware_interface, button_name_prefixed, button_state)
        _hardware_interface.named_button_states[button_name] = button_state

        for event in events:
            def create_handler(event, button_name_prefixed):
                def handler(self, button):
                    return self.handle_control_event(event, button)

                return handler

            handler_name = f"{button_name_prefixed}_{event}"
            handler = create_handler(event, button_name_prefixed)
            event_decorator = getattr(button_state, event)
            decorated_handler = event_decorator(handler)
            setattr(_hardware_interface, handler_name, decorated_handler)

    for encoder_name in encoder_names:
        encoder_state = EncoderState()
        encoder_name_prefixed = f'_encoder_{encoder_name}'
        setattr(_hardware_interface, encoder_name_prefixed, encoder_state)
        _hardware_interface.encoder_states[encoder_name] = encoder_state

        def create_handler(name):
            def handler(self, value, encoder):
                return self.handle_encoder_event(encoder_name, value)

            return handler

        handler_name = f"{encoder_name_prefixed}_value"
        handler = create_handler(encoder_name_prefixed)
        event_decorator = getattr(encoder_state, 'value')
        decorated_handler = event_decorator(handler)
        setattr(_hardware_interface, handler_name, decorated_handler)

    matrix_control = control_matrix(ZState)
    setattr(_hardware_interface, 'button_matrix', matrix_control)

    for event in events:
        def create_handler(event_type=event, name='button_matrix'):
            def handler(self, element):
                return self.handle_control_event(event_type, element)

            return handler

        handler_name = f"button_matrix_{event}"
        handler = create_handler()
        event_decorator = getattr(matrix_control, event)
        decorated_handler = event_decorator(handler)
        setattr(_hardware_interface, handler_name, decorated_handler)

    return _hardware_interface

class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    create_mappings_function = create_mappings

def create_instance(c_instance):
    global ROOT_LOGGER
    global plugin_loader
    global CONFIG_DIR
    global PREF_MANAGER
    this_dir = __name__.split('.')[0].lstrip('_')
    ROOT_LOGGER = logging.getLogger(this_dir)
    ROOT_LOGGER.setLevel(logging.INFO)

    dir_name = Path(__file__).parent.name
    canon_name = dir_name.lstrip('_')

    ROOT_LOGGER.info(f'{canon_name} starting...')

    log_filename = os.path.join(os.path.dirname(__file__), "log.txt")

    if not os.path.exists(log_filename):
        for handler in ROOT_LOGGER.handlers[:]:
            ROOT_LOGGER.removeHandler(handler)

    pref_manager = PreferenceManager(ROOT_LOGGER)
    prefs = pref_manager.user_prefs

    fallback_level = 'info'
    log_pref = prefs.get('log_level', fallback_level)
    try:
        log_level = getattr(logging, log_pref.upper())
    except AttributeError:
        ROOT_LOGGER.error(f'Invalid logging level `{log_pref}`, reverting to `info`')
        log_level = logging.INFO

    ROOT_LOGGER.setLevel(log_level)

    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == log_filename for h in ROOT_LOGGER.handlers):
        file_handler = logging.FileHandler(log_filename, mode="a")
        file_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # todo
        file_handler.setFormatter(formatter)

        ROOT_LOGGER.addHandler(file_handler)

    ROOT_LOGGER.debug(pref_manager.user_prefs)
    PREF_MANAGER = pref_manager

    CONFIG_DIR = pref_manager.config_dir

    plugin_loader = PluginLoader(logger=ROOT_LOGGER.getChild('PluginLoader'))

    Specification.component_map = {
        'HardwareInterface': HardwareInterface,
        'SessionRingComponent': SessionRing,
        'PageManager': PageManager,
        "ModeManager": ModeManager,
        'CxpBridge': CxpBridge,
        "ActionResolver": ActionResolver,
        "ZManager": ZManager,
        "EncoderManager": EncoderManager,
        "ApiManager": ApiManager,
    }

    def add_plugins_to_component_map(plugin_dict):
        for plugin_name, plugin_class in plugin_dict.items():
            if plugin_name in Specification.component_map:
                raise RuntimeError(f"Tried to register multiple plugins named '{plugin_name}'")
            Specification.component_map[plugin_name] = plugin_class

    add_plugins_to_component_map(plugin_loader.hardware_plugins)
    add_plugins_to_component_map(plugin_loader.user_plugins)

    # ClyphX Pro (sometimes) relies on class names to locate scripts
    # without this dynamic name, ClyphX can't differentiate between zcx scripts
    dynamically_named_core = type(canon_name, (ZCXCore,), {})

    try:
        return dynamically_named_core(Specification, c_instance=c_instance)

    except Exception as e:
        ROOT_LOGGER.info(e)
        raise
