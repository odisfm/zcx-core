import unittest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zcx_core import ZCXCore
    from action_resolver import ActionResolver


class TestResolver(unittest.TestCase):

    _zcx: "ZCXCore"


    def setUp(self):
        self.action_resolver: "ActionResolver" = self._zcx.component_map["ActionResolver"]

    def test_resolve(self):
        context = {"me": {"message": "Hello"}}
        test_str = "${me.message}, world!"
        parsed, status = self.action_resolver.compile(test_str, {}, context)
        self.assertEqual(status, 0)
        self.assertEqual(parsed, "Hello, world!")
