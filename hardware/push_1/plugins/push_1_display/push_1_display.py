from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.zcx_plugin import ZCXPlugin


class Push1Display(ZCXPlugin):

    def __init__(
            self,
            name="Push1Display",
            *a,
            **k
    ):
        super().__init__(name, *a, **k)

    def setup(self):
        super().setup()
