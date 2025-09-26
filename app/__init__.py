from ableton.v3.control_surface import (
    ControlSurfaceSpecification,
    create_skin
)

ROOT_LOGGER = None
NAMED_BUTTONS = None
ENCODERS = None
PLAYABLE = False
CONFIG_DIR = '_config'
SAFE_MODE = True
PREF_MANAGER = None

plugin_loader: 'Optional[PluginLoader]' = None

def create_mappings(arg) -> dict:
    from .elements import Elements
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
    if PLAYABLE:
        hw_mapping_dict['playable_matrix'] = 'playable_matrix'

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
        "SessionView": {},
        "TestRunner": {},
        "ViewManager": {},
        "MelodicComponent": {},
    }

    def add_plugin_mappings(plugin_dict):
        for plugin_name in plugin_dict.keys():
            mappings[plugin_name] = {}

    add_plugin_mappings(plugin_loader.hardware_plugins)
    add_plugin_mappings(plugin_loader.user_plugins)

    return mappings

def prepare_hardware_interface(button_names, encoder_names) -> "Type[HardwareInterface]":
    from .hardware_interface import HardwareInterface
    from .encoder_state import EncoderState
    from .z_state import ZState
    from .consts import SUPPORTED_GESTURES

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

        def create_handler(encoder_name_prefixed):
            def handler(self, value, encoder):
                return self.handle_encoder_event(encoder_name, value)

            return handler

        handler_name = f"{encoder_name_prefixed}_value"
        handler = create_handler(encoder_name_prefixed)
        event_decorator = getattr(encoder_state, 'value')
        decorated_handler = event_decorator(handler)
        setattr(_hardware_interface, handler_name, decorated_handler)

    from ableton.v3.control_surface.controls import (
        control_matrix,
    )

    matrix_control = control_matrix(ZState)
    setattr(_hardware_interface, 'button_matrix', matrix_control)
    if PLAYABLE:
        from .playable.playable_state import PlayableState
        playable_matrix = control_matrix(PlayableState)
        setattr(_hardware_interface, 'playable_matrix', playable_matrix)

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
    from .elements import Elements
    from .skin import Skin
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    create_mappings_function = create_mappings

def create_instance(c_instance):
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    from pathlib import Path
    from typing import Type
    from .preference_manager import PreferenceManager
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

    has_rotating_handler = any(
        isinstance(h, RotatingFileHandler) and h.baseFilename == log_filename
        for h in ROOT_LOGGER.handlers
    )

    if not has_rotating_handler:
        for handler in ROOT_LOGGER.handlers[:]:
            if isinstance(handler, logging.FileHandler) and handler.baseFilename == log_filename:
                ROOT_LOGGER.removeHandler(handler)
                handler.close()

        file_handler = RotatingFileHandler(
            log_filename,
            mode="a",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=0,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        ROOT_LOGGER.addHandler(file_handler)

        if os.path.exists(log_filename):
            file_size = os.path.getsize(log_filename)
            if file_size >= 5 * 1024 * 1024:
                ROOT_LOGGER.info("Log file over size limit, rotating...")
                file_handler.doRollover()

    ROOT_LOGGER.debug(pref_manager.user_prefs)
    PREF_MANAGER = pref_manager

    CONFIG_DIR = pref_manager.config_dir

    from .action_resolver import ActionResolver
    from .api_manager import ApiManager
    from .cxp_bridge import CxpBridge
    from .encoder_manager import EncoderManager
    from .hardware_interface import HardwareInterface
    from .mode_manager import ModeManager
    from .page_manager import PageManager
    from .plugin_loader import PluginLoader
    from .z_manager import ZManager
    from .zcx_core import ZCXCore
    from .session_ring import SessionRing
    from .session_view import SessionView
    from .test_runner import TestRunner
    from .view_manager import ViewManager
    from .playable.melodic_component import MelodicComponent

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
        "SessionView": SessionView,
        "TestRunner": TestRunner,
        "ViewManager": ViewManager,
        "MelodicComponent": MelodicComponent,
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