import unittest
from typing import TYPE_CHECKING
from tests.zcx_test_case import ZCXTestCase


class TestClyphXPro(ZCXTestCase):

    def test_cxp_actions(self):
        try:
            self._cxp_bridge.trigger_action_list("DUMMY")
        except RuntimeError:
            self.fail("CxpBridge.trigger_action_list() raised RuntimeError")
