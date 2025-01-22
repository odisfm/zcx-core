from pushbase.colors import (
Basic,
Rgb,
BiLed,
Pulse,
Blink,
RgbColor
)

class BasicColorSwatch(Basic):

    base = RgbColor(127)

class BiledColorSwatch(BiLed):

    base = RgbColor(127)

class RgbColorSwatch(Rgb):

    base = Rgb.MAGENTA

