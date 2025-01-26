import logging

from ableton.v3.control_surface import (
    ControlSurface
)
from ableton.v2.base.task import TimerTask

from .template_manager import TemplateManager

root_cs = None


class ZCXCore(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.__name = __name__.split('.')[0].lstrip('_')
            from . import ROOT_LOGGER
            self.logger = ROOT_LOGGER
            self.template_manager = TemplateManager(self)
            self.component_map["ZManager"].load_control_templates()
            self.post_init()
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


    def post_init(self):
        try:
            global root_cs
            root_cs = self
            self.log(f'starting HardwareInterface setup')
            self.component_map['HardwareInterface'].setup()
            self.log(f'finished HardwareInterface setup')
            self.log(f'starting ModeManager setup')
            self.component_map['ModeManager'].setup()
            self.log(f'finished ModeManager setup')
            self.log(f'starting ZManager setup')
            self.component_map['ZManager'].setup()
            self.log(f'finished ZManager setup')
            self.log(f'starting PageManager setup')
            self.component_map['PageManager'].setup()
            self.log(f'finished PageManager setup')
        except Exception as e:
            raise e
        self.component_map['HardwareInterface'].refresh_all_lights()

    def port_settings_changed(self):
        super().refresh_state()

    def receive_midi_chunk(self, midi_chunk):
        super().receive_midi_chunk(midi_chunk)
        if midi_chunk[0][0] == 240:
            self.log(f'received sysex chunk {midi_chunk}')
            refresh_task = RefreshLightsTask(self)
            self._task_group.add(refresh_task)
            self.refresh_all_lights()

    def refresh_all_lights(self):
        self.component_map['HardwareInterface'].refresh_all_lights()


class RefreshLightsTask(TimerTask):

    def __init__(self, owner, **k):
        super().__init__(duration=2, **k)
        self._owner = owner
        self.restart()

    def on_finish(self):
        self._owner.refresh_all_lights()
