# Dependencies

## Vendored packages

These packages are bundled with each download of zcx.
[See here](/dev/build) for installation instructions.

### PyYAML

Used wherever YAML files are interacted with.

[link](https://pypi.org/project/PyYAML/)

### asteval

Used to interpret user-provided Python expressions. <sup>[see why](/lessons/python-context/)</sup>

[link](https://lmfit.github.io/asteval/)

### requests

Used only by the [upgrade script](/lessons/upgrade/#automatic-upgrade) for facilitating requests to GitHub.

[link](https://pypi.org/project/requests/)

### semver

Used only by the [upgrade script](/lessons/upgrade/#automatic-upgrade) for comparing [Semantic Versioning precedence](https://semver.org/#spec-item-11) between versions.

[link](https://pypi.org/project/semver/)

## Development dependencies

### Watchdog

Used by the [build script](/dev/build) to watch for code changes.

[link](https://pypi.org/project/watchdog/)

### Documentation

The following packages are only necessary if you want to build the documentation locally.

#### mkdocs

Static site generator powering this documentation.

[link](https://www.mkdocs.org/)

#### mkdocs plugins

- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/)
- [mkdocs-awesome-nav](https://github.com/lukasgeiter/mkdocs-awesome-nav)
- [mkdocs-nav-weight](https://github.com/shu307/mkdocs-nav-weight)
- [mkdocs-open-in-new-tab](https://github.com/JakubAndrysek/mkdocs-open-in-new-tab)
