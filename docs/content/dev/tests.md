# Testing zcx

zcx's test system is built on Python's [unittest](https://docs.python.org/3/library/unittest.html) framework.

Test files are discovered and run by the [TestRunner](https://github.com/odisfm/zcx-core/blob/dev/app/test_runner.py).
Tests are run from within zcx, after zcx and the Live set have finished loading.

## Core tests

These are tests for the code common to all zcx releases.
They are only intended for use in development, and so are not actually included in any zcx download.

To run the tests, [build zcx from source](build.md) using `__test` as the hardware name argument.
Test results will output to the file `test_log.txt`, and [optionally to log.txt](../reference/file/preferences.md#log_includes_tests).

Test files are located in [tests/](https://github.com/odisfm/zcx-core/tree/dev/tests).
All test cases inherit from a base class, [ZCXTestCase](https://github.com/odisfm/zcx-core/blob/dev/app/zcx_test_case.py).
The base test class includes some useful convenience methods, so read the source code to familiarise yourself with them.
Of note is the attribute `zcx_api`, available on all test cases.
This returns a [ZcxApi](https://github.com/odisfm/zcx-core/blob/main/app/api_manager.py) object, making it easy to get reference to controls, encoders, groups, and matrix sections.

### The test set

Where possible, tests are written so that they don't depend on the state of any Live set.
However, when testing some features this is not feasible.

The repo includes [zcx test set Project](https://github.com/odisfm/zcx-core/tree/dev/tests/zcx%20test%20set%20Project), a Live project directory with the file `zcx_test_set.als`.
This set file provides a known state we can write tests against.

!!! warning ""
    You should expect the test set to require the most recent Live beta to open.

## User tests

These are tests written by you, to validate your specific zcx configuration and/or set file.

To add user tests, create the folder `user_tests/` inside your zcx folder.
Create any test files you want in this folder, prefixed with `test_`, e.g. `test_bindings.py`.

In each test, import and extend `ZCXTestCase`, which is added to the path automatically.

```python
from zcx_test_case import ZCXTestCase
```

Follow the [unittest docs](https://docs.python.org/3/library/unittest.html) for detailed instructions on the framework.

