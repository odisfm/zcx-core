from ableton.v2.base.event import listens

from ..colors import parse_color_definition
from ..errors import ConfigurationError, CriticalConfigurationError
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

    def handle_gesture(self, gesture, dry_run=False, testing=False):
        try:
            super().handle_gesture(gesture, dry_run, testing)
        except ValueError as e:
            self.animate_failure()
            raise

    def setup(self):
        super().setup()
        from . import page_manager, action_resolver
        from .. import STRICT_MODE

        self.__page_manager = page_manager
        self.__action_resolver = action_resolver
        page_config = self._raw_config.get('page')
        if page_config is None:
            self._disabled_color = self._control_element.color_swatch.OFF
            self._color = self._disabled_color
            self._color_dict['base'] = self._disabled_color
            self._control_element.set_light(self._color)
            error_message = f'page control defined with no `page` key\n{self._raw_config}'
            if STRICT_MODE:
                raise ConfigurationError(error_message)
            else:
                self.log(error_message)
                return
        parsed_page, status = self.__action_resolver.compile(str(page_config), self._vars, self._context)
        self._color_dict['failure'] = self._control_element.color_swatch.ERROR
        self.__set_page(parsed_page)
        if self._page_number is None:
            error_message = f'invalid page number: {parsed_page}'
            if STRICT_MODE:
                raise ConfigurationError(error_message)
            else:
                self.log(error_message)
                return
        self._simple_feedback = False
        self._context['page_active'] = False
        self.page_changed()
        self._context['me']['page'] = self._page_number
        self._context['me']['Page'] =  self._page_number + 1
        page_name = self.__page_manager.get_page_name_from_index(self._page_number)
        self._context['me']['page_name'] = page_name


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
                    msg = f'Invalid page assignment: {page_number}'
                    try:
                        int(page_number)
                    except ValueError:
                        from .. import STRICT_MODE
                        if STRICT_MODE:
                            raise CriticalConfigurationError(msg)
                    finally:
                        self.warning(msg)

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
            from .. import STRICT_MODE
            if STRICT_MODE is True:
                raise
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
                self._context['me']['page_active'] = True
            else:
                self._color = self._inactive_color
                self._context['me']['page_active'] = False
            self.request_color_update()

        except Exception as e:
            self.log(e)
