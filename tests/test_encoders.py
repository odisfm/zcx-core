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
        if not self._is_using_test_set:
            self.skipTest("Not using test set")

        encoder_group = self.zcx_api.get_encoder_group("best_of_bank_test")
        self.assertIsNotNone(encoder_group)

        track = self.get_track_by_name("analog")
        assert track is not None
        eq_8_dev = self.get_device_by_name(device_name="EQ Eight", device_class_name=None, device_list=track.devices)
        self.song.view.select_device(eq_8_dev)
        self.song.view.selected_track = track

        eq_8_expected_names = [
            '1 Frequency A', '1 Gain A', '2 Frequency A', '2 Gain A', '3 Frequency A', '3 Gain A', '4 Frequency A', '4 Gain A',
            '1 Filter On A', '2 Filter On A', '3 Filter On A', '4 Filter On A', '5 Filter On A', '6 Filter On A', '7 Filter On A', '8 Filter On A'
        ]

        for i, enc in enumerate(encoder_group):
            expected_name = eq_8_expected_names[i]
            self.assertIsNotNone(enc._mapped_parameter, f"{enc._name} param is None")
            self.assertEqual(enc._mapped_parameter.name, expected_name, f"{enc._name} (param i)")



