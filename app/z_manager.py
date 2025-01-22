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
from .z_controls.basic_z_control import BasicZControl
from .control_classes import get_subclass as get_control_class

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

        try:
            for i in range(len(pad_section.owned_coordinates)):
                coord = pad_section.owned_coordinates[i]
                item_config = context_config[i]
                state: ZState.State = matrix_state.get_control(coord[0], coord[1])
                control = self.z_control_factory(item_config, pad_section)
                control.bind_to_state(state)
                control.gesture_dict = item_config['actions']
                control.raw_config = context_config[i]
                control.set_color_to_base()
        except Exception as e:
            self.log(e)

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
        except Exception as e:
            self.log(f'failed to parse section {section_obj.name} config', raw_config)
            raise e

        return flat_config

    def apply_section_context(self, section_obj, flat_config):

        try:
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

        except Exception as e:
            self.log(e)

    def process_named_buttons(self, pad_section: PadSection):
        self.log(f"processing named buttons for section {pad_section.name}")

        raw_config = self.__yaml_loader.load_yaml(f'{self.__config_dir}/named_buttons.yaml')
        if raw_config is None:
            self.log('warning, named_buttons.yaml appears to be empty')  # todo: change logging level

        parsed_config = self.parse_named_button_config(pad_section, raw_config)

        hardware = self.__hardware_interface

        for button_name, button_def in parsed_config.items():
            state: ZState.State = getattr(hardware, button_name)
            control = self.z_control_factory(button_def, pad_section)
            control.bind_to_state(state)
            control.gesture_dict = button_def['gestures']
            self.log(f'setting color for {button_name}')
            control.set_color_to_base()

    def parse_named_button_config(self, pad_section: PadSection, raw_config: dict,
                                  ignore_global_template=False) -> dict:
        try:
            ungrouped_buttons = {}
            groups = {}

            for item_name, item_def in raw_config.items():
                if item_name.startswith('__'):
                    if item_name in groups:
                        raise ConfigurationError(f'Multiple definitions for {item_name}')
                    groups[item_name] = item_def
                else:
                    if item_name in ungrouped_buttons:
                        raise ConfigurationError(f'Multiple definitions for {item_name}')
                    ungrouped_buttons[item_name] = item_def

            global_template = self.__global_control_template
            control_templates = self.__control_templates
            flat_config = {}

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

            for group_name, group_def in groups.items():
                group_config = deepcopy(group_def)
                group_config = apply_global_template(group_config)
                group_template_name = group_config.pop('template', None)
                template_def = control_templates.get(group_template_name, {})
                group_config = merge_configs(template_def, group_config)

                processed_sub_buttons = {}

                for sub_button in group_config.get('includes', []):
                    sub_button_config = deepcopy(group_config)

                    button_overrides = group_config.get('buttons', {})
                    if button_overrides and sub_button in button_overrides:
                        override_def = deepcopy(button_overrides[sub_button])
                        merged_def = merge_configs(sub_button_config, override_def)
                    else:
                        merged_def = sub_button_config

                    for key in ['includes', 'buttons']:
                        merged_def.pop(key, None)

                    processed_sub_buttons[sub_button] = merged_def

                for i, (name, _def) in enumerate(processed_sub_buttons.items()):
                    group_context = {}
                    group_name = group_name[2:]
                    group_context['group_name'] = group_name
                    group_context['group_index'] = i

                    _def.update(group_context)
                    ungrouped_buttons[name] = _def

            return ungrouped_buttons

        except Exception as e:
            raise e

    def z_control_factory(self, config, pad_section) -> ZControl:
        control_type = config.get('type') or 'basic'
        control_cls = get_control_class(control_type)

        if control_cls is None:
            raise ValueError(f"Control class for type '{control_type}' not found")

        control = control_cls(self, pad_section)
        return control

