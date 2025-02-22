BUILT_IN_COLORS = [
    "__rgb__animate_success__",
    "__rgb__animate_failure__",
    "__rgb__attention__",
    "__rgb__blank__",
    "__basic__animate_success__",
    "__basic__animate_failure__",
]


class DefaultColors:

    __rgb__animate_success__ = {"blink": {"a": "base", "b": "white", "speed": 3}}

    __rgb__animate_failure__ = {"blink": {"a": "base", "b": "red", "speed": 4}}

    __rgb__attention__ = {"pulse": {"a": "base", "b": "white"}}

    __rgb__blank__ = {"midi": 1}

    __basic__animate_success__ = {"blink": {"speed": 2}}

    __basic__animate_failure__ = {"blink": {"speed": 5}}
