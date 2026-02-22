import time

from zcx_test_case import ZCXTestCase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from z_controls.page_control import PageControl
    from z_controls.track_control import TrackControl
    from z_controls.ring_track_control import RingTrackControl
    from z_controls.param_control import ParamControl

class TestStandardControls(ZCXTestCase):

    pass

class TestPageControls(ZCXTestCase):

    def setUp(self):
        self._page_manager.set_page(0)

    def test_page_control_group(self):
        controls: "list[PageControl]" = self._z_manager.get_control_group("page_control_test_1")
        self.assertIsNotNone(controls)
        page_names = self._page_manager.all_page_names
        for i in range(len(controls)):
            try:
                control = controls[i]
                page_name = page_names[i]
                self.assertEqual(page_name, control._context["me"]["page_name"])
                control.handle_gesture("pressed", testing=True)
                self.assertEqual(i, self._page_manager.current_page)
                self.assertEqual(page_name, self._page_manager.all_page_names[self._page_manager.current_page])
            except IndexError:
                pass

        for i in range(len(controls)):
            try:
                control = controls[i]
                page_name = page_names[i]
                self.assertEqual(i, control._context["me"]["page"])
                control.handle_gesture("double_clicked", testing=True)
                self.assertEqual(i, self._page_manager.current_page)
            except IndexError:
                pass

class TestRingTrackControls(ZCXTestCase):

    def setUp(self):
        self.assertUsingTestSet()
        self._session_ring.go_to_track(0)
        self._session_ring.go_to_scene(0)

    def test_ring_track_control_group(self):
        controls: "list[RingTrackControl]" = self._z_manager.get_control_group("ring_track_control_test_1")

        def do_test():
            for i in range(len(controls)):
                control = controls[i]
                ring_track = self._session_ring.get_ring_track(i)
                self.assertEqual(ring_track, control.track, f"ring track: {ring_track.name}, control track: {control.track.name}")
                control.handle_gesture("pressed", testing=True)
                self.assertEqual(self.song.view.selected_track, control.track)

        do_test()
        self._session_ring.move(x=8)
        do_test()
        self._session_ring.move(x=-3)
        do_test()
        self._session_ring.move(x=10000)
        do_test()
        self._session_ring.move(y=10000)
        do_test()

class TestTrackControls(ZCXTestCase):

    def setUp(self):
        self.assertUsingTestSet()

    def test_track_control_group(self):
        controls: "list[TrackControl]" = self._z_manager.get_control_group("track_control_test_1")
        tracklist = list(self.song.tracks)

        for i, control in enumerate(controls):
            self.assertEqual(control.track, tracklist[i])
            control.handle_gesture("pressed", testing=True)
            self.assertEqual(self.song.view.selected_track, control.track)
