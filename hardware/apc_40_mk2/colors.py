from copy import copy

from ableton.v2.control_surface.elements import Color, AnimatedColor
RgbColor = Color


animation_speed_translation = [0, 1, 2, 3, 4]
pulse_channels = [10, 9, 8, 7, 6] # slow to fast
blink_channels = [15, 14, 13, 12, 11]

def translate_speed(speed):
    if speed < 0 or speed >= len(animation_speed_translation):
        return 0
    return animation_speed_translation[speed]

class Pulse(AnimatedColor):
    def __init__(self, color1, color2, speed=1):
        super().__init__(color1, color2)
        speed_index = translate_speed(speed - 1)
        self._channel = pulse_channels[speed_index]

class Blink(AnimatedColor):
    def __init__(self, color1, color2, speed=1):
        super().__init__(color1, color2)
        speed_index = translate_speed(speed - 1)
        self._channel = blink_channels[speed_index]

class BasicColorSwatch:

    OFF = Color(0)
    ON = Color(127)
    HALF = ON
    HALF_BLINK_SLOW = ON
    HALF_BLINK_FAST = ON
    FULL = ON
    FULL_BLINK_SLOW = ON
    FULL_BLINK_FAST = ON
    TRANSPARENT = OFF
    PAGE_ACTIVE = ON
    PAGE_INACTIVE = OFF
    PAGE_DISABLED = OFF
    ERROR = ON

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL

class BiledColorSwatch:
    OFF = Color(0)
    ON = Color(127)
    YELLOW = Color(1)
    ORANGE = Color(127)
    GREEN = YELLOW
    PLAY_GREEN = YELLOW
    GREEN_HALF = YELLOW
    GREEN_BLINK_SLOW = YELLOW
    GREEN_BLINK_FAST = YELLOW
    RED = ORANGE
    RED_HALF = ORANGE
    RED_BLINK_SLOW = ORANGE
    RED_BLINK_FAST = ORANGE
    YELLOW = YELLOW
    YELLOW_HALF = YELLOW
    YELLOW_BLINK_SLOW = YELLOW
    YELLOW_BLINK_FAST = YELLOW
    AMBER = YELLOW
    AMBER_HALF = ORANGE
    AMBER_BLINK_SLOW = ORANGE
    AMBER_BLINK_FAST = ORANGE
    HALF = YELLOW
    FULL = ORANGE
    PAGE_ACTIVE = ORANGE
    PAGE_INACTIVE = YELLOW
    PAGE_DISABLED = OFF
    ERROR = ON

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL

class RgbColorSwatch(object):
    PLAY_GREEN = Color(21)

    RED = Color(5)
    ORANGE = Color(9)
    AMBER = ORANGE  # alias
    YELLOW = Color(13)
    GREEN = Color(75)
    LIME = Color(17)
    BLUE = Color(45)
    SKY = Color(37)
    CYAN = Color(33)
    PURPLE = Color(49)
    ORCHID = PURPLE
    MAGENTA = Color(53)
    INDIGO = Color(50)
    PINK = Color(57)

    DARK_GREY = Color(1)
    GREY = Color(2)
    WHITE = Color(3)

    OFF = Color(0)
    ON = PURPLE
    BLACK = OFF

    PAGE_ACTIVE = AMBER
    PAGE_INACTIVE = GREY
    PAGE_DISABLED = DARK_GREY
    ERROR = Blink(RED, OFF, 6)

    ARM_RED = Color(7)

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL


def simplify_Color(color):
    from .. import ROOT_LOGGER
    color1 = getattr(color, 'color1', color)
    return color1

palette_forest = [
    Color(89),
    Color(110),
    Color(103),
    Color(86),
    Color(44),
    Color(109),
    Color(105),
    Color(16),
    Color(30),
    Color(93),
    Color(98),
    Color(1),
    Color(63),
]

palette_forest_reverse = palette_forest.copy()
palette_forest_reverse.reverse()

palette_ocean = [
    Color(37),
    Color(38),
    Color(36),
    Color(39),
    Color(77),
    Color(51),
    Color(104),
    Color(24),
    Color(38),
    Color(36),
    Color(41),
    Color(42),
    Color(71),
]

palette_ocean_reverse = palette_ocean.copy()
palette_ocean_reverse.reverse()

palette_rainbow = [
    Color(5),
    Color(9),
    Color(13),
    Color(17),
    Color(37),
    Color(49),
    Color(52),
]

palette_nebula = [
    Color(50),
    Color(47),
    Color(6),
    Color(54),
    Color(55),
    Color(10),
    Color(47),
    Color(50),
    Color(6),
    Color(47),
    Color(50),
    Color(47),
    Color(54),
]

palette_nebula_reverse = palette_nebula.copy()
palette_nebula_reverse.reverse()

palette_rainbow_reverse = palette_rainbow.copy()
palette_rainbow_reverse.reverse()

palettes = {
    'forest': palette_forest,
    'forest_reverse': palette_forest_reverse,
    'ocean': palette_ocean,
    'ocean_reverse': palette_ocean_reverse,
    'rainbow': palette_rainbow,
    'rainbow_reverse': palette_rainbow_reverse,
    'nebula': palette_nebula,
    'nebula_reverse': palette_nebula_reverse,
}

LIVE_TO_MIDI = [
	# row 1
	52,
	126,
	124,
	110,
	75,
	21,
	29,
	77,
	36,
	41,
	92,
	94,
	82,
	3,
	# row 2
	5,
	60,
	62,
	85,
	88,
	76,
	34,
	37,
	41,
	42,
	44,
	52,
	53,
	3,
	# row 3
	4,
	108,
	12,
	16,
	20,
	89,
	24,
	114,
	32,
	26,
	93,
	44,
	3,
	2,
	# row 4
	107,
	99,
	125,
	111,
	75,
	28,
	90,
	114,
	36,
	40,
	94,
	93,
	94,
	2,
	# row 5
	6,
	61,
	100,
	13,
	63,
	76,
	78,
	41,
	67,
	42,
	69,
	82,
	57,
	0
]

def live_index_for_midi_index(live_index):
    return LIVE_TO_MIDI[live_index % 70]

def simplify_color(color):
    color1 = getattr(color, 'color1', color)
    return color1
