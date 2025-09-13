import unittest
from typing import Any, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from action_resolver import ActionResolver
    from api_manager import ApiManager, ZcxApi
    from cxp_bridge import CxpBridge
    from encoder_element import EncoderElement
    from hardware_interface import HardwareInterface
    from encoder_state import EncoderState
    from mode_manager import ModeManager
    from pad_section import PadSection
    from page_manager import PageManager
    from plugin_loader import PluginLoader
    from preference_manager import PreferenceManager
    from session_ring import SessionRing
    from session_view import SessionView
    from template_manager import TemplateManager
    from z_control import ZControl
    from z_encoder import ZEncoder
    from z_element import ZElement
    from z_state import ZState
    from z_manager import ZManager
    from zcx_component import ZCXComponent
    from zcx_core import ZCXCore


class ZCXTestCase(unittest.TestCase):

    zcx: "ZCXCore"
    component_map: "dict[str, ZCXComponent]"
    _is_using_test_set = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls) -> None:
        cls._action_resolver: "ActionResolver" = cls.zcx.component_map["ActionResolver"]
        cls._api_manager: "ApiManager" = cls.zcx.component_map["ApiManager"]
        cls._cxp_bridge: "CxpBridge" = cls.zcx.component_map["CxpBridge"]
        cls._encoder_manager: "EncoderManager" = cls.zcx.component_map["EncoderManager"]
        cls._hardware_interface: "HardwareInterface" = cls.zcx.component_map["HardwareInterface"]
        cls._mode_manager: "ModeManager" = cls.zcx.component_map["ModeManager"]
        cls._page_manager: "PageManager" = cls.zcx.component_map["PageManager"]
        cls._session_ring: "SessionRing" = cls.zcx._session_ring_custom
        cls._session_view: "SessionView" = cls.zcx.component_map["SessionView"]
        cls._z_manager: "ZManager" = cls.zcx.component_map["ZManager"]
        cls.zcx_api: "ZcxApi" = cls.zcx.zcx_api
