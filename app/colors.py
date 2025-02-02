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

            if isinstance(special_color_def, str) and '${' in special_color_def:
                from .zcx_core import root_cs
                resolver = root_cs.component_map['ActionResolver']
                parse = resolver.compile(special_color_def, calling_control._vars, calling_control._context)
                if parse[1] != 0:
                    raise ConfigurationError(f'Unparseable color definition: {color}')
                special_color_def = parse[0]

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
                    index_offset = 0
                elif len(split) == 2:
                    index_offset = split[1]
                else:
                    raise ConfigurationError(f'Invalid color definition: {special_color_def}') #todo
                palette_name = split[0]

                context = calling_control._context['me']
                if 'group_index' in context:
                    index = context['group_index']
                    if index is None:
                        index = context['index']
                else:
                    # if this doesn't exist something is seriously wrong
                    index = context['index']

                palette_list = hardware_colors.palettes.get(palette_name)
                if palette_list is None:
                    raise ConfigurationError(f'No palette definition in `zcx/hardware/colors.py` for {palette_name}'
                                             f'\nThe maintainer may not have included it, or it may be misspelled'
                                             f'\n{calling_control.parent_section.name}'
                                             f'\n{calling_control._raw_config}')

                i = (index + index_offset) % len(palette_list)

                return palette_list[i]

            elif special_color_type == 'midi':
                return parse_color_definition(color['midi'])
            elif special_color_type == 'live':
                try:
                    special_color_def = int(special_color_def)
                except ValueError:
                    raise ConfigurationError(f'Invalid color definition: {special_color_def}\n'
                                             f'{calling_control._raw_config}')
                color_index = hardware_colors.live_index_for_midi_index(special_color_def)
                return Color(color_index)

            return RgbColor(3)

    except Exception as e:
        raise ConfigurationError(e)


def simplify_color(color):
    return hardware_colors.simplify_color(color)
