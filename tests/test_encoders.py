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


class TestEncoders(unittest.TestCase):

    _zcx: "ZCXCore"

    @classmethod
    def setUpClass(cls) -> None:
        cls.encoder_manager: "EncoderManager" = cls._zcx.component_map["EncoderManager"]
        cls.mode_manager: "ModeManager" = cls._zcx.component_map["ModeManager"]
        cls.song = cls._zcx.song

    def setUp(self):
        for mode in self.mode_manager.all_modes:
            self.mode_manager.remove_mode(mode)

    def test_encoder_simple(self):
        enc: "ZEncoder" = self.encoder_manager.get_encoder("enc_master")
        param = enc._mapped_parameter
        self.assertTrue(param)
        track = param.canonical_parent.canonical_parent
        self.assertEqual(track, self.song.master_track)
        self.assertEqual(param.name, "Track Volume")

        self.mode_manager.add_mode("shift")
        self.assertEqual(track, self.song.master_track)
        param = enc._mapped_parameter
        self.assertEqual(param.name, "Preview Volume")

