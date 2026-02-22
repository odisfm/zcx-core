from typing import TYPE_CHECKING
from zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from z_controls.session_clip_control import SessionClipControl


class TestSessionView(ZCXTestCase):

    def setUp(self):
        super().setUp()
        self._page_manager.set_page(page_name="session_view_page")
        self.pad_section = self._session_view.pad_section
        self.owned_controls: "list[SessionClipControl]" = self.pad_section.owned_controls
        self._session_ring.go_to_track(0)
        self._session_ring.go_to_scene(0)

    def test_session_view_clip_assign(self):
        for control in self.owned_controls:
            self.assertIsNotNone(control.clip_slot)

    def test_gesture(self):
        self._mode_manager.add_mode("select")
        for i, control in enumerate(self.owned_controls):
            command = control.handle_gesture("pressed", True)[0]
            parsed = self._action_resolver._compile_and_check(command, control._vars, control._context)
            self.assertIsNotNone(parsed)
            control.handle_gesture("pressed", testing=True)
            # self.log(f"control clip slot track {control.clip_slot.canonical_parent.name} slot {list(control.clip_slot.canonical_parent.clip_slots).index(control.clip_slot)}")
            # self.log(f"highlighted clip slot track {self.song.view.highlighted_clip_slot.canonical_parent.name} slot {list(self.song.view.highlighted_clip_slot.canonical_parent.clip_slots).index(self.song.view.highlighted_clip_slot)}")

            self.assertEqual(control.clip_slot, self.song.view.highlighted_clip_slot, f"control {i}")

    def test_ring_integration(self):
        first_row_controls = self.owned_controls[:8]
        def do_test():
            scene_offset = self._session_ring.scene_offset
            for i, control in enumerate(first_row_controls):
                self.assertEqual(control.clip_slot.canonical_parent, self._session_ring.get_ring_track(i))
                clip_slot_idx = list(control.clip_slot.canonical_parent.clip_slots).index(control.clip_slot)
                self.assertEqual(scene_offset, clip_slot_idx)

        do_test()

        self._session_ring.go_to_track(1000)
        self._session_ring.go_to_scene(1000)

        do_test()

