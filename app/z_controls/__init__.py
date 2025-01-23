from typing import Optional

from ..action_resolver import ActionResolver
from ..page_manager import PageManager
from ..mode_manager import ModeManager

from .basic_z_control import BasicZControl
from .page_control import PageControl

action_resolver:ActionResolver = Optional[None]
page_manager:PageManager = Optional[None]
mode_manager:ModeManager = Optional[None]

__all__ = ["BasicZControl", "PageControl"]
