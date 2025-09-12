import unittest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zcx_core import ZCXCore
    from page_manager import PageManager


class TestPages(unittest.TestCase):

    _zcx: "ZCXCore"

    def setUp(self):
        self.page_manager: "PageManager" = self._zcx.component_map["PageManager"]

    def test_initial_page(self):
        self.assertEqual(self.page_manager.current_page, 0)
