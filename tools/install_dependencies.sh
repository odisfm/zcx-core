#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 -m pip install pyyaml --target "$SCRIPT_DIR/../app/vendor" --upgrade
python3 -m pip install requests --target "$SCRIPT_DIR/../app/vendor" --upgrade
python3 -m pip install asteval --target "$SCRIPT_DIR/../app/vendor" --upgrade
python3 -m pip install semver --target "$SCRIPT_DIR/../app/vendor" --upgrade
