from copy import copy, deepcopy
from typing import TYPE_CHECKING, Any

from ableton.v3.control_surface import ControlSurface
from ableton.v3.control_surface.elements.color import Color

from .encoder_manager import EncoderManager
from .mode_manager import ModeManager
from .z_manager import ZManager
from .zcx_component import ZCXComponent
from .colors import parse_color_definition

if TYPE_CHECKING:
    from .pad_section import PadSection
    from .z_control import ZControl
    from .z_encoder import ZEncoder
    from .zcx_core import ZCXCore
    from .page_manager import PageManager


class ApiManager(ZCXComponent):

    def __init__(
        self,
        name="ApiManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)

    def setup(self):
        self.debug(f'{self.name} doing setup')

    def get_api_object(self):
        return ZcxApi(self.canonical_parent)


class ZcxApi:

    root_cs: 'ZCXCore'
    z_manager: ZManager
    encoder_manager: EncoderManager

    def __init__(self, root_cs, *a, **k):
        super().__init__()
        self.root_cs = root_cs
        self.z_manager = self.root_cs.component_map['ZManager']
        self.encoder_manager = self.root_cs.component_map['EncoderManager']
        self.page_manager: PageManager = self.root_cs.component_map['PageManager']
        self.mode_manager: ModeManager = self.root_cs.component_map['ModeManager']

        self.request_page_change = self.page_manager.request_page_change
        self.set_page = self.page_manager.set_page
        self.increment_page = self.page_manager.increment_page
        self.add_mode = self.mode_manager.add_mode
        self.remove_mode = self.mode_manager.remove_mode
        self.toggle_mode = self.mode_manager.toggle_mode

    @property
    def script_name(self):
        return self.root_cs.name

    def get_control_group(self, group_name) -> list['ZControl']:
        return self.z_manager.get_control_group(group_name)

    def get_encoder_group(self, group_name) -> list['ZEncoder']:
        return self.encoder_manager.get_encoder_group(group_name)

    def get_named_control(self, control_name) -> 'ZControl':
        return self.z_manager.get_named_control(control_name)

    def get_encoder(self, encoder_name) -> 'ZEncoder':
        return self.encoder_manager.get_encoder(encoder_name)

    def get_matrix_section(self, section_name) -> 'PadSection':
        return self.z_manager.get_matrix_section(section_name)

    def get_matrix_section_controls(self, section_name) -> list['ZControl']:
        return self.get_matrix_section(section_name).owned_controls

    def get_control(self, control_name) -> 'Optional[ZControl]':
        return self.z_manager.get_aliased_control(control_name) or self.get_named_control(control_name)

    def create_color(self, color_def: Any, calling_control: 'ZControl'=None) -> Color:
        """
        Takes a color_def in normal zcx format and returns a Color object.
        Needs a calling_control to make use of certain features and definition types.
        :param color_def:
        :param calling_control:
        :return:
        """
        try:
            return parse_color_definition(color_def, calling_control)
        except Exception as e:
            self.root_cs

    def refresh(self):
        self.root_cs.refresh_all_lights()

    def set_hardware_mode(self, mode_def):
        self.root_cs.set_hardware_mode(mode_def)

    @property
    def plugin_map(self):
        return copy(self.root_cs.plugin_map)

    @property
    def page(self):
        return self.page_manager.current_page

    @property
    def page_name(self):
        return self.page_manager.current_page_name

    @property
    def modes(self):
        return self.mode_manager.current_modes

    @property
    def active_modes(self):
        return self.mode_manager.active_modes

    @property
    def name(self) -> str:
        return self.root_cs.name
