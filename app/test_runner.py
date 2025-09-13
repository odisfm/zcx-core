from typing import TYPE_CHECKING
import fnmatch
import sys
import unittest
import os
from pathlib import Path
from functools import partial
from .zcx_component import ZCXComponent

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
        self.test_loader = unittest.TestLoader()

    def setup(self):
        """Discover and load tests from the tests/ directory"""
        try:

            project_root = Path(__file__).parent
            tests_dir = project_root / "tests"

            for name in list(sys.modules):
                if name.startswith("tests.") or fnmatch.fnmatch(name, "test*"):
                    sys.modules.pop(name, None)

            self.test_suite = self.test_loader.discover(
                start_dir=str(tests_dir),
                pattern='test*.py',
                top_level_dir=str(project_root)
            )


            for suite in self.test_suite:
                for test in (suite if isinstance(suite, unittest.TestSuite) else [suite]):
                    for case in (test if isinstance(test, unittest.TestSuite) else [test]):
                        self.log(case)
                        case._zcx = self.canonical_parent
                        case.log = partial(self.log)

            test_count = self.test_suite.countTestCases()
            if test_count == 0:
                return

            self.log(f"Discovered {test_count} test cases in {tests_dir}")

            self.run_tests()

        except Exception as e:
            if str(e).startswith("Start directory is not importable"):
                return
            self.log(f"Error discovering tests: {e}")
            self.test_suite = unittest.TestSuite()

    def run_tests(self):
        """Run the discovered tests"""
        if self.test_suite is None:
            self.log("No test suite available. Run setup() first.")
            return False

        project_root = Path(__file__).parent
        log_file_path = project_root / "test_log.txt"

        with open(log_file_path, 'a') as log_file:
            runner = unittest.TextTestRunner(
                stream=log_file,
                verbosity=2
            )
            result = runner.run(self.test_suite)

        self.log(f"Test results logged to {log_file_path}")

        return result.wasSuccessful()
