from ableton.v2.base.event import listens

from ..colors import parse_color_definition
from ..errors import ConfigurationError
from ..z_control import ZControl


class OverlayControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self.__view_manager = self.root_cs.component_map["ViewManager"]
        self.__overlay_name = None
        self.__unvalidated_overlay_name = None

    def handle_gesture(self, gesture, dry_run=False, testing=False):
        try:
            super().handle_gesture(gesture, dry_run, testing)
        except ValueError as e:
            self.animate_failure()
            raise

    def setup(self):
        super().setup()

        overlay_config = self._raw_config.get('overlay')
        if overlay_config is None:
            self._disabled_color = self._control_element.color_swatch.OFF
            self._color = self._disabled_color
            self._color_dict['base'] = self._disabled_color
            self._control_element.set_light(self._color)
            error_message = f'overlay control defined with no `overlay` key\n{self._raw_config}'
            raise ConfigurationError(error_message)

        parsed_overlay, status = self.root_cs.component_map["ActionResolver"].compile(str(overlay_config), self._vars, self._context)
        if status != 0:
            raise ConfigurationError(f'Unparseable `overlay` value in {self.parent_section.name}: {overlay_config}')
        self.__unvalidated_overlay_name = parsed_overlay
        # ViewManager is not set up yet
        self._color_dict['failure'] = self._control_element.color_swatch.ERROR
        self._simple_feedback = False
        self._context['me']['overlay'] = self.__overlay_name
        self._on_active_overlay_names_changed.subject = self.__view_manager

        active_color = self._raw_config.get('active_color')
        inactive_color = self._raw_config.get('inactive_color')
        if active_color is not None:
            self._active_color = parse_color_definition(active_color, self)
        else:
            self._active_color = self._control_element.color_swatch.PAGE_ACTIVE
        if inactive_color is not None:
            self._inactive_color = parse_color_definition(inactive_color, self)
        else:
            self._inactive_color = self._control_element.color_swatch.PAGE_INACTIVE

        self._disabled_color = self._control_element.color_swatch.OFF
        self._simple_feedback = False
        self._suppress_animations = True

    def finish_setup(self):
        self.__set_overlay_name()
        self.update_feedback()

    def __set_overlay_name(self):
        name = self.__unvalidated_overlay_name
        if not name in self.__view_manager.all_overlay_names:
            error_message = f'Unknown overlay name: {name}'
            raise ConfigurationError(error_message)
        self.__overlay_name = name

    def animate_success(self, duration=0):
        return

    def _do_simple_feedback_held(self):
        pass

    def _do_simple_feedback_release(self):
        pass

    def update_feedback(self):
        if self.__overlay_name in self.__view_manager.active_overlay_names:
            self.replace_color(self._active_color)
        else:
            self.replace_color(self._inactive_color)

    @listens('active_overlay_names')
    def _on_active_overlay_names_changed(self, _):
        self.update_feedback()
