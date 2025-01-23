from ableton.v2.base.event import listens
from ..colors import RgbColor

from ..z_control import ZControl
from ..errors import ConfigurationError


class PageControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
        self.__page_manager = None
        self.__action_resolver = None
        self._page_number = None

    def handle_gesture(self, gesture):
        super().handle_gesture(gesture)

    def setup(self):
        super().setup()
        from . import page_manager, action_resolver
        self.__page_manager = page_manager
        self.__action_resolver = action_resolver
        page_config = self._raw_config.get('page')
        if page_config is None:
            raise ConfigurationError('page control defined with no `page` key')
        parsed_page, status = self.__action_resolver.compile(str(page_config), self._vars, self._context)
        self.__set_page(parsed_page)
        self.page_changed()

    def __set_page(self, page_number):
        try:
            _page_number = int(page_number)
        except ValueError:
            _page_number = self.__page_manager.get_page_number_from_name(page_number)
            if _page_number is False:
                raise ConfigurationError(f'Invalid page assignment: {page_number}')
        self._page_number = _page_number
        self.page_changed.subject = self.__page_manager

    @listens('current_page')
    def page_changed(self):
        try:
            page = self.__page_manager.current_page

            if page == self._page_number:
                self._color = RgbColor(22)
                self.request_color_update()
            else:
                self._color = RgbColor(1)
                self.request_color_update()

        except Exception as e:
            self.log(e)
