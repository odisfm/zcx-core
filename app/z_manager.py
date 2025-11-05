from copy import deepcopy, copy
from copy import deepcopy, copy
from typing import Optional

from ableton.v3.control_surface.controls import control_matrix
from .z_controls import ParamControl, KeyboardControl, OverlayControl

from .control_classes import get_subclass as get_control_class
from .errors import ConfigurationError, CriticalConfigurationError
from .hardware_interface import HardwareInterface
from .pad_section import PadSection
from .z_control import ZControl
from .z_state import ZState
from .zcx_component import ZCXComponent
from .encoder_manager import SelectedDeviceWatcher


class ZManager(ZCXComponent):

    def __init__(
        self,
        name="ZManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)

        self.__named_controls_section = None
        self.__hardware_interface: HardwareInterface = (
            self.canonical_parent.component_map["HardwareInterface"]
        )
        self.__global_control_template = {}
        self.__control_templates = {}
        self.__control_groups = {}
        self.__named_controls = {}
        self.__named_control_section: PadSection = None
        self.__overlay_sections: dict[str, PadSection] = {}
        self.__matrix_sections: dict[str, PadSection] = {}
        self.__control_aliases = {}
        self.__all_controls: "list[ZControl]" = []
        self._param_controls: "list[ParamControl]" = []

    @property
    def all_controls(self) -> "list[ZControl]":
        return copy(self.__all_controls)

    @property
    def all_matrix_sections(self) -> "dict[str, PadSection]":
        return copy(self.__matrix_sections)

    @property
    def named_controls_section(self) -> "PadSection":
        return self.__named_controls_section

    @property
    def all_overlay_sections(self) -> "dict[str, OverlaySection]":
        return copy(self.__overlay_sections)

    def setup(self):
        from . import z_controls
        self.load_control_templates()

        ZControl.task_group = self.canonical_parent._task_group
        z_controls.page_manager = self.canonical_parent.component_map["PageManager"]
        z_controls.action_resolver = self.canonical_parent.component_map[
            "ActionResolver"
        ]
        z_controls.mode_manager = self.canonical_parent.component_map["ModeManager"]

    def _unload(self):
        super()._unload()
        self.log("unloading")
        for section in self.__matrix_sections.values():
            section.disconnect()
        self.__global_control_template = {}
        self.__control_templates = {}
        self.__control_groups = {}
        self.__named_controls = {}
        self.__named_control_section: PadSection = None
        self.__matrix_sections: dict[PadSection] = {}
        self.__control_aliases = {}
        self.__all_controls = []

    def reinit(self):
        pass

    def create_named_controls(self):
        page_count = len(self.component_map["PageManager"].all_page_names)
        named_pad_section = PadSection(
            "__named_buttons_section", None, {i for i in range(page_count)}, 0
        )
        self.process_named_buttons(named_pad_section)

        general_overlay_def, overlay_defs = self.load_overlay_definitions()
        for overlay_name, overlay_def in overlay_defs.items():
            general_def_content = general_overlay_def["overlays"][overlay_name]
            layer_def = general_def_content.get("layer", 1)
            if not(isinstance(layer_def, int)):
                raise CriticalConfigurationError(f"Invalid layer for overlay `{overlay_name}`: {layer_def}\nMust be a positive integer.")
            elif layer_def < 1:
                raise CriticalConfigurationError(f"Invalid datatype for layer in overlay `{overlay_name}`: {layer_def}\nMust be a positive integer.")
            section_obj = PadSection(
                f"__named_buttons_section__{overlay_name}", None, {i for i in range(page_count)}, 0, overlay_def, layer_def, overlay_def=general_def_content
            )
            self.process_named_buttons(section_obj, overlay_name)
            section_obj._PadSection__in_view = True


    def add_control_to_group(self, control, group_name):
        if group_name in self.__control_groups:
            self.__control_groups[group_name].append(control)
        else:
            self.__control_groups[group_name] = [control]

    def get_control_group(self, group_name) -> "list[ZControl] | None":
        if group_name in self.__control_groups:
            return self.__control_groups[group_name]
        else:
            self.log(
                f"No control group for {group_name}. Registered groups are:\n"
                f"{self.__control_groups.keys()}"
            )
            return None

    def get_named_control(self, control_name) -> "ZControl | None":
        if control_name in self.__named_controls:
            return self.__named_controls[control_name]
        else:
            self.log(
                f"No control named {control_name}. Registered controls are:\n"
                f"{self.__named_controls.keys()}"
            )
            return None

    def get_matrix_section(self, section_name) -> "PadSection | None":
        if section_name in self.__matrix_sections:
            return self.__matrix_sections[section_name]
        else:
            self.log(
                f"No matrix section for {section_name}. Registered sections are:\n"
                f"{self.__matrix_sections.keys()}"
            )

    def load_control_templates(self):
        manager = self.canonical_parent.template_manager
        self.__control_templates = manager.control_templates
        self.__global_control_template = manager.global_control_template

    def process_pad_section(self, pad_section: PadSection):
        self.debug(f'Processing pad_section {pad_section.name}')

        matrix_state: control_matrix = self.__hardware_interface.button_matrix_state

        try:
            raw_section_config = self.yaml_loader.load_yaml(
            f"{self._config_dir}/matrix_sections/{pad_section.name}.yaml"
            )
        except FileNotFoundError:
            if pad_section._raw_template:
                raw_section_config = {}
            else:
                raise CriticalConfigurationError(f"section `{pad_section.name}` referenced in `matrix_sections.yaml` without corresponding file `matrix_sections/{pad_section.name}.yaml`")

        flat_config = self.flatten_section_config(pad_section, raw_section_config)
        context_config = self.apply_section_context(pad_section, flat_config)

        try:
            for i in range(len(pad_section.owned_coordinates)):
                try:
                    coord = pad_section.owned_coordinates[i]
                    item_config = context_config[i]
                    state: ZState.State = matrix_state.get_control(coord[0], coord[1])
                    control = self.z_control_factory(item_config, pad_section)
                    self.debug(f'instantiated {pad_section.name} control #{i}')
                    control.bind_to_state(state)
                    control.raw_config = context_config[i]
                    control.setup()

                    if "alias" in control.raw_config:
                        if not isinstance(control.raw_config["alias"], str):
                            msg = f'Bad alias for control `{control.name}`, alias must be a string.'
                            from . import STRICT_MODE
                            if STRICT_MODE:
                                raise CriticalConfigurationError(msg)
                            else:
                                self.warning(msg + " Ignoring alias.")

                            alias = None

                        elif "$" in control.raw_config["alias"]:
                            parsed, status = self.component_map["ActionResolver"].compile(
                                control.raw_config["alias"],
                                control._vars,
                                control._context
                            )

                            if status != 0:
                                msg = f'Unparseable template string in alias for control `{control.name}`: {control.raw_config["alias"]}'
                                from . import STRICT_MODE
                                if STRICT_MODE:
                                    raise CriticalConfigurationError(msg)
                                else:
                                    self.warning(msg)
                                    alias = None
                            else:
                                alias = parsed
                        else:
                            alias = control.raw_config["alias"]

                        if alias:
                            alias_lower = alias.lower()
                            if alias_lower != alias:
                                self.warning(
                                    f'Invalid alias `{alias}`: alias must be lowercase. Using `{alias_lower}`'
                                )
                                alias = alias_lower
                            try:
                                self.set_control_alias(alias, control)
                                control._alias = alias
                            except ConfigurationError as e:
                                from . import STRICT_MODE
                                if STRICT_MODE:
                                    raise CriticalConfigurationError(e)
                                else:
                                    self.warning(str(e) + f" Ignoring alias for control `{control.name}`.")

                    self.debug(f'{pad_section.name} control #{i} successfully setup')
                except CriticalConfigurationError:
                    raise
                except Exception as e:
                    from . import STRICT_MODE
                    if STRICT_MODE:
                        raise
                    self.error(e)

        except Exception as e:
            raise

        self.__matrix_sections[pad_section.name] = pad_section

    def flatten_section_config(
            self, section_obj, raw_config, ignore_global_template=False
    ):
        """Flattens a section configuration by applying templates and processing pad groups."""

        try:
            def merge_configs(base, override):
                """Deep merge two configurations, ensuring override values take precedence."""
                if not isinstance(override, dict):
                    return override
                if not isinstance(base, dict):
                    return override
                merged = deepcopy(base)
                for key, value in override.items():
                    if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                        if key == "color":

                            base_color_def = merged["color"]
                            override_color_def = value

                            try:
                                if list(base_color_def.keys())[0] == list(override_color_def.keys())[0]:
                                    merged["color"] = base_color_def | override_color_def
                                else:
                                    merged["color"] = override_color_def
                            except IndexError:
                                merged["color"] = override_color_def

                        else:
                            merged[key] = merge_configs(merged[key], value)
                    else:
                        merged[key] = deepcopy(value)
                return merged

            def apply_global_template(config):
                """Apply global template to config if not ignored."""
                if not ignore_global_template:
                    if not isinstance(config, dict):
                        return config
                    return merge_configs(deepcopy(global_template), config)
                return config

            def apply_control_templates(config):
                """Apply any specified control templates to config."""
                if "template" not in config:
                    return config, False

                template_value = config.pop("template")
                skip_global = False
                result_config = {}

                # Handle template key which can be string, list, or None
                if template_value is None:
                    # No template specified, return empty dict as base
                    skip_global = True
                    return result_config, skip_global
                elif isinstance(template_value, str):
                    # Single template name
                    template = control_templates.get(template_value)
                    if template is None:
                        raise ValueError(
                            f"Config error in {section_obj.name}: "
                            f'Specified non-existent template "{template_value}"'
                        )
                    result_config = deepcopy(template)
                elif isinstance(template_value, list):
                    # List of templates - apply in order (left to right)
                    result_config = {}

                    # Check if first template is None to skip global
                    if template_value and template_value[0] is None:
                        skip_global = True
                        template_value = template_value[1:]  # Skip the None value

                    # Apply templates in order
                    for template_name in template_value:
                        if template_name is not None:  # Skip None values
                            template = control_templates.get(template_name)
                            if template is None:
                                raise ValueError(
                                    f"Config error in {section_obj.name}: "
                                    f'Specified non-existent template "{template_name}"'
                                )
                            result_config = merge_configs(result_config, deepcopy(template))
                else:
                    raise ValueError(
                        f"Config error in {section_obj.name}: "
                        f'Invalid template value "{template_value}"'
                    )

                # Merge with original config
                result_config = merge_configs(result_config, config)
                return result_config, skip_global

            global_template = self.__global_control_template
            control_templates = self.__control_templates

            section_template = section_obj._raw_template
            self.debug(f"{section_obj.name} template: {section_template}")

            if isinstance(section_template, dict):
                section_template = section_template
            else:
                raise ConfigurationError(f"Section {section_obj.name} `template` key must be a dict:\n{raw_config}")

            flat_config = []
            unnamed_groups = 0

            # Handle empty yaml file as empty anonymous group def
            if raw_config is None:
                raw_config = {}

            is_whole_section_group = False

            # Handle single dict group section config
            if isinstance(raw_config, dict):
                is_whole_section_group = True
                if "pad_group" in raw_config:
                    raw_config = [raw_config]
                else:
                    pad_overrides = raw_config.get(
                        "controls", [None] * len(section_obj.owned_coordinates)
                    )
                    group_template = {
                        k: v for k, v in raw_config.items() if k != "controls"
                    }
                    if not group_template.get('skip_section_template', False):
                        group_template = merge_configs(section_template, group_template)
                    raw_config = []

                    for i in range(len(section_obj.owned_coordinates)):
                        override = pad_overrides[i] if i < len(pad_overrides) else None
                        if override is None:
                            raw_config.append(deepcopy(group_template))
                        else:
                            merged = merge_configs(deepcopy(group_template), override)
                            raw_config.append(merged)

            for i, item in enumerate(raw_config):
                config = deepcopy(item)

                if config is None:
                    config = {}
                elif not isinstance(config, dict):
                    raise CriticalConfigurationError(
                        f"Config error in {section_obj.name}. Control definition must be dict or null, provided: {config}  ({type(config)})"
                    )

                # Handle single pad configuration
                if "pad_group" not in config:
                    # Apply templates
                    skip_global = False

                    if not config.get('skip_section_template', False):
                        config = merge_configs(section_template, config)

                    if "template" in config:
                        config, skip_global = apply_control_templates(config)

                    # Apply global template if not skipped
                    if not skip_global:
                        base_config = apply_global_template({})
                        final_config = merge_configs(base_config, config)
                    else:
                        final_config = config

                    final_config["group_context"] = {
                        "group_name": None,
                        "group_index": None,
                        "group_Index": None,
                        "group_count": 0,
                    }
                    flat_config.append(final_config)
                    continue

                # Handle pad group
                pad_group = config["pad_group"]
                group_name = (
                    pad_group
                    if isinstance(pad_group, str)
                    else f"{section_obj.name}_group_{unnamed_groups}"
                )
                group_name_lower = group_name.lower()
                if group_name_lower != group_name:
                    self.warning(f"Group names must be lowercase. Changed `{group_name}` to {group_name_lower}")
                    group_name = group_name_lower
                if not isinstance(pad_group, str):
                    unnamed_groups += 1

                group_pads = config.get(
                    "controls")

                if not group_pads or not isinstance(group_pads, list):
                    if not is_whole_section_group:
                        raise CriticalConfigurationError(
                        f"Error in section `{section_obj.name}` group `{group_name}`:"
                        f"\nA group within a matrix section must have a `controls` option, a list with an entry for each control."
                        f"\nProvided: {group_pads}"
                        )
                    else:
                        group_pads = [None] * (len(section_obj.owned_coordinates) - i)

                if not isinstance(group_pads, list):
                    raise CriticalConfigurationError(
                        f"Config error in {section_obj.name} {group_name}: "
                        f'If "controls" key is present it must be a list.'
                    )

                # Create base group config with correct template inheritance
                group_config = deepcopy(config)
                del group_config["pad_group"]
                if "controls" in group_config:
                    del group_config["controls"]

                # Apply templates
                skip_global = False
                if "template" in group_config:
                    group_config, skip_global = apply_control_templates(group_config)

                # Apply global template if not skipped
                if not skip_global:
                    base_config = apply_global_template({})
                    group_config = merge_configs(base_config, group_config)

                group_count = len(group_pads)

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
                        skip_pad_global = False
                        if "template" in pad_config:
                            template_config, skip_pad_global = apply_control_templates(pad_config)
                            # If pad config says to skip global but group already applied it,
                            # we need to apply just the templates without the global part
                            if skip_pad_global and not skip_global:
                                # This is tricky to handle completely correctly, but we'll merge
                                # the template with the pad config and use that
                                member_config = merge_configs(member_config, template_config)
                            else:
                                member_config = merge_configs(member_config, template_config)
                        else:
                            # Just merge the pad's config
                            member_config = merge_configs(member_config, pad_config)

                    member_config["group_context"] = {
                        "group_name": group_name,
                        "group_index": j,
                        "group_Index": j + 1,
                        "group_count": group_count,
                    }
                    flat_config.append(member_config)
        except Exception as e:
            self.critical(f"failed to parse section `{section_obj.name}` config", raw_config)
            raise

        num_coords = len(section_obj.owned_coordinates)
        num_in_config = len(flat_config)
        num_missing = num_coords - num_in_config

        if num_missing < 0:
            raise CriticalConfigurationError(
                f"{section_obj.name}: Too many ({num_in_config}) controls in config. Section has {num_coords} controls.")
        elif num_missing > 0:
            dummy_control = {
                "color": 1,
                "gestures": {
                    "pressed": f'msg "This control definition is missing from {section_obj.name}.yaml !"',
                }
            }
            for i in range(num_missing):
                flat_config.append(dummy_control)

            self.warning(
                f"{num_missing} controls missing from {section_obj.name}.yaml — dummy controls have been added.")

        return flat_config

    def apply_section_context(self, section_obj, flat_config):

        try:
            section_context = {"section_name": section_obj.name}

            processed_config = []

            if section_obj.bounds is not None:
                section_height = section_obj.bounds["height"]
                section_width = section_obj.bounds["width"]
            else:
                section_height = 0
                section_width = 0

            for i in range(len(flat_config)):
                item = flat_config[i]
                global_y, global_x = section_obj.owned_coordinates[i]
                global_Y = global_y + 1
                global_X = global_x + 1
                global_y_flip = (global_y - section_height) * -1 -1
                global_x_flip = (global_x - section_width) * -1 -1
                global_Y_flip = global_y_flip + 1
                global_X_flip = global_x_flip + 1
                x = global_x - section_obj._PadSection__bounds["min_x"]
                y = global_y - section_obj._PadSection__bounds["min_y"]
                X = x + 1
                Y = y + 1
                x_flip =  global_x_flip - section_obj._PadSection__bounds["min_x"] * -1
                y_flip = global_y_flip - section_obj._PadSection__bounds["min_y"] * -1
                X_flip = x_flip + 1
                Y_flip = y_flip + 1
                item_context = deepcopy(section_context)
                item_context.update(
                    {
                        "index": i,
                        "global_x": global_x,
                        "global_y": global_y,
                        "global_X": global_X,
                        "global_Y": global_Y,
                        "global_y_flip": global_y_flip,
                        "global_x_flip": global_x_flip,
                        "global_Y_flip": global_Y_flip,
                        "global_X_flip": global_X_flip,
                        "x": x,
                        "y": y,
                        "X": X,
                        "Y": Y,
                        "x_flip": x_flip,
                        "y_flip": y_flip,
                        "X_flip": X_flip,
                        "Y_flip": Y_flip,
                    }
                )

                item["section_context"] = item_context
                processed_config.append(item)

            return processed_config

        except Exception as e:
            self.log(e)

    def process_named_buttons(self, pad_section: PadSection, overlay: Optional[str] = None):
        if overlay:
            this_file = f"{overlay}.yaml"
            path = f"overlays/{this_file}"
        else:
            this_file = f"named_controls.yaml"
            path = this_file
        raw_config = self.yaml_loader.load_yaml(
            f"{self._config_dir}/{path}"
        )

        parsed_config = self.parse_named_button_config(pad_section, raw_config, False, this_file)

        hardware = self.__hardware_interface

        for button_name, button_def in parsed_config.items():
            try:
                try:
                    state: ZState.State = getattr(hardware, f'_button_{button_name}')
                except AttributeError:
                    raise CriticalConfigurationError(
                        f'`{this_file}` specifies control called `{button_name}` which does not exist.'
                    )
                formatted_name = f'{button_name}{"" if not overlay else f"_{overlay}"}'
                control = self.z_control_factory(button_def, pad_section, formatted_name)
                control.bind_to_state(state)
                control.setup()
                self.__named_controls[formatted_name] = control
            except CriticalConfigurationError as e:
                raise
            except Exception as e:
                from . import STRICT_MODE
                if STRICT_MODE:
                    raise
                self.error(e)

        if not overlay:
            self.__named_controls_section = pad_section
        else:
            self.__overlay_sections[overlay] = pad_section

    def parse_named_button_config(
            self, pad_section: PadSection, raw_config: dict, ignore_global_template=False, this_file=None
    ) -> dict:
        working_control_name = None
        working_control_def = None
        try:
            if not isinstance(raw_config, dict):
                raw_config = {}

            ungrouped_buttons = {}
            groups = {}

            # Separate grouped and ungrouped buttons
            for item_name, item_def in raw_config.items():
                working_control_name = item_name
                working_control_def = item_def
                if item_name.startswith("__"):
                    if item_name in groups:
                        raise ConfigurationError(f"Multiple definitions for {item_name} in {this_file}")
                    groups[item_name] = item_def
                else:
                    if item_name in ungrouped_buttons:
                        raise ConfigurationError(f"Multiple definitions for {item_name} in {this_file}")
                    ungrouped_buttons[item_name] = item_def

            global_template = self.__global_control_template
            control_templates = self.__control_templates

            def merge_configs(base, override):
                """Deep merge two configurations, ensuring override values take precedence"""
                if not isinstance(override, dict):
                    return override
                if not isinstance(base, dict):
                    return override
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
                    if not isinstance(config, dict):
                        return config
                    return merge_configs(deepcopy(global_template), config)
                return config

            def apply_control_templates(config):
                """Apply any specified control templates to config"""
                if "template" not in config:
                    return config, False

                template_value = config.pop("template")
                skip_global = False
                result_config = {}

                # Handle template key which can be string, list, or None
                if template_value is None:
                    # No template specified, return empty dict as base
                    skip_global = True
                    return result_config, skip_global
                elif isinstance(template_value, str):
                    # Single template name
                    template = control_templates.get(template_value)
                    if template is None:
                        raise ValueError(
                            f'Specified non-existent template "{template_value}" in "{this_file}"'
                        )
                    result_config = deepcopy(template)
                elif isinstance(template_value, list):
                    # List of templates - apply in order (left to right)
                    result_config = {}

                    # Check if first template is None to skip global
                    if template_value and template_value[0] is None:
                        skip_global = True
                        template_value = template_value[1:]  # Skip the None value

                    # Apply templates in order
                    for template_name in template_value:
                        if template_name is not None:  # Skip None values
                            template = control_templates.get(template_name)
                            if template is None:
                                raise ValueError(
                                    f'Specified non-existent template "{template_name}" in "{this_file}"'
                                )
                            result_config = merge_configs(result_config, deepcopy(template))
                else:
                    raise ValueError(
                        f'Invalid template value "{template_value}" in "{this_file}"'
                    )

                # Merge with original config
                result_config = merge_configs(result_config, config)
                return result_config, skip_global

            # Process ungrouped buttons
            processed_ungrouped = {}
            for button_name, button_def in ungrouped_buttons.items():
                working_control_name = button_name
                working_control_def = button_def
                config = deepcopy(button_def)
                if config is None:
                    config = {}

                # Apply templates
                skip_global = False
                if "template" in config:
                    config, skip_global = apply_control_templates(config)

                # Apply global template if not skipped
                if not skip_global:
                    config = apply_global_template(config)

                processed_ungrouped[button_name] = config

            # Process grouped buttons
            for group_name, group_def in groups.items():
                group_config = deepcopy(group_def)

                # Apply templates to the group config
                skip_global = False
                if "template" in group_config:
                    group_config, skip_global = apply_control_templates(group_config)

                # Apply global template if not skipped
                if not skip_global:
                    group_config = apply_global_template(group_config)

                processed_sub_buttons = {}

                for sub_button in group_config.get("includes", []):
                    sub_button_config = deepcopy(group_config)

                    button_overrides = group_config.get("controls", {})
                    if button_overrides and sub_button in button_overrides:
                        override_def = deepcopy(button_overrides[sub_button])

                        # Check if the override has its own template
                        if "template" in override_def:
                            override_template_config, override_skip_global = apply_control_templates(override_def)
                            # If override says to skip global but group already applied it,
                            # we just use the override template config
                            merged_def = merge_configs(sub_button_config, override_template_config)
                        else:
                            merged_def = merge_configs(sub_button_config, override_def)
                    else:
                        merged_def = sub_button_config

                    for key in ["includes", "controls"]:
                        merged_def.pop(key, None)

                    processed_sub_buttons[sub_button] = merged_def

                cleaned_group_name = group_name[2:]
                group_count = len(processed_sub_buttons.values())

                for i, (name, _def) in enumerate(processed_sub_buttons.items()):
                    group_context = {"group_name": cleaned_group_name, "group_index": i, "group_Index": i+1, "group_count": group_count}
                    _def["group_context"] = group_context
                    processed_ungrouped[name] = _def

            return processed_ungrouped

        except Exception as e:
            raise CriticalConfigurationError(f"Bad definition for control `{working_control_name}` in `{this_file}`: "
                                             f"\nControl definition: "
                                             f"\n{working_control_def}\n"
                                             f"\n{str(e)}") from e

    def z_control_factory(self, config, pad_section, button_name=None) -> ZControl:
        try:
            control = None
            control_type = config.get("type") or "standard"
            try:
                control_cls = get_control_class(control_type)
            except ValueError:
                raise CriticalConfigurationError(f"Error in pad section `{pad_section.name}`, no control type `{control_type}`")

            self.debug(f'creating control:', config)

            control = control_cls(self.canonical_parent, pad_section, config, button_name)
            if "group_context" in config:
                if "group_name" in config["group_context"]:
                    self.add_control_to_group(
                        control, config["group_context"]["group_name"]
                    )

        except ConfigurationError as e:
            from . import STRICT_MODE

            name = f"`{button_name}`" if button_name is not None else f"in section {pad_section.name}"

            if STRICT_MODE is True:
                raise CriticalConfigurationError(f"Bad definition for control {name}: "
                                                 f"\nControl definition: "
                                                 f"\n{config}\n"
                                                 f"\n{str(e)}") from e
            else:
                self.critical(
                    f"Bad definition for control {name}: "
                    f"\nControl definition: "
                    f"\n{config}\n"
                    f"\n{str(e)}")

                self.critical(f"As strict mode is disabled, this failed control has been replaced with a blank control")
                control = get_control_class("standard")(self.canonical_parent, pad_section, {"color": 0}, button_name)

        self.__all_controls.append(control)

        return control

    def set_control_alias(self, alias, control):
        if alias in self.__control_aliases:
            raise ConfigurationError(f'multiple controls with alias `{alias}`.')
        if alias in self.__named_controls:
            raise ConfigurationError(f'Canonical control already exists called `{alias}`. You cannot use this name.')
        self.__control_aliases[alias] = control

    def get_aliased_control(self, alias) -> "ZControl | None":
        return self.__control_aliases.get(alias)

    def song_ready(self):
        """
        Some controls rely on objects that are not ready when the control is created,
        so we iterate over every control and call necessary methods based on the control's class
        """
        selected_device_watcher = SelectedDeviceWatcher(self, self._song)
        ParamControl.selected_device_watcher = selected_device_watcher
        for control in self.__all_controls:
            try:
                if isinstance(control, ParamControl):
                    control.bind_to_active()
                    self._param_controls.append(control)
                if isinstance(control, KeyboardControl):
                    control.finish_setup()
                if isinstance(control, OverlayControl):
                    control.finish_setup()
            except Exception as e:
                from . import STRICT_MODE
                msg = f"Error finishing control setup in section `{control.parent_section.name}` control `{control.name}`"
                if STRICT_MODE:
                    self.critical(msg)
                    self.critical(e)
                    raise e
                else:
                    self.error(msg)
                    self.error(e)

    def load_overlay_definitions(self):

        try:
            general_def = self.yaml_loader.load_yaml(f"{self._config_dir}/overlays.yaml")
        except FileNotFoundError as e:
            self.warning(f"No file called `{self._config_dir}/overlays.yaml`")
            return {}, {}
        if general_def is None:
            self.warning(f"`overlays.yaml` is empty")
            return {}, {}

        overlay_defs: dict[str, dict] = {}

        overlays_obj = general_def.get("overlays")
        overlay_names = list(overlays_obj.keys())
        for i, name in enumerate(overlay_names):
            lower_name = name.lower()
            if lower_name != name:
                self.warning(f"Overlay `{name}` was renamed to `{lower_name}")
                overlay_names[i] = lower_name

        if overlays_obj is None:
            self.warning(f"Key `overlays` in `overlays.yaml` is missing")
            return {}, {}
        elif not isinstance(overlays_obj, dict):
            raise CriticalConfigurationError(f"Key `overlays` in `overlays.yaml` must be a dict:\n{overlays_obj}")
        elif len(overlay_names) == 0:
            self.warning(f"Dict `overlays` in `overlays.yaml` is empty")
            return {}, {}

        for overlay_name in overlay_names:
            try:
                obj = self.yaml_loader.load_yaml(f"{self._config_dir}/overlays/{overlay_name.lower()}.yaml")
                if obj is None:
                    self.warning(f"File `{self._config_dir}/overlays/{overlay_name}.yaml is empty")
                    overlay_defs[overlay_name] = {}
                elif not isinstance(obj, dict):
                    raise CriticalConfigurationError(f"File `{self._config_dir}/overlays/{overlay_name}.yaml must be a dict (is `{obj.__class__.__name__}`):\n{obj}")
            except FileNotFoundError as e:
                raise CriticalConfigurationError(f"`overlays.yaml` specifies overlay name `{overlay_name}` but missing file `{self._config_dir}/overlays/{overlay_name}.yaml`")
            overlay_defs[overlay_name] = obj

        return general_def, overlay_defs

    def register_special_section_object(self, pad_section: PadSection, name: str):
        self.__matrix_sections[name] = pad_section

    def refresh_all_bindings(self):
        for control in self._param_controls:
            control.refresh_binding()
