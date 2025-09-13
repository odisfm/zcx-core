import unittest
from typing import TYPE_CHECKING
from tests.zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from pad_section import PadSection
    from z_encoder import ZEncoder


class TestWithSet(ZCXTestCase):

    def setUp(self):
        if not self._is_using_test_set:
            self.skipTest("Test set is not loaded")
        self._session_ring.go_to_scene(0)
        self._session_ring.go_to_track(0)

    def test_ring_encoders(self):
        encoders = []
        for i in range(1, 8):
            encoders.append(self.zcx_api.get_encoder(f"enc_{i}"))

        actual_tracks = list(self.song.tracks)[:7]
        ring_tracks = []

        for i in range(0, 7):
            ring_tracks.append(self._session_ring.get_ring_track(i))

        def test_correct_tracks():
            for j in range(len(actual_tracks)):
                self.assertEqual(actual_tracks[j], ring_tracks[j])

        test_correct_tracks()

        for i in range(len(actual_tracks)):
            param = encoders[i]._mapped_parameter
            self.assertEqual(param.canonical_parent.canonical_parent, actual_tracks[i])
            self.assertEqual(param.name, "Track Volume")

        self._mode_manager.add_mode("shift")

        test_correct_tracks()

        for encoder in encoders:
            param = encoder._mapped_parameter
            self.assertEqual(param.name, "Track Panning")
