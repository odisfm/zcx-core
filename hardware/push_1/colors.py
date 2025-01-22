from pushbase.colors import (
Basic,
Rgb,
BiLed,
Pulse,
Blink,
RgbColor
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

class BasicColorSwatch(Basic):

    base = RgbColor(127)

class BiledColorSwatch(BiLed):

    base = RgbColor(127)

class RgbColorSwatch(Rgb):

    base = Rgb.MAGENTA

def simplify_color(color):
    from .. import ROOT_LOGGER
    color1 = getattr(color, 'color1', color)
    return color1
