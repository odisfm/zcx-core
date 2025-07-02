from copy import copy

from Push2.colors import (
    Basic,
    Rgb,
    Pulse,
    Blink,
    FallbackColor,
    TransparentColor,
    determine_shaded_color_index,
    inverse_translate_color_index,
    translate_color_index
)

from Push2.colors import IndexedColor as PushIndexedColor
from pushbase.colors import Color


animation_speed_translation = [48, 24, 12, 6, 4]


class IndexedColor(PushIndexedColor):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    def shade(self, shade_level=1):
        return PushIndexedColor.from_push_index((self.midi_value + shade_level))


RgbColor = IndexedColor

def translate_speed(speed):
    if speed < 1 or speed >= len(animation_speed_translation):
        return 48
    return animation_speed_translation[speed]

class BasicColorSwatch:
    OFF = Color(0)
    ON = IndexedColor(127)
    FULL = ON
    LOW = IndexedColor(20)

    HALF = IndexedColor(50)
    HALF_BLINK_SLOW = Blink(FULL, LOW, 48)
    HALF_BLINK_FAST = Blink(FULL, LOW, 12)

    FULL_BLINK_SLOW = Blink(FULL, OFF, 48)
    FULL_BLINK_FAST = Blink(FULL, OFF, 12)

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL

class RgbColorSwatch(object):
    PLAY_GREEN = IndexedColor(126)

    RED = IndexedColor(2)
    ORANGE = IndexedColor(3)
    AMBER = ORANGE  # alias
    YELLOW = IndexedColor(8)
    GREEN = IndexedColor(10)
    LIME = IndexedColor(12)
    BLUE = IndexedColor(18)
    SKY = IndexedColor(16)
    CYAN = IndexedColor(15)
    OCEAN = IndexedColor(33) # hw specific
    DEEP_OCEAN = IndexedColor(95) # hw specific
    PURPLE = IndexedColor(107)
    ORCHID = PURPLE
    MAGENTA = IndexedColor(109)
    INDIGO = IndexedColor(101)
    PINK = IndexedColor(23)

    LIGHT_GREY = IndexedColor(123)
    DARK_GREY = IndexedColor(124)
    BLACK = IndexedColor(0)
    WHITE = IndexedColor(122)
    GREY = LIGHT_GREY
    ON = WHITE
    OFF = BLACK

    # GREEN_HALF = GREEN.shade(1)
    GREEN_BLINK_SLOW = Blink(GREEN, OFF, 48)
    GREEN_BLINK_FAST = Blink(GREEN, OFF, 12)
    # RED = RED
    # RED_HALF = RED.shade(1)
    RED_BLINK_SLOW = Blink(RED, OFF, 48)
    RED_BLINK_FAST = Blink(RED.shade(1), OFF, 12)
    # YELLOW = YELLOW
    # YELLOW_HALF = Blink(YELLOW.shade(1))
    YELLOW_BLINK_SLOW = Blink(YELLOW, OFF, 48)
    YELLOW_BLINK_FAST = Blink(YELLOW, OFF, 12)
    # AMBER = AMBER
    # AMBER_HALF = AMBER.shade(1)
    AMBER_BLINK_SLOW = Blink(AMBER, OFF, 48)
    AMBER_BLINK_FAST = Blink(AMBER, OFF, 12)
    HALF = Color(4)
    HALF_BLINK_SLOW = RED_BLINK_SLOW
    HALF_BLINK_FAST = RED_BLINK_FAST
    FULL = Color(127)
    FULL_BLINK_SLOW = GREEN_BLINK_SLOW
    FULL_BLINK_FAST = GREEN_BLINK_FAST
    PAGE_ACTIVE = AMBER
    PAGE_INACTIVE = GREY
    PAGE_DISABLED = DARK_GREY
    ERROR = Blink(RED, OFF, 12)

    ARM_RED = IndexedColor(1)

    def __init__(self):
        pass

    @classmethod
    def __getattr__(cls, attr):
        return cls.FULL

BiledColorSwatch = RgbColorSwatch

def simplify_color(color):
    from .. import ROOT_LOGGER
    color1 = getattr(color, 'color1', color)
    return color1

palette_forest = [
    RgbColorSwatch.GREEN,
    RgbColorSwatch.LIME,
    RgbColorSwatch.AMBER,
    RgbColorSwatch.LIME.shade(1),
    RgbColorSwatch.GREEN.shade(2),
    RgbColorSwatch.AMBER.shade(1),
]

palette_forest_reverse = palette_forest.copy()
palette_forest_reverse.reverse()

palette_ocean = [
    RgbColorSwatch.DEEP_OCEAN,
    RgbColorSwatch.OCEAN,
    RgbColorSwatch.BLUE,
    RgbColorSwatch.GREEN.shade(3),
    RgbColorSwatch.DEEP_OCEAN,
    RgbColorSwatch.OCEAN,
    RgbColorSwatch.BLUE,
    RgbColorSwatch.PURPLE,
    RgbColorSwatch.BLUE,
    RgbColorSwatch.DEEP_OCEAN,
    RgbColorSwatch.INDIGO,
]

palette_ocean_reverse = palette_ocean.copy()
palette_ocean_reverse.reverse()

palette_rainbow = [
    RgbColorSwatch.RED,
    RgbColorSwatch.ORANGE,
    RgbColorSwatch.YELLOW,
    RgbColorSwatch.GREEN,
    RgbColorSwatch.SKY,
    RgbColorSwatch.BLUE,
    RgbColorSwatch.PURPLE,
    RgbColorSwatch.MAGENTA,
    RgbColorSwatch.PINK,
]

palette_nebula = [
    RgbColorSwatch.PURPLE,
    RgbColorSwatch.RED,
    RgbColorSwatch.PURPLE.shade(1),
    RgbColorSwatch.AMBER,
    RgbColorSwatch.DEEP_OCEAN,
    RgbColorSwatch.INDIGO,
    RgbColorSwatch.PURPLE.shade(1),
    RgbColorSwatch.AMBER.shade(1),
    RgbColorSwatch.DEEP_OCEAN.shade(1),
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
    return translate_color_index(live_index)
