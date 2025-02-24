from .zcx_component import ZCXComponent


class ZCXPlugin(ZCXComponent):

    def __init(
            self,
            name,
            *a,
            **k
    ):
        super().__init__(name, *a, **k)
        self.__zcx_api = None

    def setup(self):
        self.debug(f'Loading plugin {self.name}')
        self.__zcx_api = self.canonical_parent.component_map['ApiManager'].get_zcx_api()

    @property
    def api(self):
        return self.__zcx_api

    def add_api_method(self, method_name, callable):
        api_class = self.__zcx_api.__class__
        if hasattr(api_class, method_name):
            raise RuntimeError(f'Method {method_name} already exists on API object')

        setattr(api_class, method_name, callable)
