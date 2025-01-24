import copy

from ableton.v2.base.event import EventObject, listenable_property
from ableton.v3.control_surface import Component, ControlSurface
from .errors import ConfigurationError
from .pad_section import PadSection

MATRIX_MIN_NOTE = 0
MATRIX_MAX_NOTE = 0
MATRIX_WIDTH = 0
MATRIX_HEIGHT = 0

CONFIG_DIR = None


class PageManager(Component, EventObject):

    canonical_parent: ControlSurface

    def __init__(
        self,
        name="PageManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        from . import CONFIG_DIR as config_dir

        global CONFIG_DIR
        CONFIG_DIR = config_dir
        from .yaml_loader import yaml_loader

        self.yaml_loader = yaml_loader
        self._logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.__z_manager: ZManager = self.canonical_parent.component_map["ZManager"]
        self.__raw_sections: Dict[str, Dict] = {}
        self.__current_page = -1
        self.__page_count = 1
        self.__pages_sections = {}
        self.__page_names = []
        self.__pad_sections: Dict[PadSection] = {}
        self.__named_button_section: Optional[PadSection] = None

    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)

    @listenable_property
    def current_page(self):
        return self.__current_page

    def increment_page(self, increment=1):
        new_page = (self.__current_page + increment) % self.__page_count
        self.set_page(page_number=new_page)

    def set_page(self, page_number=None, page_name=None):
        if page_name in self.__page_names:
            self.__current_page = self.__page_names.index(page_name)
            self.notify_current_page()
            return True
        elif type(page_number) is int and self.__page_count > page_number >= 0:
            self.__current_page = page_number
            self.notify_current_page()
            return True
        else:
            raise ValueError(f"invalid value {page_number or page_name} for set_page()")

    def get_page_number_from_name(self, name):
        try:
            return self.__page_names.index(name)
        except ValueError:
            return False

    def is_valid_page_number(self, page_number):
        return 0 <= page_number < self.__page_count

    def request_page_change(self, page:any=None):
        try:
            page = int(page)
        except ValueError:
            pass
        if isinstance(page, int):
            result = self.set_page(page_number=page)
            return result
        elif isinstance(page, str):
            if page in ['prev', 'up']:
                self.increment_page(-1)
                return True
            elif page in ['next', 'down']:
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
        sections_config = self.load_sections_config()
        pages_config = self.load_pages_config()

        if pages_config is None:
            pages_dict = {}
            main = []
            for section in sections_config.keys():
                main.append(section)
            pages_dict["main"] = main
            pages_order = copy.copy(main)
        else:
            pages_dict = copy.copy(pages_config.get("pages"))
            pages_order = pages_config.get("order")
            if pages_order is None:
                pages_order = list(pages_dict.keys())

        self.determine_matrix_specs()

        for page_name, page_sections in pages_dict.items():
            self.validate_page_sections(page_name, page_sections, sections_config)

        self.__page_count = len(pages_dict)

        for page_name in pages_order:
            try:
                self.__pages_sections[page_name] = pages_dict[page_name]
                self.__page_names.append(page_name)
            except KeyError:
                continue

        # build section objects
        PadSection.root_cs = self.canonical_parent
        PadSection.page_manager = self

        for section_name, section_config in sections_config.items():
            self.__raw_sections[section_name] = section_config
            section_obj = self.build_section(section_name, section_config)
            self.__pad_sections[section_name] = section_obj

        for section in self.__pad_sections.values():
            self.__z_manager.process_pad_section(section)

        named_pad_section = PadSection(
            "__named_buttons_section", None, {i for i in range(self.__page_count)}, 0
        )

        self.__z_manager.process_named_buttons(named_pad_section)

        self.set_page(0)

    def build_section(self, section_name, section_config):
        matrix_element = self.canonical_parent.component_map[
            "HardwareInterface"
        ].button_matrix_state

        self.validate_section_config(section_name, section_config)

        col_start = section_config["col_start"]
        col_end = section_config["col_end"]
        row_start = section_config["row_start"]
        row_end = section_config["row_end"]

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
            width=(row_end - row_start + 1),
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
        sections = self.yaml_loader.load_yaml(f"{CONFIG_DIR}/matrix_sections.yaml")
        return sections

    def load_pages_config(self):
        try:
            pages = self.yaml_loader.load_yaml(f"{CONFIG_DIR}/pages.yaml")
        except FileNotFoundError:
            pages = None
        return pages

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
