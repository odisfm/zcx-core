import logging
from functools import partial
import traceback

from ableton.v2.base.task import TimerTask
from ableton.v3.control_surface import (
    ControlSurface
)

from .hardware.sysex import LIVE_MODE, USER_MODE, INIT_DELAY, ON_DISCONNECT
from .template_manager import TemplateManager
from .session_ring import SessionRing
from .consts import REQUIRED_LIVE_VERSION
from .errors import ZcxStartupError, ConfigurationError

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

                from . import PREF_MANAGER
                user_prefs = PREF_MANAGER.user_prefs

                self.__refresh_on_all_sysex = user_prefs.get('refresh_on_all_sysex', False)
                initial_hw_mode = user_prefs.get('initial_hw_mode', 'zcx')
                self.__initial_hw_mode = initial_hw_mode

                self.template_manager = TemplateManager(self)

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

                from .osc_watcher import OscWatcher
                OscWatcher.address_prefix = f'/zcx/{self.name}/'

                self.post_init()

                if initial_hw_mode == 'zcx' and USER_MODE is not None:
                    if INIT_DELAY > 0:
                        delay = INIT_DELAY / 1000
                        sysex_task = DelayedSysexTask(self, duration=delay, sysex_tuple=USER_MODE)
                        self._task_group.add(sysex_task)
                        sysex_task.restart()
                    else:
                        self._do_send_midi(USER_MODE)
                self.application.add_control_surfaces_listener(self.song_ready)

                from .yaml_loader import yaml_loader
                zcx_yaml = yaml_loader.load_yaml('zcx.yaml')
                self.debug(zcx_yaml)
                version = zcx_yaml.get('version')

                if version is None or version == "0.0.0":
                    version_string = ''
                    self.__version = None
                else:
                    version_string = f"v{version} "
                    self.__version = version

                self.log(f'{self.name} {version_string}loaded :)', level='critical')
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

                try:
                    self._logger.critical(popup_string)
                    self._logger.critical(traceback.format_exc())
                    self._logger.critical(e)
                except AttributeError:
                    pass

                self.show_popup(popup_string)

                self.disconnect()
                self._enabled = False

            except Exception as e:
                logging.getLogger(__name__).error(e)
                raise

    @property
    def name(self):
        return self.__name

    @property
    def zcx_api(self):
        if not self._enabled:
            raise RuntimeError(f'{self.name} is not enabled.')
        return self.component_map["ApiManager"].get_api_object()

    @property
    def version(self):
        return self.__version

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
            self.debug(f'starting CxpBridge setup')
            self.component_map['CxpBridge'].setup()
            self.debug(f'finished CxpBridge setup')
            self.debug(f'starting ActionResolver setup')
            self.component_map['ActionResolver'].setup()
            self.debug(f'finished ActionResolver setup')
            self.debug(f'starting SessionRing setup')
            self._session_ring_custom.setup()
            self.debug(f'finished SessionRing setup')
            self.component_map['SessionView'].setup()
            self.debug(f'starting SessionView setup')
            self.debug(f'finished SessionView setup')
            self.debug(f'doing setup on plugins')
            for plugin_name, plugin_instance in self.plugin_map.items():
                try:
                    self.debug(f'starting plugin {plugin_name} setup')
                    plugin_instance.setup()
                    self.debug(f'finished plugin {plugin_name} setup')
                except Exception as e:
                    self.critical(f'{plugin_name} plugin setup failed:', e)

            from . import PREF_MANAGER
            user_prefs = PREF_MANAGER.user_prefs
            startup_command = user_prefs.get('startup_command')
            try:
                if startup_command is not None:
                    self.log("doing startup command", startup_command)
                    self.component_map["ActionResolver"].execute_command_bundle(None, startup_command, {}, {})
            except Exception as e:
                self.critical(e)

            startup_page = user_prefs.get('startup_page')
            if startup_page is not None:
                try:
                    if isinstance(startup_page, str) and "${" in startup_page:
                        startup_page, status = self.component_map["ActionResolver"].compile(startup_page, {}, {})
                        if not status == 0:
                            raise ValueError(f"Couldn't parse template string")
                    success = self.component_map["PageManager"].request_page_change(startup_page)
                    if not success:
                        raise ConfigurationError(f"Invalid startup_page: {startup_page}")
                except Exception as e:
                    self.critical(e)
                    self.component_map['PageManager'].set_page(0)
            else:
                self.component_map['PageManager'].set_page(0)

        except Exception as e:
            self.critical(e)
            raise
        self.component_map['HardwareInterface'].refresh_all_lights()

    def hot_reload(self):
        try:
            self.log("doing hot reload")
            self.log("unloading components")
            self.template_manager = TemplateManager(self)
            from . import PREF_MANAGER
            PREF_MANAGER.setup()
            self.component_map["HardwareInterface"]._unload()
            self.component_map["ZManager"]._unload()
            self.component_map["PageManager"]._unload()
            self.component_map["EncoderManager"]._unload()
            self._session_ring_custom._unload()
            self.component_map["SessionView"]._unload()
            self.log("doing setup on components")
            self.post_init()
            self.log("finishing setup")
            self.song_ready()
            self.refresh_required()
            self.log("hot reload complete")
        except Exception as e:
            self.critical(e)
            self.critical("Hot reload failed. You should perform a full reload.")
            self.show_message("Hot reload failed. You should perform a full reload.")

    def song_ready(self):
        if self.application.control_surfaces_has_listener(self.song_ready):
            self.application.remove_control_surfaces_listener(self.song_ready)
        self.component_map['EncoderManager'].bind_all_encoders()
        self.component_map['ZManager'].song_ready()

    def port_settings_changed(self):
        if not self._enabled:
            return
        super().refresh_state()
        self.refresh_required()

        if self.__initial_hw_mode == 'live':
            pass
        elif self.__initial_hw_mode == 'zcx':
            self.set_hardware_mode('zcx', 1)

    def refresh_required(self, duration=0.2):
        refresh_task = RefreshLightsTask(self, duration)
        self._task_group.add(refresh_task)

    def receive_midi_chunk(self, midi_chunk):
        super().receive_midi_chunk(midi_chunk)
        if self._enabled and midi_chunk[0][0] == 240:
            sysex_message = midi_chunk[0]
            self.debug(f'received sysex: {sysex_message}')
            if self.__refresh_on_all_sysex or sysex_message == USER_MODE:
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

    def set_hardware_mode(self, mode: str, wait=0.2):
        if mode == 'live':
            sysex = LIVE_MODE
        elif mode == 'zcx':
            sysex = USER_MODE
        else:
            raise ValueError(f'Invalid hardware mode `{mode}`')

        task = DelayedSysexTask(self, wait, sysex)
        self._task_group.add(task)
        task.restart()

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

