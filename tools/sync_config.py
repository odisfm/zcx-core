from pathlib import Path

HOME = Path.home()
CONTROL_SURFACE_NAME = "_zcx_core"
HARDWARE_CONFIG = None

REMOTE_SCRIPTS_PATH = HOME / "Music/Ableton/User Library/Remote Scripts"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "app"
