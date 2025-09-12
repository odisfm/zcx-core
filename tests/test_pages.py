import unittest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zcx_core import ZCXCore
    from page_manager import PageManager


class TestPages(unittest.TestCase):

    _zcx: "ZCXCore"

    def setUp(self):
        self.page_manager: "PageManager" = self._zcx.component_map["PageManager"]
        self.page_manager.set_page(page_number=0)

    def test_initial_page(self):
        self.assertEqual(self.page_manager.current_page, 0)

    def test_page_increment(self):
        page_num = self.page_manager.current_page
        self.page_manager.increment_page(1)
        self.assertEqual(self.page_manager.current_page, page_num + 1)
        self.page_manager.increment_page(-1)
        self.assertEqual(self.page_manager.current_page, page_num)

    def test_navigate_to_page_name(self):
        all_pages = self.page_manager.all_page_names
        self.page_manager.set_page(page_name=all_pages[1])
        self.assertEqual(self.page_manager.current_page, 1)
