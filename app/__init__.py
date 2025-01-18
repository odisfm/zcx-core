from .zcx_core import ZCXCore, Specification

# logger = None


def create_instance(c_instance):
    # global logger
    # logger = logging.getLogger(__name__)
    return ZCXCore(Specification, c_instance=c_instance)
