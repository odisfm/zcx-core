import unittest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zcx_core import ZCXCore


class TestRootCSBasics(unittest.TestCase):

    _zcx: "ZCXCore"

    def test_enabled(self):
        self.assertTrue(self._zcx._enabled)

    def test_cs_name(self):
        self.assertEqual(self._zcx.name, "zcx_test")

    def test_api(self):
        self.assertTrue(self._zcx.zcx_api)
