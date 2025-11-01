# Dependencies

## Vendored packages

These packages are bundled with each download of zcx.
[See here](build.md) for installation instructions.

### PyYAML

Used wherever YAML files are interacted with.

[link](https://pypi.org/project/PyYAML/)

### asteval

Used to interpret user-provided Python expressions. <sup>[see why](../lessons/python-context.md)</sup>

[link](https://lmfit.github.io/asteval/)

### requests

Used only by the [upgrade script](../lessons/upgrade.md#automatic-upgrade) for facilitating requests to GitHub.

[link](https://pypi.org/project/requests/)

### semver

Used only by the [upgrade script](../lessons/upgrade.md#automatic-upgrade) for comparing [Semantic Versioning precedence](https://semver.org/#spec-item-11) between versions.

[link](https://pypi.org/project/semver/)

## Development dependencies

You can install all development dependencies with `pip install -r requirements.txt` from the repo root.

### Watchdog

Used by the [build script](build.md) to watch for code changes.

[link](https://pypi.org/project/watchdog/)

### Documentation

This documentation is powered by [mkdocs](https://www.mkdocs.org/), the [Material for MkDocs theme](https://squidfunk.github.io/mkdocs-material/), and [several plugins](https://github.com/odisfm/zcx-core/blob/main/docs/requirements.txt) for mkdocs.

You can install mkdocs and all required plugins with `pip install -r docs/requirements.txt`.
