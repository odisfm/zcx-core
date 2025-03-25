import os
from .vendor.yaml import safe_load


class YamlLoader:

    def __init__(self):
        from . import ROOT_LOGGER
        self.__logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.log('initialised')
        self.__base_dir = os.path.abspath(os.path.dirname(__file__))

    def log(self, *msg):
        for message in msg:
            self.__logger.info(message)

    def load_yaml(self, path):
        if not path.endswith('.yaml'):
            raise ValueError('path must end with .yaml')

        full_path = os.path.abspath(os.path.join(self.__base_dir, path))

        # Check that the resulting path is within the allowed base directory.
        if os.path.commonpath([full_path, self.__base_dir]) != self.__base_dir:
            raise ValueError('Attempted directory traversal outside of base directory')

        if not os.path.isfile(full_path):
            raise FileNotFoundError(f'{full_path} does not exist or is not a file')

        with open(full_path, 'r') as f:
            obj = safe_load(f)

        return obj


yaml_loader = YamlLoader()
