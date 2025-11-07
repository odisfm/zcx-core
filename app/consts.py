APP_NAME = "zcx-core"

DEFAULT_CONFIG_DIR = '_config'
DEFAULT_PREFS_DIR = '_preferences'

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

ZCX_TEST_SET_NAME = "zcx test set"

NAMED_COLORS = [
    "white",
    "grey",
    "dark_grey",
    "red",
    "orange",
    "yellow",
    "green",
    "play_green",
    "lime",
    "blue",
    "sky",
    "cyan",
    "purple",
    "magenta",
    "indigo",
    "pink"
]

DEFAULT_PLAYABLE_MIDI_CHANNEL = 9 # channel 10


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C"]
NOTE_NAMES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C"]

SCALE_NAMES = [
    "Major",
    "Minor",
    "Dorian",
    "Mixolydian",
    "Lydian",
    "Phrygian",
    "Locrian",
    "Whole Tone",
    "Half-whole Dim.",
    "Whole-half Dim.",
    "Minor Blues",
    "Minor Pentatonic",
    "Major Pentatonic",
    "Harmonic Minor",
    "Harmonic Major",
    "Dorian #4",
    "Phrygian Dominant",
    "Melodic Minor",
    "Lydian Augmented",
    "Lydian Dominant",
    "Super Locrian",
    "8-Tone Spanish",
    "Bhairav",
    "Hungarian Minor",
    "Hirajoshi",
    "In-Sen",
    "Iwato",
    "Kumoi",
    "Pelog Selisir",
    "Pelog Tembung",
    "Messiaen 3",
    "Messiaen 4",
    "Messiaen 5",
    "Messiaen 6",
    "Messiaen 7"
]

REPEAT_RATES = [
    "OFF", "1/4D", "1/4", "1/4T",
    "1/8D", "1/8", "1/8T",
    "1/16D", "1/16", "1/16T",
    "1/32D", "1/32", "1/32T",
    "1/64D", "1/64", "1/64T"
]

SEND_LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
SENDS_COUNT = len(SEND_LETTERS)
