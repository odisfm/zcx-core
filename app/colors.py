try:
    from .hardware import colors as hardware_colors
except ImportError:
    # this makes your IDE autocomplete work
    from ..hardware.push_1 import colors as hardware_colors

from .errors import *

Color = hardware_colors.Color
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
    if color is None:
        return hardware_colors.Rgb.RED
    return color

def parse_color_definition(color, calling_control=None):
    try:
        if type(color) is int:
            if 0 <= color <= 127:
                return RgbColor(color)
        elif type(color) is str:
            return get_named_color(color)
        elif type(color) is dict:

            special_color_type = list(color.keys())[0]
            special_color_def = list(color.values())[0]

            if special_color_type.lower() == 'blink':
                a_def = special_color_def['a']
                b_def = special_color_def['b']
                speed_def = special_color_def.get('speed', 1)
                a = parse_color_definition(a_def)
                b = parse_color_definition(b_def)
                speed = hardware_colors.translate_speed(speed_def)

                return Blink(a, b, speed)

            elif special_color_type.lower() == 'pulse':
                a_def = special_color_def['a']
                b_def = special_color_def['b']
                speed_def = special_color_def.get('speed', 1)
                a = parse_color_definition(a_def)
                b = parse_color_definition(b_def)
                speed = hardware_colors.translate_speed(speed_def)

                return Pulse(a, b, speed)
            elif special_color_type.lower() == 'palette':
                palette_name = special_color_def
                palette = hardware_colors.palettes.get(palette_name, None)
                index = calling_control._context['me']['index'] % len(palette)
                return palette[index]

            elif special_color_type.lower() == 'midi':
                return parse_color_definition(color['midi'])
            elif special_color_type.lower() == 'live':
                # todo: needs Live/controller tranlsation
                pass

            return RgbColor(3)

    except Exception as e:
        raise ConfigurationError(e)


def simplify_color(color):
    return hardware_colors.simplify_color(color)
