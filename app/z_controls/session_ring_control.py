from ableton.v3.base import listens, listenable_property
from ..z_control import ZControl
from ..errors import ConfigurationError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session_ring import SessionRing


class SessionRingControl(ZControl):

    session_ring = None

    def __init__(self, *a, **kw):
        ZControl.__init__(self, *a, **kw)
        self._ring_index = None
        from . import session_ring, action_resolver
        self.__session_ring = session_ring
        self.__action_resolver = action_resolver

    def setup(self):
        super().setup()
        try:
            ring_idx_def = self._raw_config['ring_index']
            parsed, status = self.__action_resolver.compile(ring_idx_def, self._vars, self._context)
            if status != 0:
                raise ConfigurationError(f'Unparseable `ring_index`: {ring_idx_def}')
            self._ring_index = int(parsed)
        except KeyError:
            raise ConfigurationError('SessionRingControl defined with no `ring_index` key')
        except ValueError:
            raise ConfigurationError(f'SessionRingControl `ring_index` must be an integer. `{ring_idx_def}` was given')

    @property
    def ring_index(self):
        return self._ring_index

    @listens('offsets')
    def ring_moved(self):
        pass


