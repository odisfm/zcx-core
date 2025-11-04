import re
from functools import partial
from itertools import chain
from typing import Dict, Any, Tuple, Callable, Union
from random import randint

from .util import DynamicString
from .vendor.asteval import Interpreter, make_symbol_table

from ableton.v3.base import listens, listens_group
from ClyphX_Pro.clyphx_pro import ParseUtils

from .cxp_bridge import CxpBridge
from .hardware.sysex import USER_MODE, LIVE_MODE
from .hardware_interface import HardwareInterface
from .mode_manager import ModeManager
from .page_manager import PageManager
from .z_control import ZControl
from .zcx_component import ZCXComponent
from .colors import parse_color_definition
from .errors import ConfigurationError

ABORT_ON_FAILURE = True # todo: add to preferences.yaml


class DotDict:
    """Helper class to allow dot notation access to nested dictionaries"""

    def __init__(self, data):
        self._data = data

    def __getattr__(self, key):
        if key in self._data:
            value = self._data[key]
            if isinstance(value, dict):
                return DotDict(value)
            if isinstance(value, list):
                return [DotDict(x) if isinstance(x, dict) else x for x in value]
            return value
        raise AttributeError(key)

    def __getitem__(self, key):
        value = self._data[key]
        if isinstance(value, dict):
            return DotDict(value)
        if isinstance(value, list):
            return [DotDict(x) if isinstance(x, dict) else x for x in value]
        return value


