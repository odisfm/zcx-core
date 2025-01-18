import logging

from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin
)
from .elements import Elements
from .skin import Skin


def create_mappings(control_surface):
    mappings = {}

    return mappings


class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    create_mappings_function = create_mappings


class ZCXCore(ControlSurface):

    def __init__(self, *a, **k):
        global ROOT_CS_LOGGER
        super().__init__(*a, **k)
        try:
            self.name = __name__.split('.')[1]
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(logging.INFO)
            ROOT_CS_LOGGER = self.logger
            self.log(f'{self.name} loaded :)', level='critical')

        except Exception as e:
            try:
                self.logger.critical(e)
            except Exception:
                logging.getLogger(__name__).critical(e)

    def log(self, message, level='info'):
        method = getattr(self.logger, level)
        method(message)

    def setup(self):
        super().setup()
        self.init()

    def init(self):
        pass

    def port_settings_changed(self):
        super().refresh_state()
