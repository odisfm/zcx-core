# Building zcx from source

If you would like to [contribute to zcx-core](contributing.md), you will need to use the build script to consolidate all necessary files into a folder in your Live `Remote Scripts` directory.

!!! warning

    This lesson is only intended for developers.
    To use zcx, see [getting started](../lessons/getting-started/index.md).

## Instructions

### Clone the repo

Clone the repo [from GitHub](https://github.com/odisfm/zcx-core/) to a convenient location on your computer.

### Create a virtual environment

It is highly recommended that you create a [Python virtual environment](https://docs.python.org/3/library/venv.html) before proceeding.

### Install vendored dependencies

zcx bundles [several packages](dependencies.md) with each install.
These dependencies must be installed in the folder `zcx-core/app/vendor`.
A simple script is provided at `zcx-core/tools/install_vendored_dependencies.py` to install the packages (via pip) to the correct location.

!!! warning
    These packages **must** be located in the `vendor/` directory.

### Install development dependencies

From the project root, run `pip install -r requirements.txt` to install all [development dependencies](dependencies.md).

### Run the script

From the project root, run:

`python tools/build.py <hardware name> <destination folder name>`

Where `<hardware name>` is the name of a folder in `zcx-core/hardware`, e.g. `push_1` and `<desintation folder name>` is a name of your choice, e.g. `my_zcx_script`.
Omit `<destination folder name>` to use `_zcx_<hardware name>`.

You must manually create the destination folder.

#### Extra arguments

##### --custom-config

Provide the path to a folder that will be copied into the destination instead of the `demo_config` folder.

##### --blank-config

Use the [blank config](../lessons/blank-config.md) folder instead of the `demo_config` folder.

##### --user-library

By default, the script will determine the default path to your Live User Library depending on your operating system.
If you use a non-default location for your User Library, you will need to provide the path as an argument.

### Building with your own config

While working on zcx, you'll likely prefer to use your own config, rather than the demo config.

One option is to use the [--custom-config](#--custom-config) argument and pass the path to your own config.

Another is to use symbolic links in the destination directory to other files or directories on your computer.
The build script will ignore symbolic links in the destination directory.

## Building the documentation

This documentation is powered by [mkdocs](https://www.mkdocs.org/), the [Material for MkDocs theme](https://squidfunk.github.io/mkdocs-material/), and [several plugins](https://github.com/odisfm/zcx-core/blob/main/docs/requirements.txt) for mkdocs.

From the project root, run `pip install -r docs/requirements.txt` to install all documentation dependencies.
To start the dev server, run:
```bash
cd docs
mkdocs serve
```

For more information, refer to the documentation for the projects above.

!!! note "Suggestions welcome"
    If you have feedback about the existing docs, or think something should be added, feel free to post in [the Discord](https://discord.zcxcore.com).
