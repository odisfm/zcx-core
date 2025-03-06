from .zcx_component import ZCXComponent


class ZCXPlugin(ZCXComponent):

    def __init__(
            self,
            name,
            *a,
            **k
    ):
        super().__init__(name, *a, **k)
        try:
            self.__zcx_api = None
            from . import PREF_MANAGER
            self._user_config = PREF_MANAGER.get_plugin_config(self.__class__.__module__)
            if self._user_config is not None:
                self.log(self._user_config)
        except:
            self._user_config = None

    def setup(self):
        self.debug(f'Loading plugin {self.name}')
        self.__zcx_api = self.canonical_parent.zcx_api

    @property
    def api(self):
        return self.__zcx_api

    def add_api_method(self, method_name, callable):
        api_class = self.__zcx_api.__class__
        if hasattr(api_class, method_name):
            raise RuntimeError(f'Method {method_name} already exists on API object')

        setattr(api_class, method_name, callable)

    def refresh_feedback(self):
        """
        zcx_core calls this method when it determines that physical feedback needs to be updated.
        This may be because the hardware was reconnected, or it is returning to User mode from Live mode.
        You do not need to implement this method unless your plugin manually sets controller feedback.
        :return:
        """
        pass

    def receive_sysex(self, midi_bytes: tuple[int]):
        """
        When zcx_core receives a sysex message it will forward the message to all plugins.
        :param midi_bytes:
        :return:
        """
        pass
