import unittest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zcx_core import ZCXCore
    from z_manager import ZManager
    from pad_section import PadSection
    from page_manager import PageManager
    from mode_manager import ModeManager
    from encoder_manager import EncoderManager
    from z_control import ZControl


class TestColors(unittest.TestCase):

    _zcx: "ZCXCore"

    @classmethod
    def setUpClass(cls) -> None:
        cls.z_manager: "ZManager" = cls._zcx.component_map["ZManager"]
        cls.mode_manager: "ModeManager" = cls._zcx.component_map["ModeManager"]
        cls.song = cls._zcx.song

    def setUp(self):
        for mode in self.mode_manager.all_modes:
            self.mode_manager.remove_mode(mode)

    def test_all_controls_have_color(self):
        controls = self.z_manager.all_controls
        for control in controls:
            color = control._color
            self.assertIsNotNone(color)
            try:
                midi_val = color.midi_value
                self.assertIsInstance(midi_val, int)
                self.assertTrue(0 <= midi_val <= 127)
            except NotImplementedError: # animated colors throw when accessing their midi_value
                color_1 = color.color1.midi_value
                self.assertIsInstance(color_1, int)
                self.assertTrue(0 <= color_1 <= 127)
                color_2 = color.color2.midi_value
                self.assertIsInstance(color_2, int)
                self.assertTrue(0 <= color_2 <= 127)

    def test_attention_animation(self):
        control: "ZControl" = self.z_manager.get_named_control("scene_1")
        color = control._color
        self.mode_manager.add_mode("shift")
        self.assertNotEqual(color, control._color)
        self.assertEqual(control._color_dict["attention"], control._color)
