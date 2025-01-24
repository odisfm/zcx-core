from ableton.v2.base.event import listens
from ..z_control import only_in_view
from ..colors import RgbColor, Color, ColorSwatches

from ..z_control import ZControl
from ..errors import ConfigurationError


class PageControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self.__page_manager = None
        self.__action_resolver = None
        self._page_number = None
        self._suppress_animations = True

    def handle_gesture(self, gesture):
        super().handle_gesture(gesture)

    def setup(self):
        super().setup()
        from . import page_manager, action_resolver
        self.__page_manager = page_manager
        self.__action_resolver = action_resolver
        page_config = self._raw_config.get('page')
        if page_config is None:
            self._color = self._control_element._color_swatch.OFF
            self._control_element.set_light(self._color)
            from .. import SAFE_MODE
            error_message = f'page control defined with no `page` key\n{self._raw_config}'
            if SAFE_MODE is True:
                raise ConfigurationError(error_message)
            else:
                self.log(error_message)
        parsed_page, status = self.__action_resolver.compile(str(page_config), self._vars, self._context)
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
                    self._color = ColorSwatches.basic.OFF
                    self.page_changed.subject = self.__page_manager
                    self._page_number = None
                    raise ConfigurationError(f'Invalid page assignment: {page_number}')
            self._page_number = _page_number
            self.page_changed.subject = self.__page_manager
        except ConfigurationError as e:
            from .. import SAFE_MODE
            if SAFE_MODE is True:
                raise e
            else:
                self.log(e)

    @listens('current_page')
    def page_changed(self):
        try:
            new_page_no = self.__page_manager.current_page
            if self._page_number is None:
                self.request_color_update()
            elif new_page_no == self._page_number:
                self._color = self._color_swatch.YELLOW
            else:
                self._color = self._color_swatch.RED
            self.request_color_update()

        except Exception as e:
            self.log(e)
