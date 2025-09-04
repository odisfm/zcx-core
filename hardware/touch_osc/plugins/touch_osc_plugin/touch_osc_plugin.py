from typing import TYPE_CHECKING
from collections import Counter

from ableton.v3.base import EventObject
from ableton.v3.base import listens_group, listens
from ableton.v2.base.task import TimerTask
from util import to_percentage

if TYPE_CHECKING:
    from app.zcx_core import ZCXCore
    from app.zcx_plugin import ZCXPlugin
    from app.z_encoder import ZEncoder
    from app.encoder_manager import EncoderManager
    from app.session_ring import SessionRing
    from app.cxp_bridge import CxpBridge

class TouchOscPlugin(ZCXPlugin):

    def __init__(
            self,
            name="TouchOscPlugin",
            *a,
            **k
    ):
        super().__init__(name, *a, **k)
        self._persistent_message = ''
        self.cxp: "Optional[CxpBridge]" = None
        self._base_osc_address = ""

    def setup(self):
        super().setup()
        self.cxp: 'CxpBridge' = self.canonical_parent.component_map["CxpBridge"]
        self._base_osc_address = f"/zcx/{self.canonical_parent.name}/message_box"
        self.add_api_method('write_display_message', self.receive_message_from_ua)

    def receive_message_from_ua(self, message):
        self.cxp._osc_server.sendOSC(self._base_osc_address, message)
