from ableton.v2.base import EventObject, listenable_property


class PadSection(EventObject):

    root_cs = None
    page_manager = None

    def __init__(
            self,
            section_name,
            owned_coordinates,
            pages_in,
            width
    ):
        super().__init__()
        self._logger = self.page_manager._logger.getChild(f'matrix_section__{section_name}')
        self.log(f'I appear in pages {pages_in}')

    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)
