import unittest
from typing import TYPE_CHECKING
from zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from pad_section import PadSection


class TestGestures(ZCXTestCase):

    def setUp(self):
        self.test_section_1: "PadSection" = self._z_manager.get_matrix_section("test_section_1")
        self._page_manager.set_page(page_name="test_page_1")

    def tearDown(self):
        all_modes = self._mode_manager.all_modes
        for mode in all_modes:
            self._mode_manager.remove_mode(mode)

    def test_basic_gestures(self):
        test_control = self.test_section_1.owned_controls[0]
        self.assertEqual(test_control.handle_gesture("pressed", dry_run=True)[0], "pressed")
        self.assertEqual(test_control.handle_gesture("pressed_delayed", dry_run=True)[0], "pressed_delayed")
        self.assertEqual(test_control.handle_gesture("released", dry_run=True)[0], "released")
        self.assertEqual(test_control.handle_gesture("released_delayed", dry_run=True)[0], "released_delayed")
        self.assertEqual(test_control.handle_gesture("released_immediately", dry_run=True)[0], "released_immediately")
        self.assertEqual(test_control.handle_gesture("double_clicked", dry_run=True)[0], "double_clicked")

    def test_mode_gestures(self):
        test_control = self.test_section_1.owned_controls[1]
        self.assertEqual(test_control.handle_gesture("pressed", dry_run=True)[0], "pressed")
        self._mode_manager.add_mode("shift")
        self.assertEqual(test_control.handle_gesture("pressed", dry_run=True)[0], "pressed__shift")
        self._mode_manager.add_mode("select")
        self.assertEqual(test_control.handle_gesture("pressed", dry_run=True)[0], "pressed__shift__select")
        self._mode_manager.remove_mode("shift")
        self.assertEqual(test_control.handle_gesture("pressed", dry_run=True)[0], "pressed__select")

    def test_cascading_gestures(self):
        test_control = self.test_section_1.owned_controls[2]
        self._mode_manager.add_mode("test_1")
        self._mode_manager.add_mode("test_2")
        self.assertEqual(test_control.handle_gesture("pressed", dry_run=True),
                         ["pressed", "test_1", "test_2"]
                         )
        test_control._cascade_direction = "up"
        self.assertEqual(test_control.handle_gesture("pressed", dry_run=True),
                         ["test_2", "test_1", "pressed"]
                         )
