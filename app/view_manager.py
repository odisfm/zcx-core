import copy
from typing import TYPE_CHECKING

from ableton.v2.base.event import listenable_property

from .errors import ConfigurationError, CriticalConfigurationError
from .pad_section import PadSection
from .zcx_component import ZCXComponent

if TYPE_CHECKING:
    from .action_resolver import ActionResolver


class ViewManager(ZCXComponent):

    def __init__(
        self,
        name="ViewManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)

    def setup(self):
        pass

    def _unload(self):
        pass
