from copy import deepcopy

from ableton.v3.control_surface import ControlSurface
from .defaults import BUILT_IN_COLORS


class TemplateManager:

    def __init__(self, root_cs):
        self.root_cs: ControlSurface = root_cs
        self.__global_control_template = {}
        self.__control_templates = {}
        self.__name = self.__class__.__name__
        self.__logger = self.root_cs._logger.getChild(self.__name)
        from .yaml_loader import yaml_loader
        self.__yaml_loader = yaml_loader
        from . import CONFIG_DIR
        self.__config_dir = CONFIG_DIR
        self.__color_templates = {}
        self.load_control_templates()
        self.__logger.debug(f'{self.__name} initialised')

    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)

    @property
    def global_control_template(self):
        return deepcopy(self.__global_control_template)

    @property
    def control_templates(self):
        return deepcopy(self.__control_templates)

    def get_control_template(self, name):
        template = self.__control_templates.get(name)
        if template is None:
            return None
        return deepcopy(template)

    def get_color_template(self, name):
        template = self.__color_templates.get(name)
        if template is None:
            return None
        return deepcopy(template)

    def load_control_templates(self):
        try:
            raw_config = self.__yaml_loader.load_yaml(
                f"{self.__config_dir}/control_templates.yaml"
            )
        except FileNotFoundError:
            raw_config = {}
        if "__global__" in raw_config:
            self.__global_control_template = raw_config.pop("__global__")
        self.__control_templates = raw_config

    def load_color_templates(self):
        try:
            raw_config = self.__yaml_loader.load_yaml(
                f"{self.__config_dir}/colors.yaml"
            )
        except FileNotFoundError:
            raw_config = {}

        color_templates = {}

        for color in BUILT_IN_COLORS:
            if color in raw_config:
                color_templates[color] = deepcopy(raw_config[color])
            else:
                color_templates[color] = getattr(BUILT_IN_COLORS, color)

        for color in raw_config:
            if color.startswith("__"):
                continue
            color_templates[color] = deepcopy(raw_config[color])
