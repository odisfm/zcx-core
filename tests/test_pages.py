import unittest
from typing import TYPE_CHECKING
from tests.zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from zcx_core import ZCXCore
    from page_manager import PageManager


class TestPages(ZCXTestCase):

    def setUp(self):
        self._page_manager.set_page(page_number=0)

    def test_initial_page(self):
        self.assertEqual(self._page_manager.current_page, 0)

    def test_page_increment(self):
        page_num = self._page_manager.current_page
        self._page_manager.increment_page(1)
        self.assertEqual(self._page_manager.current_page, page_num + 1)
        self._page_manager.increment_page(-1)
        self.assertEqual(self._page_manager.current_page, page_num)

    def test_navigate_to_page_name(self):
        all_pages = self._page_manager.all_page_names
        self._page_manager.set_page(page_name=all_pages[1])
        self.assertEqual(self._page_manager.current_page, 1)
