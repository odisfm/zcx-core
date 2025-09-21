# https://github.com/odisfm/zcx-core
from functools import partial
from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from ClyphX_Pro.clyphx_pro.ClyphX_ProComponent import logger

if TYPE_CHECKING:
    from ..app.api_manager import ZcxApi, ZCXCore


class Zcx(UserActionsBase):

    def __init__(self, *a, **k):
        UserActionsBase.__init__(self, *a, **k)
        self.__logger = logger.getChild('Zcx')
        self.set_logger_level('info')

        self.__slots_to_scripts = {
            0: None,
            1: None,
            2: None,
            3: None,
            4: None,
            5: None,
        }

        self.__names_to_scripts: dict[str, "ZcxApi"] = {}

        self.error = partial(self.log, level='error')
        self.debug = partial(self.log, level='debug')
        self.critical = partial(self.log, level='critical')

    def log(self, *msg, level='info'):
        log_method = getattr(self.__logger, level)
        for msg in msg:
            log_method(f'{self.name}: {msg}')

    def set_logger_level(self, level):
        import logging
        level = getattr(logging, level.upper())
        self.__logger.setLevel(level)

    def create_actions(self):
        self.add_global_action('zcx', self.action_entry_point)

    def on_control_surface_scripts_changed(self, scripts):
        self.debug(f'scripts: {scripts}')

        cs_list = list(self.canonical_parent.application().control_surfaces)

        self.__names_to_scripts = {}

        for i, cs in enumerate(cs_list):
            if self.is_zcx_script(cs):
                api = cs.zcx_api
                self.__slots_to_scripts[i] = api
                self.__names_to_scripts[api.script_name] = api
                self.debug(f'found zcx script: {api.script_name}')
            else:
                self.__slots_to_scripts[i] = None


        self.debug(f'scripts: {cs_list}')

    def is_zcx_script(self, script):
        return script is not None and hasattr(script, 'zcx_api')

    def action_entry_point(self, action_def: dict[str], args: str):
        try:
            _args = args.split()
            sub_action = _args[1]

            target_def = _args[0]
            target_slot = None

            if target_def.isdigit():
                try:
                    target_slot = int(target_def)
                    target_script = self.__slots_to_scripts[target_slot - 1]
                except KeyError:
                    raise RuntimeError(f'Control surface slot {target_slot} does not seem to contain a zcx script.', self.__slots_to_scripts)
                except ValueError:
                    raise RuntimeError(f'Something went seriously wrong parsing `ZCX {args}`')
            else:
                try:
                    target_script = self.__names_to_scripts[target_def]
                except KeyError:
                    raise RuntimeError(f'No zcx script named {target_def}.', self.__names_to_scripts)

            if sub_action == 'page':
                target_script.request_page_change(page=_args[2])
            elif sub_action == 'mode':
                mode_args = _args[2:]
                status = mode_args[0]
                mode_name = mode_args[1]

                if status == 'on':
                    target_script.add_mode(mode_name)
                elif status == 'off':
                    target_script.remove_mode(mode_name)
                elif status == 'tgl':
                    target_script.toggle_mode(mode_name)
            elif sub_action == "overlay":
                overlay_args = _args[2:]
                status = overlay_args[0]
                overlay_name = overlay_args[1]

                if status == 'on':
                    target_script.view_manager.enable_overlay(overlay_name)
                elif status == 'off':
                    target_script.view_manager.disable_overlay(overlay_name)
                elif status == 'tgl':
                    target_script.view_manager.toggle_overlay(overlay_name)

            elif sub_action == 'set_color':
                color_args = _args[2:]
                target_control_def = color_args[0]
                target_color = color_args[1]

                target_control_def.strip('"')

                control_obj = target_script.get_control(target_control_def)
                control_obj.set_color(target_color)
                control_obj.request_color_update()

            elif sub_action in ['set_section_color', 'set_group_color']:
                color_args = _args[2:]
                list_def = color_args[0]
                target_color = color_args[1]

                if sub_action == 'set_section_color':
                    control_list = target_script.get_matrix_section(list_def).owned_controls
                elif sub_action == 'set_group_color':
                    control_list = target_script.get_control_group(list_def)
                else:
                    raise ValueError()

                if target_color == "initial":
                    for control in control_list:
                        control.reset_color_to_initial()
                        control.request_color_update()
                else:
                    for i, control in enumerate(control_list):
                        control.set_color(target_color)
                        control.request_color_update()

            elif sub_action == 'msg':
                message_portion = args.split('"')[1] # will fix
                target_script.write_display_message(message_portion)

            elif sub_action.startswith("bind"):
                target_name = _args[2]
                bind_def = args.split('"')[1]
                bind_def = bind_def.replace('`', '"')
                target_obj = target_script.get_control_or_encoder(target_name)
                if target_obj is None:
                    raise RuntimeError(f'Encoder {target_name} does not exist on {target_script.name}.')
                try:
                    if sub_action == 'bind':
                        target_obj.bind_ad_hoc(bind_def)
                    else:
                        modes_portion = sub_action[5:]
                        target_obj.override_binding_definition(bind_def, unparsed_mode_string= modes_portion)
                except AttributeError as e:
                    self.log(f'`{target_name}` is not a bindable control', e, level="error")
                except Exception as e:
                    self.log(f"error binding `{target_name}`", e, level="error")

            elif sub_action == 'refresh':
                target_script.refresh()

            elif sub_action == 'hw_mode':
                mode_def = _args[2]
                target_script.set_hardware_mode(mode_def)

            elif sub_action == 'hot_reload':
                target_script.root_cs.hot_reload()

            else:
                raise ValueError(f'Unknown action {sub_action}')
        except Exception as e:
            self.error(e)
