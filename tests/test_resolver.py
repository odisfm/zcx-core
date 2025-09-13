import unittest
from typing import TYPE_CHECKING
from tests.zcx_test_case import ZCXTestCase


class TestResolver(ZCXTestCase):

    def test_resolve(self):
        context = {"me": {"message": "Hello"}}
        test_str = "${me.message}, world!"
        parsed, status = self._action_resolver.compile(test_str, {}, context)
        self.assertEqual(status, 0)
        self.assertEqual(parsed, "Hello, world!")
