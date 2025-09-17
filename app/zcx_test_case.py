import unittest
from typing import Any, TYPE_CHECKING, TypedDict, Iterable

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

    def setUp(self) -> None:
        for mode in self._mode_manager.all_modes:
            self._mode_manager.remove_mode(mode)

    @classmethod
    def get_track_by_name(cls, name: str):
        tracklist = list(cls.song.tracks)
        for track in tracklist:
            if track.name == name:
                return track
        return None

    @classmethod
    def is_rack_device(cls, device):
        return device.class_name in ['AudioEffectGroupDevice', 'MidiEffectGroupDevice', 'InstrumentGroupDevice']

    @classmethod
    def get_device_by_name(cls, device_name: str, device_class_name: None, device_list: Iterable[Any]):
        for device in device_list:
            if device_class_name and device.class_name == device_class_name:
                return device
            if device.name == device_name:
                return device
            if cls.is_rack_device(device):
                chains = device.chains
                for chain in chains:
                    return cls.get_device_by_name(device_name, device_class_name, chain.devices)
        return None

    @classmethod
    def get_track_for_device(cls, device):
        parent = device.canonical_parent
        if parent.__class__.__name__ == "Track":
            return parent
        else:
            return cls.get_track_for_device(parent)

    def assertUsingTestSet(self):
        if not self._is_using_test_set:
            self.skipTest("Test set is not loaded")
