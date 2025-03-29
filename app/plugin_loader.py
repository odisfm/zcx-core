import importlib
import inspect
import os
import sys
from copy import copy
from pathlib import Path
from typing import Dict, Type, Any

from .zcx_plugin import ZCXPlugin

ALLOW_MISSING_PLUGIN_DIR = True # todo: user preference


class PluginLoader:

    def __init__(self, logger, *a, **k):
        self.logger = logger
        self.__base_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        zcx_plugin_dir = str(self.__base_dir.resolve())
        if zcx_plugin_dir not in sys.path:
            sys.path.append(zcx_plugin_dir)

        self.__hardware_plugins = {}
        self.__user_plugins = {}
        self.__get_plugins()

    def log(self, *msg):
        for m in msg:
            self.logger.info(m)

    @property
    def hardware_plugins(self):
        return copy(self.__hardware_plugins)

    @property
    def user_plugins(self):
        return copy(self.__user_plugins)

    @property
    def plugin_names(self):
        return list(self.hardware_plugins.keys()) + list(self.user_plugins.keys())

    def __get_plugins(self):
        self.__hardware_plugins = self.collect_plugin_classes('hardware/plugins/')
        self.__user_plugins = self.collect_plugin_classes('plugins/')

    def collect_plugin_classes(self, plugin_dir: str) -> dict[Any, Type[ZCXPlugin]] | None:
        """
        Scans a directory for plugin classes and returns them in a dictionary.
        """
        plugin_classes = {}
        plugin_path = self.__base_dir / plugin_dir

        self.log(f'looking for plugins in {plugin_path}')

        if not plugin_path.exists():
            if not ALLOW_MISSING_PLUGIN_DIR:
                raise RuntimeError(f"Plugin directory does not exist: {plugin_path}")
            else:
                self.log(f"Plugin directory does not exist: {plugin_path}")
                return {}

        for folder in plugin_path.iterdir():
            if not folder.is_dir():
                continue

            plugin_found = False
            sys.path.insert(0, str(folder))

            try:
                for file_path in folder.glob('*.py'):
                    if file_path.name == '__init__.py':
                        continue

                    module_name = file_path.stem
                    self.log(f"Attempting to import module: {module_name} from {folder}")

                    try:
                        module_globals = {'ZCXPlugin': ZCXPlugin}
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        module = importlib.util.module_from_spec(spec)
                        module.__dict__.update(module_globals)
                        spec.loader.exec_module(module)
                        self.log(f"Successfully imported module: {module_name}")

                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and
                                    issubclass(obj, ZCXPlugin) and
                                    obj != ZCXPlugin):
                                plugin_classes[folder.name] = obj
                                plugin_found = True
                                self.log(f"Found plugin class: {obj.__name__} in {module_name}")
                                break

                        if plugin_found:
                            break

                    except Exception as e:
                        self.log(f"Failed to import {module_name} from {folder}: {e}")

                if not plugin_found:
                    raise RuntimeError(f"No valid ZCXPlugin class found in folder: {folder}")

            finally:
                sys.path.remove(str(folder))

        return plugin_classes
