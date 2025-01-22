from ableton.v3.control_surface import Component, ControlSurface



class TemplateManager:

    def __init__(self, root_cs):
        self.root_cs: ControlSurface = root_cs
        self.global_control_template = {}
        self.control_templates = {}
        self.__name = self.__class__.__name__
        self.__logger = self.root_cs.logger.getChild(self.__name)
        from .yaml_loader import yaml_loader
        from . import CONFIG_DIR

        self.log(f'{self.__name} initialised')

    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)
