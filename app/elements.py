import logging
from functools import partial

from ableton.v3.control_surface import ElementsBase


class Elements(ElementsBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.logger = logging.getLogger(__name__)
        self.log = partial(self.logger.critical, *a)

        self.log('hello')
