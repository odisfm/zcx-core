import unittest
from typing import TYPE_CHECKING
from tests.zcx_test_case import ZCXTestCase

if TYPE_CHECKING:
    from pad_section import PadSection
    from z_encoder import ZEncoder


class TestEncoders(ZCXTestCase):

    def setUp(self):
        for mode in self._mode_manager.all_modes:
            self._mode_manager.remove_mode(mode)

    def test_encoder_simple(self):
        enc: "ZEncoder" = self._encoder_manager.get_encoder("enc_master")
        param = enc._mapped_parameter
        self.assertTrue(param)
        track = param.canonical_parent.canonical_parent
        self.assertEqual(track, self.song.master_track)
        self.assertEqual(param.name, "Track Volume")

        self._mode_manager.add_mode("shift")
        self.assertEqual(track, self.song.master_track)
        param = enc._mapped_parameter
        self.assertEqual(param.name, "Preview Volume")

    def test_best_of_bank(self):
        pass
