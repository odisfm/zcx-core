import unittest
from typing import TYPE_CHECKING
from zcx_test_case import ZCXTestCase
from consts import NAMED_COLORS

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

    def test_parse_int_color(self):
        color_def = 50
        color_obj = self.zcx_api.create_color(color_def, None)
        self.assertEqual(color_def, color_obj.midi_value)

    def test_parse_named_colors(self):
        color_objs = []
        for color_name in NAMED_COLORS:
            color_obj = self.zcx_api.create_color(color_name, None)
            self.assertIsNotNone(color_obj)
            self.assertTrue(0 <= color_obj.midi_value <= 127)
            color_objs.append(color_obj)

        shade_1_color_objs = []
        for color_name in NAMED_COLORS:
            color_obj = self.zcx_api.create_color(f"{color_name} shade 1", None)
            self.assertIsNotNone(color_obj)
            self.assertTrue(0 <= color_obj.midi_value <= 127)
            shade_1_color_objs.append(color_obj)
            
        for i in range(len(NAMED_COLORS)):
            self.assertNotEqual(color_objs[i].midi_value, shade_1_color_objs[i].midi_value)

    def test_parse_animated_colors(self):
        green = self.zcx_api.create_color("green", None)
        red = self.zcx_api.create_color("red", None)
        pulse_test = self.zcx_api.create_color({"pulse": {"a": "green", "b": "red"}}, None)
        self.assertIsNotNone(pulse_test)
        self.assertEqual(pulse_test.color1.midi_value, green.midi_value)
        self.assertEqual(pulse_test.color2.midi_value, red.midi_value)
        blink_test = self.zcx_api.create_color({"blink": {"a": "green", "b": "red"}}, None)
        self.assertIsNotNone(blink_test)
        self.assertEqual(blink_test.color1.midi_value, green.midi_value)
        self.assertEqual(blink_test.color2.midi_value, red.midi_value)

        lazy_pulse_test = self.zcx_api.create_color({"pulse": "green"}, None)
        self.assertIsNotNone(lazy_pulse_test)
        self.assertEqual(lazy_pulse_test.color1.midi_value, green.midi_value)
        self.assertEqual(lazy_pulse_test.color2.midi_value, green.midi_value)

        lazy_blink_test = self.zcx_api.create_color({"blink": "green"}, None)
        self.assertIsNotNone(lazy_blink_test)
        self.assertEqual(lazy_blink_test.color1.midi_value, green.midi_value)
        self.assertEqual(lazy_blink_test.color2.midi_value, 0)
