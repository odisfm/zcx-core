try:
    from .hardware import colors as hardware_colors
except ImportError:
    # this makes your IDE autocomplete work
    from ..hardware.push_1 import colors as hardware_colors

RgbColor = hardware_colors.RgbColor
Pulse = hardware_colors.Pulse
Blink = hardware_colors.Blink


class ColorSwatches:

    basic = hardware_colors.BasicColorSwatch
    biled = hardware_colors.BiledColorSwatch
    rgb = hardware_colors.RgbColorSwatch


def get_named_color(name):
    name = name.upper()
    color = getattr(hardware_colors.Rgb, name, None)
    return color


def parse_color_definition(color):
    if type(color) is int:
        if 0 <= color <= 127:
            return RgbColor(color)
    elif type(color) is str:
        return get_named_color(color)
