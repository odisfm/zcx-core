from typing import Any
from tests.zcx_test_case import ZCXTestCase
from parse_target_path import parse_target_path


class TestTargetPathParser(ZCXTestCase):

    def check_valid_result(self, result: dict[str, Any] = None, assertions: list[tuple[str, Any]] = None) -> None:
        asserted_keys = []
        for assertion in assertions:
            if assertion[1] is True:
                self.assertTrue(result[assertion[0]])
            else:
                self.assertEqual(result[assertion[0]], assertion[1], result)
            asserted_keys.append(assertion[0])

        for key, value in result.items():
            if key in asserted_keys or key == "input_string":
                continue
            self.assertFalse(value, f"{key} should be falsy\n{result}")


    def test_parse_simple_paths(self):
        self.check_valid_result(
            parse_target_path("SEL / VOL"),
            [
                ("track", "SEL"),
                ("parameter_type", "VOL")
            ]
        )
        self.check_valid_result(
            parse_target_path('"my cool track" / VOL'),
            [
                ("track", "my cool track"),
                ("parameter_type", "VOL")
            ]
        )
        self.check_valid_result(
            parse_target_path('"my cool track" / PAN'),
            [
                ("track", "my cool track"),
                ("parameter_type", "PAN")
            ]
        )
        self.check_valid_result(
            parse_target_path('1 / SEND F'),
            [
                ("track", "1"),
                ("parameter_type", "SEND"),
                ("send", "F")
            ]
        )
        self.check_valid_result(
            parse_target_path('1 / PANL'),
            [
                ("track", "1"),
                ("parameter_type", "PANL"),
            ]
        )
        self.check_valid_result(
            parse_target_path('1 / PANR'),
            [
                ("track", "1"),
                ("parameter_type", "PANR"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SELP'),
            [
                ("parameter_type", "SELP"),
            ]
        )
        self.check_valid_result(
            parse_target_path('1 / DEV(SEL) CS'),
            [
                ("track", "1"),
                ("device", "SEL"),
                ("parameter_type", "CS"),
            ]
        )
        self.check_valid_result(
            parse_target_path('"my cool track" / DEV(1) P40'),
            [
                ("track", "my cool track"),
                ("device", "1"),
                ("parameter_number", "40"),
            ]
        )
        self.check_valid_result(
            parse_target_path('"my cool track" / DEV("my device") "my param"'),
            [
                ("track", "my cool track"),
                ("device", "my device"),
                ("parameter_name", "my param"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / DEV(SEL) B1 P2'),
            [
                ("track", "SEL"),
                ("device", "SEL"),
                ("bank", "1"),
                ("parameter_number", "2"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / DEV(1.1) PAN'),
            [
                ("track", "SEL"),
                ("chain_map", ["1", "1"]),
                ("parameter_type", "PAN"),
            ]
        )
        # self.check_valid_result(
        #     parse_target_path('SEL / DEV(1."my chain") PAN'),
        #     [
        #         ("track", "SEL"),
        #         ("chain_map", ["my rack", "my chain"]),
        #         ("parameter_type", "PAN"),
        #     ]
        # )
        self.check_valid_result(
            parse_target_path('SEL / DEV(1.1) SEND A'),
            [
                ("track", "SEL"),
                ("chain_map", ["1", "1"]),
                ("parameter_type", "SEND"),
                ("send", "A"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / DEV(1.1) VOL'),
            [
                ("track", "SEL"),
                ("chain_map", ["1", "1"]),
                ("parameter_type", "VOL"),
            ]
        )
        # self.check_valid_result(
        #     parse_target_path('XFADER'),
        #     [
        #         ("parameter_type", "XFADER"),
        #     ]
        # )
        self.check_valid_result(
            parse_target_path('RING(0) / VOL'),
            [
                ("ring_track", "0"),
                ("parameter_type", "VOL"),
            ]
        )

    def test_parse_additional_paths(self):
        self.check_valid_result(
            parse_target_path('SEL / DEV(1)'),
            [
                ("track", "SEL"),
                ("device", "1"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / DEV(1) SEL'),
            [
                ("track", "SEL"),
                ("device", "1"),
                ("parameter_type", "SEL"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / SEL'),
            [
                ("track", "SEL"),
                ("track_select", True),
                ("parameter_type", "SEL"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / ARM'),
            [
                ("track", "SEL"),
                ("arm", True),
                ("parameter_type", "ARM"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / MUTE'),
            [
                ("track", "SEL"),
                ("mute", True),
                ("parameter_type", "MUTE"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / SOLO'),
            [
                ("track", "SEL"),
                ("solo", True),
                ("parameter_type", "SOLO"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / MON IN'),
            [
                ("track", "SEL"),
                ("monitor", "in"),
                ("parameter_type", "MON"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / XFADE A'),
            [
                ("track", "SEL"),
                ("x_fade_assign", "a"),
                ("parameter_type", "XFADE"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / XFADE OFF'),
            [
                ("track", "SEL"),
                ("x_fade_assign", "off"),
                ("parameter_type", "XFADE"),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / PLAY'),
            [
                ("track", "SEL"),
                ("parameter_type", "PLAY"),
                ("play", True),
            ]
        )
        self.check_valid_result(
            parse_target_path('SEL / STOP'),
            [
                ("track", "SEL"),
                ("parameter_type", "STOP"),
                ("stop", True),
            ]
        )

