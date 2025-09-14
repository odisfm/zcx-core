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
        self.assertUsingTestSet()

        encoder_group = self.zcx_api.get_encoder_group("best_of_bank_test")
        self.assertIsNotNone(encoder_group)

        def bulk_check_param_names(_encoders: "list[ZEncoder]", expected_names):
            for i, _enc in enumerate(_encoders):
                expected_name = expected_names[i]
                _enc.bind_to_active()
                if expected_name is not None:
                    self.assertIsNotNone(_enc._mapped_parameter, f"{_enc._name} param is None")
                    self.assertEqual(_enc._mapped_parameter.name, expected_name, f"{_enc._name} (param {i})")
                else:
                    self.log(f'should be mapped to `{expected_name}`, is mapped to {_enc._mapped_parameter.__class__.__name__}.')
                    self.assertIs(_enc._mapped_parameter, None)
            return True

        track = self.get_track_by_name("analog")
        assert track is not None
        eq_8_dev = self.get_device_by_name(device_name="EQ Eight", device_class_name=None, device_list=track.devices)
        assert eq_8_dev is not None
        self.song.view.select_device(eq_8_dev)
        self.song.view.selected_track = track
        assert self.song.view.selected_track == track

        eq_8_expected_names = [
            '1 Frequency A', '1 Gain A', '2 Frequency A', '2 Gain A', '3 Frequency A', '3 Gain A', '4 Frequency A', '4 Gain A',
            '1 Filter On A', '2 Filter On A', '3 Filter On A', '4 Filter On A', '5 Filter On A', '6 Filter On A', '7 Filter On A', '8 Filter On A'
        ]


        bulk_check_param_names(encoder_group, eq_8_expected_names)

        comp_dev = self.get_device_by_name(device_name="Compressor", device_class_name=None, device_list=track.devices)
        assert comp_dev is not None
        self.song.view.select_device(comp_dev)
        assert track.view.selected_device == comp_dev

        comp_dev_expected_names = [
            "Threshold", "Ratio", "Model", "Knee", "Attack", "Release", "Dry/Wet", "Output Gain",
            "S/C On", "S/C Gain", "S/C Mix", "S/C Listen", "S/C EQ On", "S/C EQ Type", "S/C EQ Freq", "S/C EQ Q"
        ]
        bulk_check_param_names(encoder_group, comp_dev_expected_names)

        grain_delay = self.get_device_by_name(device_name="Grain Delay", device_class_name=None, device_list=track.devices)
        assert grain_delay is not None
        self.song.view.select_device(grain_delay)
        assert track.view.selected_device == grain_delay

        grain_delay_expected_names = [
            "Frequency", "Pitch", "Delay Mode", "Beat Delay", "Random", "Spray", "Feedback", "DryWet",
            "Delay Mode", "Beat Delay", "Beat Swing", "Feedback", None, None, None, "DryWet"
        ]

        bulk_check_param_names(encoder_group, grain_delay_expected_names)

        grain_delay_expected_names = [
            "Frequency", "Pitch", "Delay Mode", "Beat Delay", "Random", "Spray", "Feedback", "DryWet",
            "Delay Mode", "Beat Delay", "Beat Swing", "Feedback", "DryWet", None, None, None
        ]

        for enc in encoder_group:
            enc._prefer_left = True

        bulk_check_param_names(encoder_group, grain_delay_expected_names)

    def test_ring_encoders(self):
        self.assertUsingTestSet()

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

