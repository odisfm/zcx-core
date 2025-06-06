# Building zcx from source

If you would like to [contribute to zcx-core](/dev/contributing), you will need to use the build script to consolidate all necessary files into a folder in your Live `Remote Scripts` directory.

!!! warning

    This lesson is only intended for developers.
    To use zcx, see [getting started](/tutorials/getting-started).

## Instructions

### Clone the repo

Clone the repo [from GitHub](https://github.com/odisfm/zcx-core/) to a convenient location on your computer.

### Install vendored dependencies

zcx bundles [several packages](/dev/dependencies) with each install.
These dependencies must be installed in the folder `zcx-core/app/vendor`.
For Mac/Linux users, a simple script is provided at `zcx-core/tools/install_dependencies.sh` to install the packages (via pip) to the correct location.

**Note:** these packages **must** be located in the `vendor/` directory.

### Install watchdog

You will need to install [watchdog](https://pypi.org/project/watchdog/) in your Python environment to monitor the codebase for changes.

### Run the script

From the project root, run:

`python tools/build.py <hardware name> <destination folder name>`

Where `<hardware name>` is the name of a folder in `zcx-core/hardware`, e.g. `push_1` and `<desintation folder name>` is a name of your choice, e.g. `my_zcx_script`.

#### Extra arguments

##### --custom-config

Provide the path to a folder that will be copied into the destination instead of the `demo_config` folder.

##### --user-library

By default the script will determine the default path to your Live User Library depending on your operating system.
If you use a non-default location for your User Library, you will need to provide the path as an argument.
