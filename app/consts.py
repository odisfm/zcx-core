APP_NAME = "zcx-core"

DEFAULT_CONFIG_DIR = "_config"
DEFAULT_PREFS_DIR = "_preferences"

REQUIRED_HARDWARE_SPECS = ["cc_buttons", "note_buttons", "encoders"]

CXP_NAME = "ClyphX_Pro"

ON_GESTURES = ["pressed", "pressed_delayed", "double_clicked"]

OFF_GESTURES = [
    "released",
    "released_delayed",
    "released_immediately",
]

SUPPORTED_GESTURES = [
    "pressed",
    "pressed_delayed",
    "released",
    "released_immediately",
    "released_delayed",
    "double_clicked",
]

REQUIRED_LIVE_VERSION = (12, 1)

TEMPLATE_IDENTIFIER = "@"

LIVE_TEMPLATE_IDENTIFIER = "$"

DEFAULT_ON_THRESHOLD = 30
