import copy
from typing import TYPE_CHECKING

from ableton.v2.base.event import listenable_property
from .osc_watcher import OscSectionWatcher, OscNamedSectionWatcher

from .errors import ConfigurationError, CriticalConfigurationError
from .pad_section import PadSection
from .zcx_component import ZCXComponent

MATRIX_MIN_NOTE = 0
MATRIX_MAX_NOTE = 0
MATRIX_WIDTH = 0
MATRIX_HEIGHT = 0

if TYPE_CHECKING:
    from .action_resolver import ActionResolver

class PageManager(ZCXComponent):

    def __init__(
        self,
        name="PageManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)

        self.__z_manager: ZManager = self.canonical_parent.component_map["ZManager"]
        self.__raw_sections: Dict[str, Dict] = {}
        self.__current_page = -1
        self.__last_page = -1
        self.__page_count = 1
        self.__pages_sections = {}
        self.__page_names = []
        self.__pad_sections: Dict[PadSection] = {}
        self.__named_button_section: Optional[PadSection] = None
        self.__page_definitions = {}
        self.__action_resolver: ActionResolver = None
        self.__osc_server = None
        self.__osc_address_prefix = None
        self.__osc_address_page_name = None
        self.__osc_address_page_number = None
        self.__does_send_osc = False
        self.__special_sections_config = {
            "__session_view": None,
        }
        self.__does_send_page_change_osc = False
        self.__does_send_matrix_label_osc = None
        self.__does_send_named_label_osc = False
        self.__osc_section_watchers = []

    @listenable_property
    def current_page(self):
        return self.__current_page

    @property
    def current_page_name(self):
        return self.__page_names[self.current_page]

    def increment_page(self, increment=1):
        new_page = (self.__current_page + increment) % self.__page_count
        self.set_page(page_number=new_page)

    def set_page(self, page_number=None, page_name=None):
        initial_page_set = self.__current_page == -1
        incoming_page_num = page_number if page_number is not None else self.__page_names.index(page_name)
        if incoming_page_num < 0 or incoming_page_num >= self.__page_count:
            self.error(f'invalid page number {incoming_page_num}')
            return False
        if incoming_page_num == self.__current_page:
            return True
        self.__last_page = self.__current_page
        self.__current_page = incoming_page_num
        self.notify_current_page()

        if not initial_page_set:
            self.handle_page_commands(self.__current_page, self.__last_page)

        try:
            if self.__does_send_page_change_osc:
                self.__osc_server.sendOSC(self.__osc_address_page_name, self.current_page_name)
                self.__osc_server.sendOSC(self.__osc_address_page_number, self.__current_page)
        except:
            pass

        return True

    def return_to_last_page(self):
        self.set_page(page_number=self.__last_page)

    def get_page_number_from_name(self, name):
        try:
            return self.__page_names.index(name)
        except ValueError:
            return False

    def get_page_name_from_index(self, index):
        return self.__page_names[index]

    def is_valid_page_number(self, page_number):
        return 0 <= page_number < self.__page_count

    def request_page_change(self, page: any = None):
        try:
            page = int(page)
        except ValueError:
            pass
        if isinstance(page, int):
            result = self.set_page(page_number=page)
            return result
        elif isinstance(page, str):
            if page in ["prev", "up"]:
                self.increment_page(-1)
                return True
            elif page in ["next", "down"]:
                self.increment_page(1)
                return True
            else:
                page_num = self.get_page_number_from_name(page)
                if page_num:
                    self.set_page(page_number=page_num)
                    return True
                return False
        else:
            raise ValueError(f"invalid value {page} for request_page_change()")

    def setup(self):
        self.__action_resolver: ActionResolver = self.component_map["ActionResolver"]

        sections_config = self.load_sections_config()  # raw yaml
        pages_config = self.load_pages_config()  # raw yaml

        pages_dict = {}

        if pages_config is None:
            # If no pages config, create default from sections
            main_sections = list(sections_config.keys())
            pages_dict["main"] = {"sections": main_sections}
            pages_order = ["main"]
        else:
            raw_pages = pages_config.get("pages", {})
            # Process each page, handling both list and dict formats
            for page_name, page_def in raw_pages.items():
                if isinstance(page_def, list):
                    pages_dict[page_name] = {"sections": page_def}
                elif isinstance(page_def, dict):
                    if "sections" not in page_def:
                        raise CriticalConfigurationError(f'Pages `{page_name}` missing `sections` key: {page_def}')
                    pages_dict[page_name] = page_def
                else:
                    raise CriticalConfigurationError(f'Malformed page definition for `{page_name}`: {page_def}')

            # Get page order (or use all keys if not specified)
            if "order" in pages_config:
                pages_order = pages_config.get("order", [])
                for page_name in pages_order:
                    if page_name not in pages_dict:
                        raise CriticalConfigurationError(f"Page `{page_name}` specified in order does not exist")
                # Only include pages that are specified in the order
            else:
                pages_order = list(pages_dict.keys())

        self.determine_matrix_specs()

        for page_name, page_def in pages_dict.items():
            self.validate_page_sections(page_name, page_def["sections"], sections_config)

        self.__page_count = len(pages_order)

        for page_name in pages_order:
            if page_name in pages_dict:
                # Store sections list for each page
                self.__pages_sections[page_name] = pages_dict[page_name]["sections"]
                # Store full page definition for additional properties
                self.__page_definitions[page_name] = pages_dict[page_name]
                self.__page_names.append(page_name)

        # Build section objects

        PadSection.root_cs = self.canonical_parent
        PadSection.page_manager = self

        used_sections = set()
        for page_sections in self.__pages_sections.values():
            used_sections.update(page_sections)

        special_section_names = self.__special_sections_config.keys()

        for section_name, section_config in sections_config.items():
            if section_name in used_sections:  # Only build sections that are used
                if section_name in special_section_names:
                    self.__special_sections_config[section_name] = section_config
                    continue
                self.__raw_sections[section_name] = section_config
                section_obj = self.build_section(section_name, section_config)
                self.__pad_sections[section_name] = section_obj

        for section in self.__pad_sections.values():
            self.__z_manager.process_pad_section(section)

        named_pad_section = PadSection(
            "__named_buttons_section", None, {i for i in range(self.__page_count)}, 0
        )

        self.__z_manager.process_named_buttons(named_pad_section)

        self.__osc_server = self.component_map['CxpBridge']._osc_server
        self.__osc_address_prefix = f'/zcx/{self.canonical_parent.name}/page'
        self.__osc_address_page_name = self.__osc_address_prefix + '/name'
        self.__osc_address_page_number = self.__osc_address_prefix + '/number'

        from . import PREF_MANAGER
        osc_prefs = PREF_MANAGER.user_prefs.get('osc_output', {})
        try:
            self.__does_send_page_change_osc = osc_prefs.get('page', False)
            self.__does_send_matrix_label_osc = osc_prefs.get('matrix', False)
            self.__does_send_named_label_osc = osc_prefs.get('controls', False)
        except:
            pass

        if self.__does_send_matrix_label_osc:
            for section_obj in self.__pad_sections.values():
                watcher = OscSectionWatcher(section_obj)
                self.__osc_section_watchers.append(watcher)

        if self.__does_send_named_label_osc:
            named_watcher = OscNamedSectionWatcher(named_pad_section)
            self.__osc_section_watchers.append(named_watcher)

        for watcher in self.__osc_section_watchers:
            watcher.update_osc_labels()

        self.set_page(0)

    def _unload(self):
        self.__raw_sections: Dict[str, Dict] = {}
        self.__current_page = -1
        self.__last_page = -1
        self.__page_count = 1
        self.__pages_sections = {}
        self.__page_names = []
        self.__pad_sections: Dict[PadSection] = {}
        self.__named_button_section: Optional[PadSection] = None
        self.__page_definitions = {}
        self.__osc_server = None
        self.__osc_address_prefix = None
        self.__osc_address_page_name = None
        self.__osc_address_page_number = None
        self.__does_send_osc = False
        self.__special_sections_config = {
            "__session_view": None,
        }
        self.__does_send_page_change_osc = False
        self.__does_send_matrix_label_osc = None
        self.__does_send_named_label_osc = False
        for watcher in self.__osc_section_watchers:
            watcher.disconnect()
        self.__osc_section_watchers = []

    def build_section(self, section_name, section_config):
        matrix_element = self.canonical_parent.component_map[
            "HardwareInterface"
        ].button_matrix_state

        self.validate_section_config(section_name, section_config)

        col_start = section_config["col_start"]
        col_end = section_config["col_end"]
        row_start = section_config["row_start"]
        row_end = section_config["row_end"]

        section_template = section_config.get("template", {})

        control_states = []
        owned_coordinates = []

        for y in range(row_start, row_end + 1):
            for x in range(col_start, col_end + 1):
                state = matrix_element.get_control(y, x)
                if state is None:
                    raise RuntimeError(
                        f"Could not get control state for coordinates ({y}, {x})"
                    )
                control_states.append(state)
                owned_coordinates.append((y, x))

        pages_in = set()

        for page_num, sections_list in enumerate(self.__pages_sections.values()):
            if section_name in sections_list:
                pages_in.add(page_num)

        section_object = PadSection(
            section_name=section_name,
            owned_coordinates=owned_coordinates,
            pages_in=pages_in,
            width=(col_end - col_start + 1),
            raw_template=section_template,
        )

        self._registered_disconnectables.append(section_object)

        return section_object

    def determine_matrix_specs(self):
        global MATRIX_MIN_NOTE, MATRIX_MAX_NOTE, MATRIX_WIDTH, MATRIX_HEIGHT
        hw_interface = self.canonical_parent.component_map["HardwareInterface"]
        matrix_element = hw_interface.button_matrix_element
        nested_controls = matrix_element.nested_control_elements()
        MATRIX_WIDTH = matrix_element.width()
        MATRIX_MIN_NOTE = nested_controls[-1]._original_identifier - (MATRIX_WIDTH - 1)
        MATRIX_MAX_NOTE = nested_controls[0]._original_identifier + (MATRIX_WIDTH)
        MATRIX_HEIGHT = len(nested_controls) // MATRIX_WIDTH

    def load_sections_config(self):
        sections = self.yaml_loader.load_yaml(
            f"{self._config_dir}/matrix_sections.yaml"
        )
        return sections

    def load_pages_config(self):
        try:
            pages = self.yaml_loader.load_yaml(f"{self._config_dir}/pages.yaml")
        except FileNotFoundError:
            pages = None
        return pages

    def handle_page_commands(self, incoming_page_num, outgoing_page_num):
        self.debug(f'incoming_page_num: {incoming_page_num}, outgoing_page_num: {outgoing_page_num}')
        incoming_page_name = self.__page_names[incoming_page_num]
        outgoing_page_name = self.__page_names[outgoing_page_num]

        def get_page_command(page_name, outgoing=False):
            key = 'on_leave' if outgoing else 'on_enter'
            try:
                return self.__page_definitions[page_name].get(key)
            except Exception:
                raise

        def make_context_dict(page_name, page_num):
            return {
                'page': {
                    'name': page_name,
                    'number': page_num,
                }
            }

        incoming_command_bundle = get_page_command(incoming_page_name)
        outgoing_command_bundle = get_page_command(outgoing_page_name, True)


        if incoming_command_bundle:
            incoming_vars = self.__page_definitions[incoming_page_name].get('vars', {})
            context = make_context_dict(incoming_page_name, incoming_page_num)

            self.__action_resolver.execute_command_bundle(
                bundle=incoming_command_bundle,
                vars_dict=incoming_vars,
                context=context
            )

        if outgoing_command_bundle:
            outgoing_vars = self.__page_definitions[outgoing_page_name].get('vars', {})
            context = make_context_dict(incoming_page_name, incoming_page_num)

            self.__action_resolver.execute_command_bundle(
                bundle=outgoing_command_bundle,
                vars_dict=outgoing_vars,
                context=context
            )

    @staticmethod
    def validate_section_config(section_name, section_config):
        """Validates section configuration

        Coordinate system:
        - Origin (0,0) is top-left, corresponding to MIDI note 36
        - X increases left-to-right (0 to MATRIX_WIDTH-1)
        - Y increases top-to-bottom (0 to MATRIX_HEIGHT-1)
        - All coordinates are inclusive
        - Valid note range is MATRIX_MIN_NOTE to MATRIX_MAX_NOTE
        """
        required_fields = ["col_start", "col_end", "row_start", "row_end"]

        # Check all required fields exist
        for field in required_fields:
            if field not in section_config:
                raise ConfigurationError(
                    f"Missing required field '{field}' in section {section_name}"
                )

        # Validate row order (must be ascending)
        if section_config["row_start"] > section_config["row_end"]:
            raise ConfigurationError(
                f"Section {section_name}: rows must be ordered from top to bottom (row_start < row_end)"
            )

        # Validate coordinate ranges using hardware-specific bounds
        if not (
            0 <= section_config["row_start"] < MATRIX_HEIGHT
            and 0 <= section_config["row_end"] < MATRIX_HEIGHT
        ):
            raise ConfigurationError(
                f"Section {section_name}: row coordinates must be between 0 and {MATRIX_HEIGHT - 1}"
            )

        if not (
            0 <= section_config["col_start"] < MATRIX_WIDTH
            and 0 <= section_config["col_end"] < MATRIX_WIDTH
        ):
            raise ConfigurationError(
                f"Section {section_name}: column coordinates must be between 0 and {MATRIX_WIDTH - 1}"
            )

        if section_config["col_start"] > section_config["col_end"]:
            raise ConfigurationError(
                f"Section {section_name}: col_end must be greater than or equal to col_start"
            )

        return True

    @staticmethod
    def validate_page_sections(page_name, page_sections, all_sections_config):
        """Validates that all sections in a page fit within the matrix bounds and don't have invalid overlaps.

        Args:
            page_name: name of the page (for logging)
            page_sections: list of section anmes
            all_sections_config: Raw YAML config containing section definitions with coordinates

        Returns:
            bool: True if all sections are valid, raises ValueError if invalid

        Raises:
            ValueError: If sections overlap or exceed matrix bounds
        """
        # Create a matrix to track which cells are claimed
        # Using None for unclaimed, section name for claimed
        matrix = [[None for x in range(MATRIX_WIDTH)] for y in range(MATRIX_HEIGHT)]

        # Check each section's coordinates
        for section_name in page_sections:
            if section_name not in all_sections_config:
                raise ValueError(
                    f"Page '{page_name}' references undefined section '{section_name}'"
                )

            section = all_sections_config[section_name]
            col_start = section["col_start"]
            col_end = section["col_end"]
            row_start = section["row_start"]
            row_end = section["row_end"]

            # Check bounds
            if not (
                0 <= col_start <= col_end < MATRIX_WIDTH
                and 0 <= row_start <= row_end < MATRIX_HEIGHT
            ):
                raise ValueError(
                    f"Section '{section_name}' in page '{page_name}' has coordinates "
                    f"outside matrix bounds: ({col_start}-{col_end}, {row_start}-{row_end})"
                )

            # Check for overlaps by trying to claim cells
            for row in range(row_start, row_end + 1):
                for col in range(col_start, col_end + 1):
                    existing = matrix[row][col]
                    if existing is not None:
                        raise ValueError(
                            f"Section '{section_name}' overlaps with section '{existing}' "
                            f"at coordinates ({row}, {col}) in page '{page_name}'"
                        )
                    matrix[row][col] = section_name

        return True

    def get_special_section_definition(self, section_type):
        return self.__special_sections_config.get(section_type)
