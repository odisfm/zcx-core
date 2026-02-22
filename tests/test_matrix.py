import unittest
from typing import TYPE_CHECKING
from zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from pad_section import PadSection


class TestMatrix(ZCXTestCase):

    def setUp(self):
        self.blank_section: "PadSection" = self._z_manager.get_matrix_section("blank_section")

    def test_coords(self):
        control1 = self.blank_section.owned_controls[0]
        self.assertEqual(control1.coordinates, "x0y0")
        big_x = control1.context["me"]["X"]
        big_y = control1.context["me"]["Y"]
        self.assertEqual(big_x, 1)
        self.assertEqual(big_y, 1)

        control2 = self.blank_section.owned_controls[34]
        self.assertEqual(control2.coordinates, "x2y4")
        flip_x = control2.context["me"]["x_flip"]
        flip_y = control2.context["me"]["y_flip"]
        self.assertEqual(flip_x, 5)
        self.assertEqual(flip_y, 3)

        control3 = self.blank_section.owned_controls[-1]
        self.assertEqual(control3.coordinates, "x7y7")

