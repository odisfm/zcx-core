import unittest
from typing import TYPE_CHECKING
from zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from zcx_core import ZCXCore


class TestRootCSBasics(ZCXTestCase):

    def test_enabled(self):
        self.assertTrue(self.zcx._enabled)

    def test_cs_name(self):
        self.assertEqual(self.zcx.name, "zcx_test")

    def test_api(self):
        self.assertTrue(self.zcx.zcx_api)
