from pushbase.colors import (
Basic,
Rgb,
BiLed,
Pulse,
Blink,
RgbColor,
Color,
FallbackColor,
TransparentColor
)

white = RgbColor(3)
green = RgbColor(22)
pulse_test = Pulse(white, green, 48)

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

    def __init__(self):
        pass

    def __getattr__(self, attr):
        return FULL


class BiledColorSwatch:
    OFF = Color(0)
    ON = Color(127)
    GREEN = Color(127)
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

    def __init__(self):
        pass

    def __getattr__(self, attr):
        return FULL

class RgbColorSwatch(object):
    OFF = Rgb.BLACK
    ON = Rgb.YELLOW
    BLACK = RgbColor(0)
    DARK_GREY = RgbColor(1)
    GREY = RgbColor(2)
    WHITE = RgbColor(3)
    RED = RgbColor(5)
    AMBER = RgbColor(9)
    YELLOW = RgbColor(13)
    LIME = RgbColor(17)
    GREEN = RgbColor(21)
    SPRING = RgbColor(25)
    TURQUOISE = RgbColor(29)
    CYAN = RgbColor(33)
    SKY = RgbColor(37)
    OCEAN = RgbColor(41)
    BLUE = RgbColor(45)
    ORCHID = RgbColor(49)
    MAGENTA = RgbColor(53)
    PINK = RgbColor(57)
    GREEN_HALF = GREEN.shade(1)
    GREEN_BLINK_SLOW = Blink(GREEN, OFF, 48)
    GREEN_BLINK_FAST = Blink(GREEN, OFF, 12)
    # RED = RED
    RED_HALF = RED.shade(1)
    RED_BLINK_SLOW = Blink(RED, OFF, 48)
    RED_BLINK_FAST = Blink(RED.shade(1), OFF, 12)
    # YELLOW = YELLOW
    YELLOW_HALF = Blink(YELLOW.shade(1))
    YELLOW_BLINK_SLOW = Blink(YELLOW, OFF, 48)
    YELLOW_BLINK_FAST = Blink(YELLOW, OFF, 12)
    # AMBER = AMBER
    AMBER_HALF = AMBER.shade(1)
    AMBER_BLINK_SLOW = Blink(AMBER, OFF, 48)
    AMBER_BLINK_FAST = Blink(AMBER, OFF, 12)
    HALF = Color(4)
    HALF_BLINK_SLOW = RED_BLINK_SLOW
    HALF_BLINK_FAST = RED_BLINK_FAST
    FULL = Color(127)
    FULL_BLINK_SLOW = GREEN_BLINK_SLOW
    FULL_BLINK_FAST = GREEN_BLINK_FAST

    def __init__(self):
        pass

    def __getattr__(self, attr):
        return FULL


def simplify_color(color):
    from .. import ROOT_LOGGER
    color1 = getattr(color, 'color1', color)
    return color1
