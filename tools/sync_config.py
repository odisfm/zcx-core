# AI slop
from pathlib import Path
from typing import NamedTuple, List

HOME = Path.home()

CONTROL_SURFACE_NAME = "_zcx_core"
HARDWARE_CONFIG = "push_1"


REMOTE_SCRIPTS_PATH = (
    HOME / f"Music/Ableton/User Library/Remote Scripts/{CONTROL_SURFACE_NAME}/"
)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "app/"

DEST_ROOT = REMOTE_SCRIPTS_PATH
CONFIG_ROOT = PROJECT_ROOT / "config"
DEST_CONFIG = DEST_ROOT / "config/"
PREFERENCES_ROOT = PROJECT_ROOT / "preferences"
DEST_PREFERENCES = DEST_ROOT / "preferences/"
PLUGINS_ROOT = PROJECT_ROOT / "plugins"
DEST_PLUGINS = DEST_ROOT / "plugins/"
HARDWARE_ROOT = PROJECT_ROOT / "_hardware"
SPECIFIC_HARDWARE = HARDWARE_ROOT / HARDWARE_CONFIG
DEST_HARDWARE = DEST_ROOT / "_hardware/"


class SyncPath(NamedTuple):
    source: Path
    destinations: List[Path]
    subdirs: List[str] = []
    rsync_args: List[str] = ["-avz", "--delete"]  # Default rsync arguments
    exclude_patterns: List[str] = []  # Patterns to exclude (can include paths)
    include_only: List[str] = []  # If set, only sync these specific files
    recursive: bool = True


# Configure your sync paths here
SYNC_PATHS = [
    # SyncPath(
    #     source=PROJECT_ROOT / '__init__.py',
    #     destinations=[DEST_ROOT / '__init__.py'],
    #     rsync_args=[
    #         '-avz',
    #         '--delete'
    #     ],
    #     recursive=False
    # ),
    SyncPath(
        source=SRC_ROOT,
        destinations=[DEST_ROOT],
        rsync_args=["-avz", "--delete"],
        recursive=True,
    ),
    SyncPath(
        source=HARDWARE_ROOT,
        destinations=[DEST_HARDWARE],
        rsync_args=["-avz", "--delete"],
    ),
    # SyncPath(
    #     source=CONFIG_ROOT,
    #     destinations=[DEST_CONFIG],
    #     rsync_args=['-avz', '--delete']
    # ),
    # SyncPath(
    #     source=PREFERENCES_ROOT,
    #     destinations=[DEST_PREFERENCES],
    #     rsync_args=['-avz', '--delete']
    # ),
    # SyncPath(
    #     source=PLUGINS_ROOT,
    #     destinations=[DEST_PLUGINS],
    #     rsync_args=['-avz', '--delete']
    # ),
]
