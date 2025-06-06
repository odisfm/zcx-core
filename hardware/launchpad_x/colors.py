from copy import copy

from pushbase.colors import (
Basic,
Rgb,
BiLed,
RgbColor,
Color,
FallbackColor,
TransparentColor
)

from novation.colors import Pulse as NovationPulse
from novation.colors import Blink as NovationBlink

class Pulse(NovationPulse):

    def __init__(self, color1=None, color2=None, speed=None):
        super().__init__(color1=color1, color2=color1)

class Blink(NovationBlink):

    def __init__(self, color1=None, color2=None, speed=None):
        super().__init__(color1=color1, color2=color2)


white = RgbColor(3)
green = RgbColor(22)

animation_speed_translation = [48, 24, 12, 8, 4]

def translate_speed(speed):
    if speed < 1 or speed >= len(animation_speed_translation):
        # raise ConfigurationError(f'Invalid speed: {speed}')
        return 48
    return animation_speed_translation[speed]

class BasicColorSwatch:

    HALF = Color(1)
    HALF_BLINK_SLOW = Color(2)
    HALF_BLINK_FAST = Color(3)
    FULL = Color(4)
    FULL_BLINK_SLOW = Color(5)
    FULL_BLINK_FAST = Color(6)
    OFF = Color(0)
    ON = Color(127)
    TRANSPARENT = TransparentColor()
    GREEN = Color(127)
    GREEN_HALF = HALF
    GREEN_BLINK_SLOW = FULL_BLINK_SLOW
    GREEN_BLINK_FAST = FULL_BLINK_FAST
    PLAY_GREEN = FULL
    RED = HALF
    RED_HALF = HALF
    RED_BLINK_SLOW = HALF_BLINK_SLOW
    RED_BLINK_FAST = HALF_BLINK_FAST
    YELLOW = HALF
    YELLOW_HALF = HALF
    YELLOW_BLINK_SLOW = HALF_BLINK_SLOW
    YELLOW_BLINK_FAST = HALF_BLINK_FAST
    AMBER = HALF
    AMBER_HALF = HALF
    AMBER_BLINK_SLOW = HALF_BLINK_SLOW
    AMBER_BLINK_FAST = HALF_BLINK_FAST
    PAGE_ACTIVE = FULL
    PAGE_INACTIVE = HALF
    PAGE_DISABLED = OFF
    ERROR = HALF_BLINK_FAST

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL

class BiledColorSwatch:
    OFF = Color(0)
    ON = Color(127)
    GREEN = Color(127)
    PLAY_GREEN = GREEN
    GREEN_HALF = Color(19)
    GREEN_BLINK_SLOW = Color(24)
    GREEN_BLINK_FAST = Color(23)
    RED = Color(4)
    RED_HALF = Color(1)
    RED_BLINK_SLOW = Color(5)
    RED_BLINK_FAST = Color(6)
    YELLOW = Color(16)
    YELLOW_HALF = Color(13)
    YELLOW_BLINK_SLOW = Color(17)
    YELLOW_BLINK_FAST = Color(18)
    AMBER = Color(10)
    AMBER_HALF = Color(7)
    AMBER_BLINK_SLOW = Color(11)
    AMBER_BLINK_FAST = Color(12)
    HALF = Color(127)
    FULL = Color(19)
    PAGE_ACTIVE = AMBER
    PAGE_INACTIVE = RED_HALF
    PAGE_DISABLED = OFF
    ERROR = RED_BLINK_FAST

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL

