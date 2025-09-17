import unittest
from typing import TYPE_CHECKING
from zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from pad_section import PadSection


class TestTemplates(ZCXTestCase):

    def setUp(self):
        self.test_section_1: "PadSection" = self._z_manager.get_matrix_section("test_section_1")

    def test_global_template(self):
        control = self.test_section_1.owned_controls[3]
        self.assertTrue(control._context["me"]["props"]["global_template"])
        self.assertEqual(control._on_threshold, 20)
        self.assertEqual(control._color.midi_value, 127)

    def test_stacked_template(self):
        control = self.test_section_1.owned_controls[4]
        self.assertEqual(control._color.midi_value, 3)
        gestures = control._gesture_dict
        self.assertEqual(gestures["pressed"], "control_def")
        self.assertEqual(gestures["released"], "test_1")
        self.assertEqual(gestures["released_delayed"], "control_def")
        self.assertEqual(gestures["double_clicked"], "test_2")
        self.assertTrue(control._context["me"]["props"]["test_1"])
        self.assertTrue(control._context["me"]["props"]["test_2"])
        self.assertTrue(control._context["me"]["props"]["control_def"])

    def test_null_template(self):
        control = self.test_section_1.owned_controls[5]
        def get_test_prop(ctr):
            return ctr._context["me"]["props"]["global_template"]
        self.assertRaises(KeyError, lambda: get_test_prop(control))

        control_2 = self.test_section_1.owned_controls[6]
        self.assertRaises(KeyError, lambda: get_test_prop(control_2))
        self.assertTrue(control_2._context["me"]["props"]["test_1"])
