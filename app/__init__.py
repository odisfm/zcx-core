from .zcx_core import ZCXCore, Specification


def create_instance(c_instance):
    return ZCXCore(Specification, c_instance=c_instance)
