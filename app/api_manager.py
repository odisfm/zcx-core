from typing import TYPE_CHECKING

from ableton.v3.control_surface import ControlSurface

from .encoder_manager import EncoderManager
from .mode_manager import ModeManager
from .z_manager import ZManager
from .zcx_component import ZCXComponent

if TYPE_CHECKING:
    from .pad_section import PadSection
    from .z_control import ZControl
    from .z_encoder import ZEncoder


class ApiManager(ZCXComponent):

    def __init__(
        self,
        name="ApiManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)

    def setup(self):
        self.log(f'{self.name} doing setup')

    def get_api_object(self):
        return ZcxApi(self.canonical_parent)


class ZcxApi:

    root_cs: ControlSurface
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
