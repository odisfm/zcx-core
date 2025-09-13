import unittest
from typing import TYPE_CHECKING
from tests.zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from z_control import ZControl


class TestColors(ZCXTestCase):

    def setUp(self):
        for mode in self._mode_manager.all_modes:
            self._mode_manager.remove_mode(mode)

    def test_all_controls_have_color(self):
        controls = self._z_manager.all_controls
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
        control: "ZControl" = self._z_manager.get_named_control("scene_1")
        color = control._color
        self._mode_manager.add_mode("shift")
        self.assertNotEqual(color, control._color)
        self.assertEqual(control._color_dict["attention"], control._color)
