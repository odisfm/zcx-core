import re
from typing import Dict, Any, Tuple, Optional, Callable, Union
from itertools import chain

from ableton.v3.control_surface import ControlSurface, Component

from .z_control import ZControl
from .cxp_bridge import CxpBridge
from .page_manager import PageManager
from .mode_manager import ModeManager
from .cxp_bridge import CxpBridge
from .hardware_interface import HardwareInterface

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


class ActionResolver(Component):

    def __init__(
            self,
            name="ActionResolver",
            *a,
            **k,
    ):
        super(ActionResolver, self).__init__(name, *a, **k)
        from . import ROOT_LOGGER
        self.__logger = ROOT_LOGGER.getChild(name)
        self.pattern = re.compile(r"\\\$\\{|\\\${|\$\\{|\${([^{}\\]*)(?<!\\)}")
        self.__page_manager: PageManager = self.canonical_parent.component_map['PageManager']
        self.__mode_manager: ModeManager = self.canonical_parent.component_map['ModeManager']
        self.__cxp: CxpBridge = self.canonical_parent.component_map['CxpBridge']
        self.__hardware_interface: HardwareInterface = self.canonical_parent.component_map['HardwareInterface']

    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)

    def _evaluate_expression(
        self, expr: str, context: Dict[str, Any], locals: Dict[str, Any]
    ) -> Tuple[Any, int]:
        """Evaluate a Python expression with given context and locals."""
        try:
            if expr.startswith("$"):
                expr = expr[1:]

            dot_context = {
                k: DotDict(v) if isinstance(v, dict) else v for k, v in context.items()
            }

            all_locals = {**dot_context, **locals}
            result = eval(expr, {}, all_locals)
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
        mode: str='build',
    ) -> Tuple[str, int]:
        """Compile an action string, resolving variables and template patterns."""
        if "@{" not in action_string and "${" not in action_string:
            return action_string, 0

        resolved_vars, status = self._resolve_vars(vars, context, mode)
        if status != 0:
            return action_string, status

        result = ""
        last_end = 0

        for match in self.pattern.finditer(action_string):
            result += action_string[last_end : match.start()]

            replacement, match_status = self._replace_match(
                match, resolved_vars, context, mode
            )
            if match_status != 0:
                return action_string, match_status

            result += replacement
            last_end = match.end()

        result += action_string[last_end:]

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
            error_msg = f"Couldn't parse command: {command_str}"
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
                            if parsed := self._compile_and_check(command_def, vars_dict, context):
                                self.__cxp.trigger_action_list(parsed)
                        case 'log':
                            if parsed := self._compile_and_check(command_def, vars_dict, context):
                                self.log(parsed)
                        case 'msg':
                            if parsed := self._compile_and_check(command_def, vars_dict, context):
                                self.canonical_parent.show_message(parsed)
                        case 'page':
                            if parsed := self._compile_and_check(command_def, vars_dict, context):
                                result = self.__page_manager.request_page_change(parsed)
                                if not result:
                                    if ABORT_ON_FAILURE:
                                        raise RuntimeError(f'invalid page change: {parsed}')
                                    return False
                        case 'mode':
                            if parsed := self._compile_and_check(command_def, vars_dict, context):
                                self.__mode_manager.toggle_mode(parsed)
                        case 'mode_on':
                            if parsed := self._compile_and_check(command_def, vars_dict, context):
                                self.__mode_manager.add_mode(parsed)
                        case 'mode_off':
                            if parsed := self._compile_and_check(command_def, vars_dict, context):
                                self.__mode_manager.remove_mode(parsed)
                        case 'refresh':
                            self.__hardware_interface.refresh_all_lights()
                        case _:
                            error_msg = f'Unknown command type: {command_type}'
                            self.log(error_msg)
                            if ABORT_ON_FAILURE:
                                raise RuntimeError(error_msg)

            return True

        except Exception as e:
            self.log(e)
            raise e
