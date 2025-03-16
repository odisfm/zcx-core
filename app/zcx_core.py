import logging
from functools import partial
import traceback

from ableton.v2.base.task import TimerTask
from ableton.v3.control_surface import (
    ControlSurface
)

from .hardware.sysex import LIVE_MODE, USER_MODE, INIT_DELAY, ON_DISCONNECT, AUTO_SWITCH_MODE
from .template_manager import TemplateManager
from .session_ring import SessionRing
from .consts import REQUIRED_LIVE_VERSION
from .errors import ZcxStartupError

root_cs = None


class ZCXCore(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            try:
                self.__name = __name__.split('.')[0].lstrip('_')
                from . import ROOT_LOGGER
                self._logger = ROOT_LOGGER

                self.error = partial(self.log, level='error')
                self.debug = partial(self.log, level='debug')
                self.warning = partial(self.log, level='warning')
                self.critical = partial(self.log, level='critical')

                self.set_logger_level('debug')

                app = self.application
                this_live_version = (app.get_major_version(), app.get_minor_version())

                if (this_live_version[0] > REQUIRED_LIVE_VERSION[0]) or (
                        this_live_version[0] == REQUIRED_LIVE_VERSION[0] and this_live_version[1] >=
                        REQUIRED_LIVE_VERSION[1]
                ):
                    pass
                else:
                    this_version_string = f'{this_live_version[0]}.{this_live_version[1]}'
                    required_version_string = f'{REQUIRED_LIVE_VERSION[0]}.{REQUIRED_LIVE_VERSION[1]}'
                    raise ZcxStartupError(f'zcx requires Live version {required_version_string} or above.',
                                          f'You are using {this_version_string}',
                                          traceback=False, boilerplate=False)

                self.template_manager = TemplateManager(self)
                self.component_map["ZManager"].load_control_templates()

                from . import plugin_loader
                plugin_names = plugin_loader.plugin_names

                self._session_ring_custom = None
                for c in self._components:
                    self.debug(type(c))
                    if isinstance(c, SessionRing):
                        self.debug(f'found the session ring: {c.name}')
                        self._session_ring_custom = c

                self.plugin_map = {}

                for plugin_name in plugin_names:
                    self.plugin_map[plugin_name] = self.component_map[plugin_name]

                self.post_init()

                if AUTO_SWITCH_MODE and USER_MODE is not None:  # todo: preference to stay in Live mode on init
                    if INIT_DELAY > 0:
                        delay = INIT_DELAY / 1000
                        sysex_task = DelayedSysexTask(self, duration=delay, sysex_tuple=USER_MODE)
                        self._task_group.add(sysex_task)
                        sysex_task.restart()
                    else:
                        self._do_send_midi(USER_MODE)
                self.application.add_control_surfaces_listener(self.song_ready)

                self.log(f'{self.name} loaded :)', level='critical')
            except ZcxStartupError:
                raise
            except Exception as e:
                raise ZcxStartupError(str(e))

        except ZcxStartupError as e:
            try:
                self.error(e)

                popup_string = f''

                if e.boilerplate:
                    popup_string += f"{self.name} encountered a fatal error while starting."

                if len(e.msg) > 0:
                    for msg in e.msg:
                        popup_string += f'\n\n{msg}'
                    popup_string += '\n\n'

                popup_string += \
                    (f"The script will now disconnect. "
                     f"Check Live's Log.txt for more details. "
                     f"Get help at www.zcxcore.com/help\n\n")

                if e.traceback:
                    tb_lines = traceback.format_exc().splitlines()
                    relevant_tb = "\n".join(tb_lines[-13:-7])
                    popup_string += f'Traceback: \n\n'
                    popup_string += relevant_tb

                self.show_popup(popup_string)

                self.disconnect()
                self._enabled = False

            except Exception as e:
                logging.getLogger(__name__).error(e)

    @property
    def name(self):
        return self.__name

    @property
    def zcx_api(self):
        return self.component_map["ApiManager"].get_api_object()

    def log(self, *msg, level='info'):
        method = getattr(self._logger, level)
        for m in msg:
            method(m)
            
    def set_logger_level(self, level):
        level = getattr(logging, level.upper())
        self._logger.setLevel(level)

    def setup(self):
        super().setup()


    def post_init(self):
        try:
            global root_cs
            root_cs = self
            self.debug(f'starting HardwareInterface setup')
            self.component_map['HardwareInterface'].setup()
            self.debug(f'finished HardwareInterface setup')
            self.debug(f'starting ModeManager setup')
            self.component_map['ModeManager'].setup()
            self.debug(f'finished ModeManager setup')
            self.debug(f'starting ZManager setup')
            self.component_map['ZManager'].setup()
            self.debug(f'finished ZManager setup')
            self.debug(f'starting PageManager setup')
            self.component_map['PageManager'].setup()
            self.debug(f'finished PageManager setup')
            self.debug(f'starting EncoderManager setup')
            self.component_map['EncoderManager'].setup()
            self.debug(f'finished EncoderManager setup')
            self.debug(f'starting ApiManager setup')
            self.component_map['ApiManager'].setup()
            self.debug(f'finished ApiManager setup')
            self.debug(f'starting ActionResolver setup')
            self.component_map['ActionResolver'].setup()
            self.debug(f'finished ActionResolver setup')
            self.debug(f'doing setup on plugins')
            for plugin_name, plugin_instance in self.plugin_map.items():
                self.debug(f'starting plugin {plugin_name} setup')
                plugin_instance.setup()
                self.debug(f'finished plugin {plugin_name} setup')

        except Exception as e:
            raise e
        self.component_map['HardwareInterface'].refresh_all_lights()

    def song_ready(self):
        self.application.remove_control_surfaces_listener(self.song_ready)
        self.component_map['EncoderManager'].bind_all_encoders()

    def port_settings_changed(self):
        super().refresh_state()
        self.refresh_required()

    def refresh_required(self):
        refresh_task = RefreshLightsTask(self, duration=0.2)
        self._task_group.add(refresh_task)

    def receive_midi_chunk(self, midi_chunk):
        super().receive_midi_chunk(midi_chunk)
        if midi_chunk[0][0] == 240:
            sysex_message = midi_chunk[0]
            if sysex_message == USER_MODE:
                self.refresh_required()

            self.invoke_all_plugins('receive_sysex', midi_bytes=sysex_message)

    def refresh_all_lights(self):
        self.component_map['HardwareInterface'].refresh_all_lights()
        self.invoke_all_plugins('refresh_feedback')

    def show_popup(self, message):
        self.application.show_on_the_fly_message(message)

    def invoke_all_plugins(self, method_name: str, **k):
        self.debug(f'invoking all plugins: {method_name}')
        for plugin_name, plugin_instance in self.plugin_map.items():
            method = getattr(plugin_instance, method_name, None)
            if method is None:
                self.debug(f'plugin {plugin_name} has no method {method_name}')
            method(**k)

class RefreshLightsTask(TimerTask):

    def __init__(self, owner, duration=1, **k):
        super().__init__(duration=duration)
        self._owner = owner
        self.restart()

    def on_finish(self):
        self._owner.refresh_all_lights()

class DelayedSysexTask(TimerTask):

    def __init__(self, owner, duration=1, sysex_tuple=tuple(), **k):
        super().__init__(duration=duration)
        self._owner: ZCXCore = owner
        self.sysex_tuple = sysex_tuple
        self.restart()

    def on_finish(self):
        self._owner._do_send_midi(self.sysex_tuple)

