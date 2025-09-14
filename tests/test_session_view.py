from typing import TYPE_CHECKING
from tests.zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from z_controls.session_clip_control import SessionClipControl


class TestSessionView(ZCXTestCase):

    def setUp(self):
        self.pad_section = self._session_view.pad_section
        self.owned_controls: "list[SessionClipControl]" = self.pad_section.owned_controls

    def test_session_view_clip_assign(self):
        for control in self.owned_controls:
            self.assertIsNotNone(control.clip_slot)

