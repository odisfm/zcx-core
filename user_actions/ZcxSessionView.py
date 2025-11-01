# https://github.com/odisfm/zcx-core
from functools import partial
from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from ClyphX_Pro.clyphx_pro.ClyphX_ProComponent import logger

if TYPE_CHECKING:
    from ..app.api_manager import ZcxApi, ZCXCore

FIXED_RECORD_VAR_NAME = "zcx_fixed_record"

class ZcxSessionView(UserActionsBase):

    def __init__(self, *a, **k):
        UserActionsBase.__init__(self, *a, **k)
        self.__logger = logger.getChild('Zcx')
        self.set_logger_level('info')

        self.error = partial(self.log, level='error')
        self.debug = partial(self.log, level='debug')
        self.critical = partial(self.log, level='critical')

    def cxp_action(self, action_list):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)

    def log(self, *msg, level='info'):
        log_method = getattr(self.__logger, level)
        for msg in msg:
            log_method(f'{self.name}: {msg}')

    def set_logger_level(self, level):
        import logging
        level = getattr(logging, level.upper())
        self.__logger.setLevel(level)

    def create_actions(self):
        self.add_track_action('sview', self.action_entry_point)

    def action_entry_point(self, action_def, args):
        try:

            target_track = action_def["track"]
            if not args:
                raise RuntimeError('No arguments provided')
            _args = args.split()

            target_slot_idx = int(_args.pop(0)) - 1
            target_slot = target_track.clip_slots[target_slot_idx]
            sub_action = _args.pop(0)

            match sub_action:
                case 'press':
                    if target_slot.is_group_slot:
                        self.cxp_action(
                            f'"{target_track.name}" / PLAY {target_slot_idx + 1}'
                        )
                    elif target_track.can_be_armed and target_track.arm and not target_slot.has_clip:
                        fixed_record = self.canonical_parent.clyphx_pro_component._user_variables.get(FIXED_RECORD_VAR_NAME, "0")
                        if fixed_record == '0':
                            self.cxp_action(
                                f'"{target_track.name}" / PLAY {target_slot_idx + 1}'
                            )
                        else:
                            self.cxp_action(
                                f'"{target_track.name}" / RECFIX %{FIXED_RECORD_VAR_NAME}% {target_slot_idx + 1}'
                            )

                    else:
                        self.cxp_action(
                            f'"{target_track.name}" / PLAY {target_slot_idx + 1}'
                        )

        except Exception as e:
            self.critical(f"{e.__class__.__name__}: {e}")
