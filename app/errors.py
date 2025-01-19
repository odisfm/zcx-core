class ConfigurationError(Exception):

    def __init__(self, message):
        super().__init__(message)


class HardwareSpecificationError(ConfigurationError):

    def __init__(self, *a):
        super().__init__(*a)
