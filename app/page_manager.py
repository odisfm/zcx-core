import copy

from ableton.v3.control_surface import Component
from ableton.v2.base.event import EventObject, listenable_property

from .errors import ConfigurationError, HardwareSpecificationError
from .pad_section import PadSection

MATRIX_MIN_NOTE = 0
MATRIX_MAX_NOTE = 0
MATRIX_WIDTH = 0
MATRIX_HEIGHT = 0


class PageManager(Component, EventObject):

    def __init__(
            self,
            name="PageManager",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        from .yaml_loader import yaml_loader
        self.yaml_loader = yaml_loader
        self._logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.log(f'{self.__class__.__name__} initialized')

    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)

    def setup(self):
        self.log('setup')
        sections_config = self.load_sections_config()
        pages_config = self.load_pages_config()

        if pages_config is None:
            pages_dict = {}
            main = []
            for section in sections_config.keys():
                main.append(section)
            pages_dict['main'] = main
            pages_order = copy.copy(main)
        else:
            pages_dict = copy.copy(pages_config.get('pages'))
            order = pages_config.get('order')
            if order is None:
                order = list(pages_dict.keys())

        self.determine_matrix_specs()

        for page_name, page_sections in pages_dict.items():
            self.validate_page_sections(page_name, page_sections, sections_config)

    def determine_matrix_specs(self):
        global MATRIX_MIN_NOTE, MATRIX_MAX_NOTE, MATRIX_WIDTH, MATRIX_HEIGHT
        hw_interface = self.canonical_parent.component_map['HardwareInterface']
        matrix_element = hw_interface.button_matrix_element
        nested_controls = matrix_element.nested_control_elements()
        MATRIX_WIDTH = matrix_element.width()
        MATRIX_MIN_NOTE = nested_controls[-1]._original_identifier - (MATRIX_WIDTH - 1)
        MATRIX_MAX_NOTE = nested_controls[0]._original_identifier + (MATRIX_WIDTH - 1)
        MATRIX_HEIGHT = len(nested_controls) // MATRIX_WIDTH

    def load_sections_config(self):
        sections = self.yaml_loader.load_yaml('_config/matrix_sections.yaml')
        return sections

    def load_pages_config(self):
        try:
            pages = self.yaml_loader.load_yaml('_config/pages.yaml')
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
        required_fields = ['col_start', 'col_end', 'row_start', 'row_end']

        # Check all required fields exist
        for field in required_fields:
            if field not in section_config:
                raise ConfigurationError(f"Missing required field '{field}' in section {section_name}")

        # Validate row order (must be ascending)
        if section_config['row_start'] > section_config['row_end']:
            raise ConfigurationError(f"Section {section_name}: rows must be ordered from top to bottom (row_start < row_end)")

        # Validate coordinate ranges using hardware-specific bounds
        if not (0 <= section_config['row_start'] < MATRIX_HEIGHT and
                0 <= section_config['row_end'] < MATRIX_HEIGHT):
            raise ConfigurationError(f"Section {section_name}: row coordinates must be between 0 and {MATRIX_HEIGHT - 1}")

        if not (0 <= section_config['col_start'] < MATRIX_WIDTH and
                0 <= section_config['col_end'] < MATRIX_WIDTH):
            raise ConfigurationError(f"Section {section_name}: column coordinates must be between 0 and {MATRIX_WIDTH - 1}")

        if section_config['col_start'] > section_config['col_end']:
            raise ConfigurationError(f"Section {section_name}: col_end must be greater than or equal to col_start")

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
                raise ValueError(f"Page '{page_name}' references undefined section '{section_name}'")

            section = all_sections_config[section_name]
            col_start = section['col_start']
            col_end = section['col_end']
            row_start = section['row_start']
            row_end = section['row_end']

            # Check bounds
            if not (0 <= col_start <= col_end < MATRIX_WIDTH and
                    0 <= row_start <= row_end < MATRIX_HEIGHT):
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
