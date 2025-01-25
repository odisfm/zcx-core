from .hardware import colors as hardware_colors

# try:
# except ImportError:
#     # this makes your IDE autocomplete work
#     # from ..hardware.push_1 import colors as hardware_colors
#     pass

from .errors import *

Color = hardware_colors.Color
RgbColor = hardware_colors.RgbColor
Pulse = hardware_colors.Pulse
Blink = hardware_colors.Blink


class ColorSwatches:

    basic = hardware_colors.BasicColorSwatch
    biled = hardware_colors.BiledColorSwatch
    rgb = hardware_colors.RgbColorSwatch


def get_named_color(name, calling_control=None):
    if 'shade' in name.lower():
        if '${' in name:
            from .zcx_core import root_cs
            resolver = root_cs.component_map['ActionResolver']
            parse = resolver.compile(name, calling_control._vars, calling_control._context)
            if parse[1] != 0:
                raise ConfigurationError(f'Unparseable color definition: {parse[0]}')
            name = parse[0]
        split = name.split()
        if len(split) == 2:
            factor = 1
        elif len(split) == 3:
            factor = int(split[2])
        else:
            raise ConfigurationError(f'Invalid color def: {name}')
        return getattr(hardware_colors.RgbColorSwatch, split[0].upper()).shade(factor)

    name = name.upper()
    if calling_control is not None:
        swatch = calling_control._control_element._color_swatch
        color = getattr(swatch, name, None)
        if color is not None:
            return color

    return getattr(hardware_colors.Rgb, name, hardware_colors.Rgb.RED)

def parse_color_definition(color, calling_control=None):
    try:
        if type(color) is int:
            if 0 <= color <= 127:
                return RgbColor(color)
        elif type(color) is str:
            if '${' in color:
                from .zcx_core import root_cs
                resolver = root_cs.component_map['ActionResolver']
                parse = resolver.compile(color, calling_control._vars, calling_control._context)
                if parse[1] != 0:
                    raise ConfigurationError(f'Unparseable color definition: {color}')
                return get_named_color(parse[0], calling_control=calling_control)
            return get_named_color(color, calling_control)
        elif type(color) is dict:
            special_color_type = list(color.keys())[0].lower()
            special_color_def = list(color.values())[0]

            if special_color_type == 'blink':
                a_def = special_color_def['a']
                b_def = special_color_def['b']
                speed_def = special_color_def.get('speed', 1)
                a = parse_color_definition(a_def)
                b = parse_color_definition(b_def)
                speed = hardware_colors.translate_speed(speed_def)

                return Blink(a, b, speed)

            elif special_color_type == 'pulse':
                a_def = special_color_def['a']
                b_def = special_color_def['b']
                speed_def = special_color_def.get('speed', 1)
                a = parse_color_definition(a_def)
                b = parse_color_definition(b_def)
                speed = hardware_colors.translate_speed(speed_def)

                return Pulse(a, b, speed)
            elif special_color_type == 'palette':
                split = special_color_def.split()
                if len(split) == 1:
                    palette_name = split[0]
                    palette = hardware_colors.palettes.get(palette_name, None)
                    index = (calling_control._context['me']['index']) % len(palette)
                    return palette[index]
                else:
                    if len(split) == 2:
                        try:
                            palette_name = split[0]
                            palette = hardware_colors.palettes.get(palette_name, None)
                            i = int(split[1])
                            index = (calling_control._context['me']['index'] + i) % len(palette)
                            return palette[index]
                        except ValueError:
                            raise ConfigurationError(f'Invalid config `{color}`')
            elif special_color_type == 'midi':
                return parse_color_definition(color['midi'])
            elif special_color_type == 'live':
                # todo: needs Live/controller tranlsation
                pass

            return RgbColor(3)

    except Exception as e:
        raise ConfigurationError(e)


def simplify_color(color):
    return hardware_colors.simplify_color(color)