class RgbColorSwatch(object):
    PLAY_GREEN = RgbColor(21)

    RED = RgbColor(5)
    ORANGE = RgbColor(9)
    AMBER = ORANGE  # alias
    YELLOW = RgbColor(13)
    GREEN = RgbColor(75)
    LIME = RgbColor(17)
    BLUE = RgbColor(45)
    SKY = RgbColor(37)
    CYAN = RgbColor(33)
    PURPLE = RgbColor(49)
    ORCHID = PURPLE
    MAGENTA = RgbColor(53)
    INDIGO = RgbColor(50)
    PINK = RgbColor(57)

    DARK_GREY = RgbColor(1)
    GREY = RgbColor(2)
    WHITE = RgbColor(3)

    OFF = RgbColor(0)
    ON = PURPLE
    BLACK = OFF

    GREEN_HALF = GREEN.shade(1)
    GREEN_BLINK_SLOW = Blink(GREEN, OFF, 48)
    GREEN_BLINK_FAST = Blink(GREEN, OFF, 12)
    RED_HALF = RED.shade(1)
    RED_BLINK_SLOW = Blink(RED, OFF, 48)
    RED_BLINK_FAST = Blink(RED.shade(1), OFF, 12)
    YELLOW_HALF = Blink(YELLOW.shade(1))
    YELLOW_BLINK_SLOW = Blink(YELLOW, OFF, 48)
    YELLOW_BLINK_FAST = Blink(YELLOW, OFF, 12)
    AMBER_HALF = AMBER.shade(1)
    AMBER_BLINK_SLOW = Blink(AMBER, OFF, 48)
    AMBER_BLINK_FAST = Blink(AMBER, OFF, 12)
    HALF = ON.shade(1)
    HALF_BLINK_SLOW = RED_BLINK_SLOW
    HALF_BLINK_FAST = RED_BLINK_FAST
    FULL = ON
    FULL_BLINK_SLOW = GREEN_BLINK_SLOW
    FULL_BLINK_FAST = GREEN_BLINK_FAST

    PAGE_ACTIVE = AMBER
    PAGE_INACTIVE = GREY
    PAGE_DISABLED = DARK_GREY
    ERROR = Blink(RED, OFF, 6)

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL


def simplify_color(color):
    from .. import ROOT_LOGGER
    color1 = getattr(color, 'color1', color)
    return color1

palette_forest = [
    RgbColor(89),
    RgbColor(110),
    RgbColor(103),
    RgbColor(86),
    RgbColor(44),
    RgbColor(109),
    RgbColor(105),
    RgbColor(16),
    RgbColor(30),
    RgbColor(93),
    RgbColor(98),
    RgbColor(1),
    RgbColor(63),
]

palette_forest_reverse = palette_forest.copy()
palette_forest_reverse.reverse()

palette_ocean = [
    RgbColor(37),
    RgbColor(38),
    RgbColor(36),
    RgbColor(39),
    RgbColor(77),
    RgbColor(51),
    RgbColor(104),
    RgbColor(24),
    RgbColor(38),
    RgbColor(36),
    RgbColor(41),
    RgbColor(42),
    RgbColor(71),
]

palette_ocean_reverse = palette_ocean.copy()
palette_ocean_reverse.reverse()

palette_rainbow = [
    RgbColor(5),
    RgbColor(9),
    RgbColor(13),
    RgbColor(17),
    RgbColor(37),
    RgbColor(49),
    RgbColor(52),
]

palette_nebula = [
    RgbColor(50),
    RgbColor(47),
    RgbColor(6),
    RgbColor(54),
    RgbColor(55),
    RgbColor(10),
    RgbColor(47),
    RgbColor(50),
    RgbColor(6),
    RgbColor(47),
    RgbColor(50),
    RgbColor(47),
    RgbColor(54),
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

def live_index_for_midi_index(live_index):
    live_index = max(live_index, 0)

    LOWER_BOUND = 0
    UPPER_BOUND = 28 # AFAAIK only the first 28 live colors (first 2 rows) map well to midi colors
    END_ROW_1 = 13
    END_ROW_2 = 27
    OFFSET_1 = 4
    OFFSET_2 = 51

    if LOWER_BOUND <= live_index < UPPER_BOUND:
        if live_index == END_ROW_1:
            return 3
        elif live_index == END_ROW_2:
            return 2
        elif live_index < 14:
            return (live_index * OFFSET_1) + OFFSET_1 + 1
        else:
            return (live_index * OFFSET_1) - OFFSET_2 + 1
    else:
        return live_index_for_midi_index(live_index % (END_ROW_2 + 1))
