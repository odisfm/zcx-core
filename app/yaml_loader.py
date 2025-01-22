import os

from .vendor.yaml import safe_load


class YamlLoader:

    def __init__(self):
        from . import ROOT_LOGGER
        self.__logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.log('initialised')
        self.this_dir = os.path.dirname(__file__)

    def log(self, *msg):
        for msg in msg:
            self.__logger.info(msg)

    def load_yaml(self, path):
        if not path.endswith('.yaml'):
            raise ValueError('path must end with .yaml')

        full_path = os.path.join(self.this_dir, path)

        with open(full_path, 'r') as f:
            obj = safe_load(f)

        return obj


yaml_loader = YamlLoader()
