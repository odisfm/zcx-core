import copy

from ableton.v2.base.event import EventObject, listenable_property
from ableton.v3.control_surface import Component, ControlSurface

from .errors import ConfigurationError, CriticalConfigurationError
from .hardware_interface import HardwareInterface
from .z_manager import ZManager
from .encoder_manager import EncoderManager


class ApiManager(Component, EventObject):

    canonical_parent: ControlSurface

    def __init__(
        self,
        name="ApiManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER

        self._logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.log(f'{self.name} loaded')
        self._encoders = {}

    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)

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

    def get_control_group(self, group_name):
        return self.z_manager.get_control_group(group_name)

    def get_encoder_group(self, group_name):
        return self.encoder_manager.get_encoder_group(group_name)

    def get_named_control(self, control_name):
        return self.z_manager.get_named_control(control_name)

    def get_encoder(self, encoder_name):
        return self.encoder_manager.get_encoder(encoder_name)

    def get_matrix_section(self, section_name):
        return self.z_manager.get_matrix_section(section_name)

    def get_matrix_section_controls(self, section_name):
        return self.get_matrix_section(section_name).owned_controls
