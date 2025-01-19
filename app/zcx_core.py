import logging

from ableton.v3.control_surface import (
    ControlSurface
)


class ZCXCore(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.__name = __name__.split('.')[1]
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(logging.INFO)
            self.log(f'{self.name} loaded :)', level='critical')

        except Exception as e:
            try:
                self.logger.critical(e)
            except Exception:
                logging.getLogger(__name__).critical(e)

    @property
    def name(self):
        return self.__name

    def log(self, message: [str, object], level: [str] = 'info') -> None:
        method = getattr(self.logger, level)
        method(message)

    def setup(self):
        super().setup()
        self.init()

    def init(self):
        pass

    def port_settings_changed(self):
        super().refresh_state()
