from copy import deepcopy

from ableton.v3.control_surface import Component
from ableton.v2.base.event import EventObject, listenable_property
from ableton.v3.control_surface.controls import (
    ButtonControl,
    control_matrix
)

from .errors import ConfigurationError, HardwareSpecificationError
from .pad_section import PadSection
from .hardware_interface import HardwareInterface
from .z_state import ZState
from .z_control import ZControl

class ZManager(Component, EventObject):

    def __init__(
            self,
            name="ZManager",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        self.__logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        from . import CONFIG_DIR
        self.__config_dir = CONFIG_DIR
        from .yaml_loader import yaml_loader
        self.__yaml_loader = yaml_loader
        self.__hardware_interface: HardwareInterface = self.canonical_parent.component_map["HardwareInterface"]
        self.__global_control_template = {}
        self.__control_templates = {}

        self.load_control_templates()

    def reinit(self):
        pass

    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)

    def load_control_templates(self):
        try:
            raw_config = self.__yaml_loader.load_yaml(f'{self.__config_dir}/control_templates.yaml')
        except FileNotFoundError:
            raw_config = {}
        if '__global__' in raw_config:
            self.__global_control_template = raw_config.pop('__global__')
        self.__control_templates = raw_config

    def process_pad_section(self, pad_section: PadSection):
        matrix_state: control_matrix = self.__hardware_interface.button_matrix_state

        raw_section_config = self.__yaml_loader.load_yaml(f'{self.__config_dir}/matrix_sections/{pad_section.name}.yaml')

        flat_config = self.flatten_section_config(pad_section, raw_section_config)
        context_config = self.apply_section_context(pad_section, flat_config)

        for i in range(len(context_config)):
            coord = pad_section.owned_coordinates[i]
            item_config = context_config[i]
            state: ZState.State = matrix_state.get_control(coord[0], coord[1])
            control = ZControl(self, pad_section)
            control.bind_to_state(state)
            control.gesture_dict = item_config['actions']
                control.raw_config = context_config[i]

    def flatten_section_config(self, section_obj, raw_config, ignore_global_template=False):
        """Flattens a section configuration by applying templates and processing pad groups."""

        try:
            self.log(f"attempting to flatten pad section {section_obj.name}")

        global_template = self.__global_control_template
        control_templates = self.__control_templates
        flat_config = []
        unnamed_groups = 0

        # handle single dict group section config
        if isinstance(raw_config, dict):
            if 'pad_group' in raw_config:
                # raise ValueError() todo: raise config error with proper message
                raw_config = [raw_config]
            else:
                raw_config = [raw_config] * len(section_obj.owned_coordinates)
        elif not isinstance(raw_config, list):
            raise ValueError()  # todo: raise config error with proper message

        def merge_configs(base, override):
            """Deep merge two configurations, ensuring override values take precedence"""
            merged = deepcopy(base)
            for key, value in override.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = merge_configs(merged[key], value)
                else:
                    merged[key] = deepcopy(value)
            return merged

        def apply_global_template(config):
            """Apply global template to config if not ignored"""
            if not ignore_global_template:
                return merge_configs(deepcopy(global_template), deepcopy(config))
            return deepcopy(config)

        def apply_control_template(config):
            """Apply any specified control template to config"""
            if 'template' not in config:
                return config

            template_name = config.pop('template')
            template = control_templates.get(template_name)
            if template is None:
                raise ValueError(f'Config error in {section_obj.name}: '
                                 f'Specified non-existent template "{template_name}"')

            # Start with the template and override with config
            return merge_configs(deepcopy(template), config)

        for i, item in enumerate(raw_config):
            config = deepcopy(item)

            # Handle single pad configuration
            if 'pad_group' not in config:
                # First apply global template
                base_config = apply_global_template({})
                # Then apply any control template
                if 'template' in config:
                    base_config = merge_configs(base_config, apply_control_template(config))
                # Finally apply the pad's specific config
                final_config = merge_configs(base_config, config)

                final_config['group_context'] = {
                    'group_name': None,
                    'group_index': None
                }
                flat_config.append(final_config)
                continue

            # Handle pad group
            pad_group = config['pad_group']
            group_name = pad_group if isinstance(pad_group, str) else f'{section_obj.name}_group_{unnamed_groups}'
            if not isinstance(pad_group, str):
                unnamed_groups += 1

            group_pads = config.get('pads', [None] * (len(section_obj.owned_coordinates) - i))
            if not isinstance(group_pads, list):
                raise ValueError(f'Config error in {section_obj.name} {group_name}: '
                                 f'If "pads" key is present it must be a list.')

            # Create base group config with correct template inheritance
            group_config = deepcopy(config)
            del group_config['pad_group']
            if 'pads' in group_config:
                del group_config['pads']

            # First apply global template to create base config
            base_config = apply_global_template({})
            # Then apply any group-level template
            if 'template' in group_config:
                base_config = merge_configs(base_config, apply_control_template(group_config))
            # Finally apply the group's specific config
            group_config = merge_configs(base_config, group_config)

            # Process each pad in group
            for j, pad_config in enumerate(group_pads):
                if pad_config is None:
                    # Use group config directly if no pad override
                    member_config = deepcopy(group_config)
                else:
                    # Start with group config
                    member_config = deepcopy(group_config)
                    pad_config = deepcopy(pad_config)

                    # Apply pad-specific template if it exists
                    if 'template' in pad_config:
                        template_config = apply_control_template(pad_config)
                        member_config = merge_configs(member_config, template_config)
                    else:
                        # Just merge the pad's config
                        member_config = merge_configs(member_config, pad_config)

                member_config['group_context'] = {
                    'group_name': group_name,
                    'group_index': j
                }
                flat_config.append(member_config)

        return flat_config

    def apply_section_context(self, section_obj, flat_config):
        self.log(f"attempting to apply context to pad section {section_obj.name}")

        section_context = {
            'section_name': section_obj.name
        }

        processed_config = []

        for i in range(len(flat_config)):
            item = flat_config[i]
            global_y, global_x = section_obj.owned_coordinates[i]

            item_context = deepcopy(section_context)
            item_context.update({
                'global_x': global_x,
                'global_y': global_y,
                'section_x': global_x - section_obj._PadSection__bounds['min_x'],
                'section_y': global_y - section_obj._PadSection__bounds['min_y']
            })

            item['section_context'] = item_context
            processed_config.append(item)

        return processed_config

    def parse_config_color(self, config):

        def parse_speed(speed):
            speed -= 1
            if speed < 0:
                speed = 0
            return [48, 24, 12, 6, 4][speed] if speed in range(0, 5) else 1

        if isinstance(config, str):
            return self.parse_color_string(config)
        elif isinstance(config, int):
            return self.colors.rgb(config) if config in range(0, 128) else None
        elif isinstance(config, dict):
            if 'pulse' in config:
                config = config['pulse']
                a = config.get('a', None)
                b = config.get('b', None)
                if a is None or b is None:
                    raise ValueError(
                        f'Config error: "pulse" color config must contain "a" and "b" keys'
                    )
                a = self.parse_color_string(a)
                b = self.parse_color_string(b)
                speed = config.get('speed', 1)
                return self.colors.pulse(a, b, parse_speed(speed))
            elif 'blink' in config:
                config = config['blink']
                a = config.get('a', None)
                b = config.get('b', None)
                if a is None or b is None:
                    raise ValueError(
                        f'Config error: "blink" color config must contain "a" and "b" keys'
                    )
                speed = config.get('speed', 1)
                return self.colors.blink(a, b, parse_speed(speed))
        raise ValueError(
            f'Config error: Unsupported color config.\n{config}'
        )

    def parse_color_string(self, string):
        self.log(f"trying to parse color string {string}")
        if isinstance(string, int):
            if string in range(0, 128):
                return self.colors.rgb(string)
            return None

        split = string.split(' ')
        if len(split) == 1:
            try:
                c = int(split[0])
                if c in range(0, 128):
                    return self.colors.rgb(c)
                else:
                    return None
            except ValueError:
                c = self.colors.get_named_color(split[0])
                return c
        # todo: the rest
        elif len(split) == 2:
            return colors.rgb(1)


