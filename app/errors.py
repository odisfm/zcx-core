class ConfigurationError(Exception):

    def __init__(self, message):
        super().__init__(message)


class CriticalConfigurationError(ConfigurationError):
    """Distinction for errors so severe that they should always crash the script."""

    pass


class HardwareSpecificationError(ConfigurationError):

    def __init__(self, *a):
        super().__init__(*a)
