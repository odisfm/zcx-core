from ableton.v2.base.event import listens

from ..colors import parse_color_definition
from ..errors import ConfigurationError
from ..z_control import ZControl


class PageControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self.__page_manager = None
        self.__action_resolver = None
        self._page_number = None
        self._active_color = None
        self._inactive_color = None
        self._disabled_color = None
        self._suppress_attention_animations = True

    def handle_gesture(self, gesture):
        try:
            super().handle_gesture(gesture)
        except ValueError as e:
            self.animate_failure()
            raise e

    def setup(self):
        super().setup()
        from . import page_manager, action_resolver
        self.__page_manager = page_manager
        self.__action_resolver = action_resolver
        page_config = self._raw_config.get('page')
        if page_config is None:
            self._disabled_color = self._control_element.color_swatch.OFF
            self._color = self._disabled_color
            self.__color_dict['base'] = self._disabled_color
            self._control_element.set_light(self._color)
            from .. import SAFE_MODE
            error_message = f'page control defined with no `page` key\n{self._raw_config}'
            if SAFE_MODE is True:
                raise ConfigurationError(error_message)
            else:
                self.log(error_message)
        parsed_page, status = self.__action_resolver.compile(str(page_config), self._vars, self._context)
        self._color_dict['failure'] = self._control_element.color_swatch.ERROR
        self.__set_page(parsed_page)
        self.page_changed()

    def __set_page(self, page_number):
        try:
            try:
                _page_number = int(page_number)
                if not self.__page_manager.is_valid_page_number(_page_number):
                    raise ValueError
            except ValueError:
                _page_number = self.__page_manager.get_page_number_from_name(page_number)
                if _page_number is False:
                    self._disabled_color = self._control_element.color_swatch.OFF
                    self._color = self._disabled_color
                    self._color_dict['base'] = self._disabled_color
                    self.page_changed.subject = self.__page_manager
                    self._page_number = None
                    raise ConfigurationError(f'Invalid page assignment: {page_number}')
            self._page_number = _page_number
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
            self._color = self._active_color
            self.page_changed.subject = self.__page_manager
        except ConfigurationError as e:
            from .. import SAFE_MODE
            if SAFE_MODE is True:
                raise e
            else:
                self.log(e)

    def animate_success(self, duration=0):
        return

    @listens('current_page')
    def page_changed(self):
        try:
            new_page_no = self.__page_manager.current_page
            if self._page_number is None:
                self.request_color_update()
            elif new_page_no == self._page_number:
                self._color = self._active_color
            else:
                self._color = self._inactive_color
            self.request_color_update()

        except Exception as e:
            self.log(e)