class ActionResolver(ZCXComponent):

    def __init__(
            self,
            name="ActionResolver",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)

        self.__pattern = re.compile(r"\\\$\\{|\\\${|\$\\{|\${([^{}\\]*)}")
        self.__page_manager: PageManager = self.canonical_parent.component_map['PageManager']
        self.__mode_manager: ModeManager = self.canonical_parent.component_map['ModeManager']
        self.__cxp: CxpBridge = self.canonical_parent.component_map['CxpBridge']
        self.__hardware_interface: HardwareInterface = self.canonical_parent.component_map['HardwareInterface']
        self.__ring_api = None
        self.__zcx_api_obj = None
        self.__log_func = lambda *args: self.log(*args)
        self.__msg_func = lambda message: self.canonical_parent.show_message(message)
        self.__interpreter = Interpreter()
        self.__cxp_partial = None
        self.__standard_context = {}

    def setup(self):
        self.__ring_api = self.canonical_parent._session_ring_custom.api
        self.__zcx_api_obj = self.component_map['ApiManager'].get_api_object()
        self.__cxp_partial = partial(self.__cxp.trigger_action_list)
        self.__standard_context = self.__build_standard_context()


    def __build_standard_context(self) -> dict[str: Any]:

        context = {
            'song': self.canonical_parent.song,
            'ring': self.__ring_api,
            'zcx': self.__zcx_api_obj,
            'print': self.__log_func,
            'msg': self.__msg_func,
            'cxp': self.__cxp_partial,
            'open': None,
            'cxp_var': self.__cxp.get_cxp_variable,
            'this_cs': self.canonical_parent.name,
            'sel_track': SelectedTrackNameGetter(self._song.view)
        }
        return context

    def _evaluate_expression(
            self, expr: str, context: Dict[str, Any], prior_resolved: Dict[str, Any]
    ) -> Tuple[Any, int]:
        """Evaluate a Python expression with given context and locals."""
        try:
            if expr.startswith("$"):
                expr = expr[1:]

            exec_context = self.__build_symtable(context, prior_resolved)
            self.__interpreter.symtable = exec_context
            result = self.__interpreter.eval(expr)
            if len(self.__interpreter.error) > 0:
                self.error(f"Error evaluating expression `{expr}`")
                for error in self.__interpreter.error:
                    self.error(error)
                return None, 2
            return result, 0
        except Exception as e:
            print(f"Error evaluating {expr}: {e}")
            return None, 2

    def _resolve_vars(
        self, vars: Dict[str, Any], context: Dict[str, Any], mode: str
    ) -> Tuple[Dict[str, Any], int]:
        """Resolve variables in order, checking for $ patterns and dependencies."""
        resolved = {}

        for var_name, expr in vars.items():
            expr = str(expr) if not isinstance(expr, str) else expr

            try:
                result, status = self._evaluate_expression(expr, context, resolved)
                if status != 0:
                    return {}, 2

                resolved[var_name] = result
            except Exception as e:
                print(f"Error resolving {var_name}: {e}")
                return {}, 2

        return resolved, 0

    def __build_symtable(self, context: Dict[str, Any], prior_resolved: Dict[str, Any]) -> Dict[str, Any]:
        """Build a comprehensive execution context with all available variables and functions."""
        dot_context = {
            k: DotDict(v) if isinstance(v, dict) else v for k, v in context.items()
        }

        extra = {}

        try:
            calling_control = context.get('me', {}).get('obj', None)

            if calling_control is None:
                parse_color = partial(parse_color_definition)
            else:
                parse_color = partial(parse_color_definition, calling_control=calling_control)
            extra['parse_color'] = parse_color

        except Exception as e:
            self.debug(e)

        exec_context = make_symbol_table(**dot_context, **prior_resolved, **self.__standard_context)
        return exec_context

    def _replace_match(
        self,
        match: re.Match,
        resolved_vars: Dict[str, Any],
        context: Dict[str, Any],
        mode: str,
    ) -> Tuple[str, int]:
        """Process a single pattern match."""

        full_match = match.group(0)
        if full_match.startswith("\\"):
            return full_match, 0

        var_name = match.group(1)
        if not var_name:
            return full_match, 0

        if var_name in resolved_vars:
            value = resolved_vars[var_name]
        else:
            result, status = self._evaluate_expression(var_name, context, resolved_vars)
            if status != 0:
                return match.group(0), 2
            value = result

        return str(value), 0

    def compile(
        self,
        action_string: str,
        vars: Dict[str, str],
        context: Dict[str, Any],
        mode: str='live',
    ) -> Tuple[str, int]:
        """Compile an action string, resolving variables and template patterns."""
        # self.log(action_string, vars, context, mode)
        if not isinstance(action_string, str) or "${" not in action_string:
            return action_string, 0

        resolved_vars, status = self._resolve_vars(vars, context, mode)
        if status != 0:
            return action_string, status

        result = ""
        last_end = 0

        for match in self.__pattern.finditer(action_string):
            result += action_string[last_end : match.start()]

            replacement, match_status = self._replace_match(
                match, resolved_vars, context, mode
            )
            if match_status != 0:
                return action_string, match_status

            result += replacement
            last_end = match.end()

        result += action_string[last_end:]
        # self.log(result)
        return result, 0

    def parse_command_bundle(self, command_bundle: Any) -> list:
        if isinstance(command_bundle, str):
            return [command_bundle]
        elif callable(command_bundle):
            return [command_bundle]
        elif isinstance(command_bundle, list):
            # Recursively parse each item and flatten
            return list(chain.from_iterable(
                self.parse_command_bundle(item) for item in command_bundle
            ))
        elif isinstance(command_bundle, dict):
            return [{k: v} for k, v in command_bundle.items()]
        else:
            raise ValueError

    def _compile_and_check(self, command_str: str, vars_dict: dict = None, context: dict = None):
        """Helper to compile commands and handle errors consistently"""
        parsed, status = self.compile(command_str, vars_dict, context)
        if status != 0:
            error_msg = (f"Couldn't parse command: {command_str}\n"
                         f"{context},"
                         f"{vars_dict}")
            self.log(error_msg)
            if ABORT_ON_FAILURE:
                raise RuntimeError(error_msg)
            return None
        return parsed

    def execute_command_bundle(
            self,
            calling_control: ZControl = None,
            bundle: list[Union[list, str, dict, Callable]] = None,
            vars_dict: dict = None,
            context: dict = None,
    ):
        try:
            commands = self.parse_command_bundle(bundle)

            for command in commands:
                if isinstance(command, str):
                    if parsed := self._compile_and_check(command, vars_dict, context):
                        self.__cxp.trigger_action_list(parsed)

                elif isinstance(command, dict):
                    command_type, command_def = command.popitem()

                    match command_type:
                        case 'cxp':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                self.__cxp.trigger_action_list(parsed)
                        case 'log':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                self.log(parsed)
                        case 'msg':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                self.canonical_parent.show_message(parsed)
                        case 'page':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                if parsed == 'last':
                                    self.__page_manager.return_to_last_page()
                                    continue
                                result = self.__page_manager.request_page_change(parsed)
                                if not result:
                                    if ABORT_ON_FAILURE:
                                        raise RuntimeError(f'invalid page change: {parsed}')
                                    return False
                        case 'mode':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                self.__mode_manager.toggle_mode(parsed)
                        case 'mode_on':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                self.__mode_manager.add_mode(parsed)
                        case 'mode_off':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                self.__mode_manager.remove_mode(parsed)
                        case "overlay":
                            overlay_def = list(command_def.items())[0]
                            def_type = overlay_def[0]
                            overlay_name_def = overlay_def[1]
                            parsed_overlay = self._compile_and_check(overlay_name_def, vars_dict, context)
                            if not parsed_overlay:
                                raise RuntimeError(f'unparseable overlay definition: {overlay_name_def}')
                            if def_type == "enable":
                                self.component_map["ViewManager"].enable_overlay(parsed_overlay)
                            elif def_type == "disable":
                                self.component_map["ViewManager"].disable_overlay(parsed_overlay)
                            elif def_type == "toggle":
                                self.component_map["ViewManager"].toggle_overlay(parsed_overlay)

                        case 'refresh':
                            self.canonical_parent.manual_refresh()
                        case 'hardware_mode':
                            if command_def == 'user':
                                bytes = USER_MODE
                            elif command_def == 'live':
                                bytes = LIVE_MODE
                            else:
                                raise RuntimeError(f'invalid hardware mode: {command_def}')
                            self.canonical_parent._do_send_midi(bytes)
                        case 'ring':
                            self.debug(command_type, command_def, vars_dict, context)

                            ring_component = self.canonical_parent._session_ring_custom

                            x_parsed = None
                            y_parsed = None
                            track_def_parsed = None
                            scene_def_parsed = None

                            if isinstance(command_def, str):
                                command_def, status = self.compile(command_def, vars_dict, context)
                                if status != 0:
                                    raise RuntimeError(f"Couldn't parse command: {command_type}: {command_def}")

                            if isinstance(command_def, str):
                                try:
                                    match (command_def.lower()):
                                        case 'left':
                                            x_parsed = -1
                                        case 'right':
                                            x_parsed = 1
                                        case 'up':
                                            y_parsed = -1
                                        case 'down':
                                            y_parsed = 1
                                        case _:
                                            _command_def = command_def.split(" ")
                                            if len(_command_def) == 1:
                                                raise ValueError()
                                            interval = int(_command_def[1])
                                            match (_command_def[0].lower()):
                                                case 'left':
                                                    x_parsed = interval * -1
                                                case 'right':
                                                    x_parsed = interval
                                                case 'up':
                                                    y_parsed = interval * -1
                                                case 'down':
                                                    y_parsed = interval
                                except:
                                    self.error(f"Invalid command definition: {command_type}: {command_def}")
                                    raise


                            elif isinstance(command_def, dict):

                                track_def = command_def.get('track')
                                scene_def = command_def.get('scene')


                                if track_def is not None:
                                    track_def_parsed = self._compile_and_check(track_def, vars_dict, context)
                                else:
                                    x_def = command_def.get('x', 0)
                                    x_parsed = self._compile_and_check(x_def, vars_dict, context)

                                if scene_def is not None:
                                    scene_def_parsed = self._compile_and_check(scene_def, vars_dict, context)
                                else:
                                    y_def = command_def.get('y', 0)
                                    y_parsed = self._compile_and_check(y_def, vars_dict, context)

                                self.debug(track_def_parsed, scene_def_parsed, x_parsed, y_parsed)

                            if x_parsed is not None:
                                ring_component.move(x=x_parsed)
                            elif track_def_parsed is not None:
                                ring_component.go_to_track(track_def_parsed)

                            if y_parsed is not None:
                                ring_component.move(y=y_parsed)
                            elif scene_def_parsed is not None:
                                ring_component.go_to_scene(scene_def_parsed)

                        case 'keyboard':
                            self.log("got keybaord cmd")
                            self.log(command_def)
                            melodic_inst = self.component_map["MelodicComponent"]

                            for key_type, key_def in command_def.items():
                                match key_type.lower():
                                    case 'in_key':
                                        if isinstance(key_def, bool):
                                            melodic_inst.chromatic = not key_def  # internal name is `chromatic`, user is `in_key`
                                        elif key_def == "toggle":
                                            melodic_inst.chromatic = not melodic_inst.chromatic
                                        else:
                                            raise ValueError(f'Invalid keyboard command: `in_key` must be a boolean or `toggle`.\n{command_def}')

                                    case 'layout':
                                        melodic_inst.layout = key_def
                                    case 'full_velo':
                                        if isinstance(key_def, bool):
                                            melodic_inst.full_velo = key_def
                                        elif key_def == "toggle":
                                            melodic_inst.full_velo = not melodic_inst.full_velo
                                        else:
                                            raise ValueError(f'Invalid keyboard command: `full_velo` must be a boolean or `toggle`.\n{command_def}')
                                        melodic_inst.full_velo = key_def
                                    case 'repeat_rate':
                                        rate_def = key_def
                                        if isinstance(key_def, bool):
                                            rate_def = "on" if key_def else "off"
                                        else:
                                            if not isinstance(key_def, str):
                                                raise RuntimeError(f'invalid key definition: {key_def}')
                                            if "${" in key_def:
                                                parsed, status = self.compile(key_def, vars_dict, context)
                                                if status != 0:
                                                    raise RuntimeError(f"Couldn't parse key: {key_def}")
                                                rate_def = parsed
                                        melodic_inst.repeat_rate = rate_def
                                    case 'octave':
                                        if isinstance(key_def, int):
                                            melodic_inst.octave = key_def
                                        if isinstance(key_def, str):
                                            if "${" in key_def:
                                                parsed, status = self.compile(key_def, vars_dict, context)
                                                if status != 0:
                                                    raise RuntimeError(f"Couldn't parse command: {command_type}: {command_def}")
                                                key_def = parsed
                                            else:
                                                try:
                                                    key_def = int(key_def)
                                                except ValueError:
                                                    raise RuntimeError(f"Couldn't parse command: {command_type}: {command_def}")
                                            melodic_inst.octave = key_def
                                        elif isinstance(key_def, dict):
                                            direction = None
                                            dir_def = key_def.get('down')
                                            if dir_def is not None:
                                                direction = "down"
                                            else:
                                                dir_def = key_def.get('up')
                                                if dir_def is not None:
                                                    direction = "up"
                                                else:
                                                    raise RuntimeError(f"Couldn't parse command: {command_type}: {command_def}")
                                            if isinstance(dir_def, str):
                                                if "${" in dir_def:
                                                    parsed, status = self.compile(dir_def, vars_dict, context)
                                                    if status != 0:
                                                        raise RuntimeError(f"Couldn't parse command: {command_type}: {command_def}")
                                                    dir_def = parsed
                                            try:
                                                dir_def = int(dir_def)
                                            except ValueError:
                                                raise RuntimeError(f"Couldn't parse command: {command_type}: {command_def}")

                                            if direction == "down":
                                                dir_def *= -1

                                            melodic_inst.increment_octave(dir_def)

                        case 'color':
                            if isinstance(command_def, str):
                                command_def = self._compile_and_check(command_def, vars_dict, context)
                            if command_def == 'initial':
                                calling_control.reset_color_to_initial()
                            elif True:
                                calling_control.set_color(command_def)

                        case 'python':
                            if (parsed := self._compile_and_check(command_def, vars_dict, context)) is not None:
                                try:
                                    resolved_vars, status = self._resolve_vars(vars_dict or {}, context, 'live')
                                    if status != 0:
                                        return False

                                    exec_context = self.__build_symtable(context, resolved_vars)

                                    self.__interpreter.symtable = exec_context

                                    result = self.__interpreter.eval(parsed, raise_errors=True)

                                    self.warning(f'Executed Python:\n{parsed}')

                                    return result

                                except Exception as e:
                                    error_msg = f"Failed to execute code: {parsed}\nError: {e}"
                                    self.error(error_msg)
                                    if ABORT_ON_FAILURE:
                                        raise RuntimeError(error_msg)
                        case 'hot_reload':
                            if not command_def:
                                self.debug("`hot_reload` called with falsy value")
                                return

                            self.canonical_parent.hot_reload()
                        case 'do_toggle':
                            if not command_def:
                                return
                            try:
                                calling_control.toggle_mapped_parameter()
                            except AttributeError:
                                raise ConfigurationError("`toggle_param` is only available on `param` type controls.")
                        case _:
                            error_msg = f'Unknown command type: {command_type}'
                            self.log(error_msg)
                            if ABORT_ON_FAILURE:
                                raise RuntimeError(error_msg)

            return True

        except Exception as e:
            self.log(e)
            raise

    @listens('tracks')
    def ring_tracks_changed(self):
        new_tracks = self.__session_ring.tracks
        self.debug(f'{self.name} ring tracks changed: {self.__session_ring.tracks}')
        for track in new_tracks:
            self.debug(track.name)


class SelectedTrackNameGetter(DynamicString):
    def __new__(cls, view):
        obj = str.__new__(cls, "")
        obj._value_func = lambda: view.selected_track.name
        return obj
