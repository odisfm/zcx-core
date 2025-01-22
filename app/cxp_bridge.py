from ableton.v3.control_surface import ControlSurface, Component
from ableton.v3.live import liveobj_valid
from .consts import CXP_NAME


class CxpBridge(Component):

    def __init__(
            self,
            name="CxpBridge",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        from . import ROOT_LOGGER
        self.__logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.__clyph_x = None
        self.__live = self.application
        self.get_clyph_x()

    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)

    def get_clyph_x(self):
        if self.__clyph_x is not None:
            if liveobj_valid(self.__clyph_x):
                self.log('Clyph X is valid')
                return
            else:
                self.__clyph_x = None

        cs_list = list(self.__live.control_surfaces)
        cxp = None

        for cs in cs_list:
            if cs.__class__.__name__ == CXP_NAME:
                cxp = cs
                break

        if cxp is None:
            raise RuntimeError(f"Could not connect to {CXP_NAME}. Is it selected as a control surface in Live?")

        self.__clyph_x = cxp.clyphx_pro_component
        self.log(f'Connected to {CXP_NAME}')

    def trigger_action_list(self, action_list):
        if self.__clyph_x is None:
            raise RuntimeError(f"Not connected to {CXP_NAME}. Is it selected as a control surface in Live?")

        self.__clyph_x.trigger_action_list(action_list)
