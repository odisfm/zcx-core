from ableton.v2.base.event import listens

from ..errors import ConfigurationError
from ..z_control import ZControl


class ModeControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self._bound_mode = None
        from . import mode_manager

        self.mode_manager = mode_manager
        from . import action_resolver

        self.action_resolver = action_resolver

    def setup(self):
        super().setup()

        mode = self._raw_config.get("mode")
        if mode is None:
            raise ConfigurationError(
                f"Mode control defined with no `mode` key"
                f"\n{self.parent_section.name}"
                f"\n{self._raw_config}"
            )

        if not isinstance(mode, str):
            raise ConfigurationError(
                f"Key `mode` must be a string"
                f"\n{self.parent_section.name}"
                f"\n{self._raw_config}"
            )

        if "${" in mode:
            mode, status = self.action_resolver.compile(mode, self._vars, self._context)
            if status != 0:
                raise ConfigurationError(
                    f"Couldn't parse mode '{mode}'\n{self.parent_section.name}\n{self._raw_config}"
                )

        all_modes = self.mode_manager.all_modes
        if mode not in all_modes:
            raise ConfigurationError(
                f"Control bound to mode `{mode}`, which is not listed in `_config/modes.yaml`\n"
                f"{self.parent_section.name}"
                f"\n{self._raw_config}"
            )

        self._bound_mode = mode
        self._suppress_animations = True

    @listens("current_modes")
    def modes_changed(self, _):
        current_modes = self.mode_manager.current_modes
        my_mode_active = current_modes.get(self._bound_mode) is True
        if my_mode_active:
            self._parent_logger.debug("my mode active!")
            self._color = self._color_dict.get("attention")
        else:
            self._color = self._color_dict.get("base")
        self.request_color_update()
