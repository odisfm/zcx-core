class ConfigurationError(Exception):

    def __init__(self, message):
        super().__init__(message)


class CriticalConfigurationError(ConfigurationError):
    """Distinction for errors so severe that they should always crash the script."""

    pass


class HardwareSpecificationError(ConfigurationError):

    def __init__(self, *a):
        super().__init__(*a)


class ZcxStartupError(Exception):

    def __init__(self, *msg, traceback=True, boilerplate=True):
        super().__init__("Zcx encountered a fatal error on startup")
        self.msg = msg
        self.traceback = traceback
        self.boilerplate = boilerplate
