import unittest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zcx_core import ZCXCore
    from z_manager import ZManager
    from pad_section import PadSection
    from page_manager import PageManager
    from mode_manager import ModeManager
    from encoder_manager import EncoderManager
    from z_encoder import ZEncoder


class TestWithSet(unittest.TestCase):

    _zcx: "ZCXCore"

    @classmethod
    def setUpClass(cls) -> None:
        cls.encoder_manager: "EncoderManager" = cls._zcx.component_map["EncoderManager"]
        cls.mode_manager: "ModeManager" = cls._zcx.component_map["ModeManager"]
        cls.song = cls._zcx.song

    def setUp(self):
        if not str(self.song.name).startswith("zcx test set"):
            self.skipTest("Set is not called `zcx test set.als`")
        self._zcx._session_ring_custom.go_to_scene(0)
        self._zcx._session_ring_custom.go_to_track(0)

    def test_ring_encoders(self):
        encoders = []
        for i in range(1, 8):
            encoders.append(self._zcx.zcx_api.get_encoder(f"enc_{i}"))

        actual_tracks = list(self.song.tracks)[:7]
        ring_tracks = []

        for i in range(0, 7):
            ring_tracks.append(self._zcx._session_ring_custom.get_ring_track(i))

        def test_correct_tracks():
            for j in range(len(actual_tracks)):
                self.assertEqual(actual_tracks[j], ring_tracks[j])

        test_correct_tracks()

        for i in range(len(actual_tracks)):
            param = encoders[i]._mapped_parameter
            self.assertEqual(param.canonical_parent.canonical_parent, actual_tracks[i])
            self.assertEqual(param.name, "Track Volume")

        self.mode_manager.add_mode("shift")

        test_correct_tracks()

        for encoder in encoders:
            param = encoder._mapped_parameter
            self.assertEqual(param.name, "Track Panning")
