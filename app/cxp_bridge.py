from ableton.v3.live import liveobj_valid
from ableton.v3.base import listens

from .consts import CXP_NAME
from .zcx_component import ZCXComponent


class CxpBridge(ZCXComponent):

    def __init__(
            self,
            name="CxpBridge",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        self.__clyph_x = None
        self.__live = self.application
        self._osc_server = None
        self.get_clyph_x()
        self.__log_action_lists = True

    def setup(self):
        from . import PREF_MANAGER
        prefs = PREF_MANAGER.user_prefs
        log_action_lists = prefs.get('action_log', True)
        if not type(log_action_lists) is bool:
            self.error(f'Invalid option for `action_log`: {log_action_lists}')
            log_action_lists = True
        self.__log_action_lists = log_action_lists
        self._on_control_surfaces_changed.subject = self.canonical_parent.application

    def get_clyph_x(self):

        try:
            cs_list = list(self.__live.control_surfaces)
            cxp = None

            for cs in cs_list:
                if cs.__class__.__name__ == CXP_NAME:
                    cxp = cs
                    break

            if cxp is None:
                raise RuntimeError(f"Could not connect to {CXP_NAME}. Is it selected as a control surface in Live?")

            self.__clyph_x = cxp.clyphx_pro_component
            try:
                self._osc_server = self.__clyph_x.osc_server
                from .osc_watcher import OscWatcher
                OscWatcher._osc_server = self._osc_server

            except AttributeError:
                self.error(f'{CXP_NAME} OSC server not found.')

            self.log(f'Connected to {CXP_NAME}')
        except Exception as e:
            self.__clyph_x = None
            self.critical(e)

    def trigger_action_list(self, action_list):
        if self.__clyph_x is None:
            raise RuntimeError(f"Can't trigger action list!:\n"
                               f"Not connected to {CXP_NAME}. Is it selected as a control surface in Live?")

        self.__clyph_x.trigger_action_list(action_list)

        if self.__log_action_lists:
            self.log(f'did action list: `{action_list}`')

    def get_cxp_variable(self, name):
        if self.__clyph_x is None:
            raise RuntimeError(f"Not connected to {CXP_NAME}.")

        try:
            return self.__clyph_x._user_variables[name]
        except KeyError:
            return None

    @listens("control_surfaces")
    def _on_control_surfaces_changed(self):
        self.get_clyph_x()