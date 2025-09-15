from typing import Any
import time
from tests.zcx_test_case import ZCXTestCase


class TestTargetPathParser(ZCXTestCase):

    def check_valid_result(
        self, result: dict[str, Any] = None, assertions: list[tuple[str, Any]] = None
    ) -> None:
        start_time = time.perf_counter()

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

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        # self.log(f"check_valid_result executed in {execution_time:.6f} seconds")

    def test_parse_simple_paths(self):
        test_cases = [
            ("SEL / VOL", [("track", "SEL"), ("parameter_type", "VOL")]),
            (
                '"my cool track" / VOL',
                [("track", "my cool track"), ("parameter_type", "VOL")],
            ),
            (
                '"my cool track" / PAN',
                [("track", "my cool track"), ("parameter_type", "PAN")],
            ),
            ("1 / SEND F", [("track", "1"), ("parameter_type", "SEND"), ("send", "F")]),
            ("1 / PANL", [("track", "1"), ("parameter_type", "PANL")]),
            ("1 / PANR", [("track", "1"), ("parameter_type", "PANR")]),
            ("SELP", [("parameter_type", "SELP")]),
            (
                "1 / DEV(SEL) CS",
                [("track", "1"), ("device", "SEL"), ("parameter_type", "CS")],
            ),
            (
                '"my cool track" / DEV(1) P40',
                [
                    ("track", "my cool track"),
                    ("device", "1"),
                    ("parameter_number", "40"),
                ],
            ),
            (
                '"my cool track" / DEV("my device") "my param"',
                [
                    ("track", "my cool track"),
                    ("device", "my device"),
                    ("parameter_name", "my param"),
                ],
            ),
            (
                "SEL / DEV(SEL) B1 P2",
                [
                    ("track", "SEL"),
                    ("device", "SEL"),
                    ("bank", "1"),
                    ("parameter_number", "2"),
                ],
            ),
            (
                "DEV(SEL) B1 P2",
                [("device", "SEL"), ("bank", "1"), ("parameter_number", "2")],
            ),
            (
                "SEL / DEV(1.1) PAN",
                [
                    ("track", "SEL"),
                    ("chain_map", ["1", "1"]),
                    ("parameter_type", "PAN"),
                ],
            ),
            (
                'SEL / DEV(1."my chain") PAN',
                [
                    ("track", "SEL"),
                    ("chain_map", ["1", "my chain"]),
                    ("parameter_type", "PAN"),
                ],
            ),
            (
                'SEL / DEV("my rack"."my chain"."1"."my inner chain") VOL',
                [
                    ("track", "SEL"),
                    ("chain_map", ["my rack", "my chain", "1", "my inner chain"]),
                    ("parameter_type", "VOL"),
                ],
            ),
            (
                "SEL / DEV(1.1) SEND A",
                [
                    ("track", "SEL"),
                    ("chain_map", ["1", "1"]),
                    ("parameter_type", "SEND"),
                    ("send", "A"),
                ],
            ),
            (
                "SEL / DEV(1.1) VOL",
                [
                    ("track", "SEL"),
                    ("chain_map", ["1", "1"]),
                    ("parameter_type", "VOL"),
                ],
            ),
            ("XFADER", [("parameter_type", "XFADER")]),
            ("RING(0) / VOL", [("ring_track", "0"), ("parameter_type", "VOL")]),
        ]

        for input_path, expected_assertions in test_cases:
            with self.subTest(path=input_path):
                result = self._parse_target_path(input_path)
                self.check_valid_result(result, expected_assertions)

    def test_parse_additional_paths(self):
        test_cases = [
            ("SEL / DEV(1)", [("track", "SEL"), ("device", "1")]),
            (
                "SEL / DEV(1) SEL",
                [("track", "SEL"), ("device", "1"), ("parameter_type", "SEL")],
            ),
            (
                "SEL / SEL",
                [("track", "SEL"), ("track_select", True), ("parameter_type", "SEL")],
            ),
            ("SEL / ARM", [("track", "SEL"), ("arm", True), ("parameter_type", "ARM")]),
            (
                "SEL / MUTE",
                [("track", "SEL"), ("mute", True), ("parameter_type", "MUTE")],
            ),
            (
                "SEL / SOLO",
                [("track", "SEL"), ("solo", True), ("parameter_type", "SOLO")],
            ),
            (
                "SEL / MON IN",
                [("track", "SEL"), ("monitor", "in"), ("parameter_type", "MON")],
            ),
            (
                "SEL / XFADE A",
                [("track", "SEL"), ("x_fade_assign", "a"), ("parameter_type", "XFADE")],
            ),
            (
                "SEL / XFADE OFF",
                [
                    ("track", "SEL"),
                    ("x_fade_assign", "off"),
                    ("parameter_type", "XFADE"),
                ],
            ),
            (
                "SEL / PLAY",
                [("track", "SEL"), ("parameter_type", "PLAY"), ("play", True)],
            ),
            (
                "SEL / STOP",
                [("track", "SEL"), ("parameter_type", "STOP"), ("stop", True)],
            ),
        ]

        for input_path, expected_assertions in test_cases:
            with self.subTest(path=input_path):
                result = self._parse_target_path(input_path)
                self.check_valid_result(result, expected_assertions)

    def test_parse_complex_paths(self):
        test_cases = [
            ('DEV("my / dev") P1', [("device", "my / dev"), ("parameter_number", "1")]),
            (
                '"my cool / track" / DEV("my device") P1',
                [
                    ("track", "my cool / track"),
                    ("device", "my device"),
                    ("parameter_number", "1"),
                ],
            ),
            (
                '"my cool / track" / DEV("my / device") P1',
                [
                    ("track", "my cool / track"),
                    ("device", "my / device"),
                    ("parameter_number", "1"),
                ],
            ),
            (
                '1 / DEV("my / device") P1',
                [("track", "1"), ("device", "my / device"), ("parameter_number", "1")],
            ),
        ]

        for input_path, expected_assertions in test_cases:
            with self.subTest(path=input_path):
                result = self._parse_target_path(input_path)
                self.check_valid_result(result, expected_assertions)
