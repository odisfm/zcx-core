import functools
from typing import TYPE_CHECKING
import fnmatch
import sys
import unittest
import os
from pathlib import Path
from functools import partial
from .zcx_component import ZCXComponent
from .consts import ZCX_TEST_SET_NAME
from .parse_target_path import parse_target_path

if TYPE_CHECKING:
    from zcx_core import ZCXCore


class TestRunner(ZCXComponent):

    def __init__(
            self,
            name="TestRunner",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        self.test_suite = None
        self.user_test_suite = None
        self.test_loader = unittest.TestLoader()
        self.stream = None

    def write_to_stream(self, message):
        """Write message to the test runner's stream"""
        if self.stream:
            msg_str = str(message)
            self.stream.write(f"\n>> {msg_str}\n")
            self.stream.flush()

    def setup(self):
        """Discover and load tests from the tests/ directory"""
        try:
            project_root = Path(__file__).parent
            tests_dir = project_root / "tests"
            user_tests_dir = project_root / "user_tests"
            sys.path.insert(0, project_root.as_posix())

            for name in list(sys.modules):
                if name.startswith("tests.") or name.startswith("user_tests."):
                    sys.modules.pop(name, None)

            from tests.zcx_test_case import ZCXTestCase

            ZCXTestCase.zcx = self.canonical_parent
            ZCXTestCase.song = self.song
            ZCXTestCase.log = self.write_to_stream
            ZCXTestCase._is_using_test_set = self.song.name.startswith(
                ZCX_TEST_SET_NAME
            )
            ZCXTestCase._parse_target_path = functools.partial(parse_target_path)

            try:
                if tests_dir.exists() and tests_dir.is_dir():
                    self.test_suite = self.test_loader.discover(
                        start_dir=str(tests_dir),
                        pattern='test*.py',
                        top_level_dir=str(project_root)
                    )
                else:
                    self.test_suite = unittest.TestSuite()
            except Exception:
                self.test_suite = unittest.TestSuite()

            try:
                if user_tests_dir.exists() and user_tests_dir.is_dir():
                    self.user_test_suite = self.test_loader.discover(
                        start_dir=str(user_tests_dir),
                        pattern='test*.py',
                        top_level_dir=str(project_root)
                    )
                else:
                    self.user_test_suite = unittest.TestSuite()
            except Exception:
                self.user_test_suite = unittest.TestSuite()

            def do_run_tests(test_suite, _tests_dir):
                if test_suite is None:
                    return
                test_count = test_suite.countTestCases()

                if test_count:
                    self.log(f"Discovered {test_count} test cases in {_tests_dir}")
                    result = self.run_tests(test_suite)
                    if result is False:
                        return
                    if result.wasSuccessful():
                        self.log(f"{test_count} tests passed!")
                    else:
                        self.log(f"{len(result.failures)}/{test_count} tests failed!")

            do_run_tests(self.test_suite, tests_dir)
            do_run_tests(self.user_test_suite, user_tests_dir)

        except Exception as e:
            if str(e).startswith("Start directory is not importable"):
                return
            self.log(f"Error discovering tests: {e}")
            self.test_suite = unittest.TestSuite()

    def run_tests(self, test_suite):
        """Run the discovered tests"""
        if test_suite is None:
            self.log("No test suite available. Run setup() first.")
            return False

        project_root = Path(__file__).parent
        log_file_path = project_root / "test_log.txt"

        with open(log_file_path, "a") as log_file:
            self.stream = log_file

            runner = unittest.TextTestRunner(stream=log_file, verbosity=2)
            result = runner.run(test_suite)

            self.stream = None

        self.log(f"Test results logged to {log_file_path}")

        return result
