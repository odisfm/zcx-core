from ..z_control import ZControl


class BasicZControl(ZControl):

    def __init__(self, *a, **kwargs):
        ZControl.__init__(self, *a, **kwargs)
