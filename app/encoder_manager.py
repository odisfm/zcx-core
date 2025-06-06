import copy

from ableton.v3.base import EventObject, listens, listenable_property
from .errors import ConfigurationError, CriticalConfigurationError
from .osc_watcher import OscEncoderWatcher
from .z_encoder import ZEncoder
from .zcx_component import ZCXComponent


class EncoderManager(ZCXComponent):


    def __init__(
        self,
        name="EncoderManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)

        self._encoders = {}
        self.__encoder_groups = {}
        self._selected_device_watcher = None

    def setup(self):
        self.debug(f'{self.name} doing setup')
        self._selected_device_watcher = SelectedDeviceWatcher(self, self.song)
        ZEncoder.selected_device_watcher = self._selected_device_watcher
        self.create_encoders()
        self.create_osc_watchers()

    def bind_all_encoders(self):
        for enc_name, enc_obj in self._encoders.items():
            try:
                enc_obj.bind_to_active()
            except Exception as e:
                self.error(f'Failed to bind {enc_name}', e)

    def create_encoders(self):
        try:
            encoder_config = self.yaml_loader.load_yaml(f'{self._config_dir}/encoders.yaml')
        except FileNotFoundError:
            encoder_config = {}

        flat_config = self.flatten_encoder_config(encoder_config)

        from . import PREF_MANAGER
        user_prefs = PREF_MANAGER.user_prefs
        ZEncoder._log_failed_bindings = user_prefs.get('log_failed_encoder_bindings', True)

        ZEncoder.mode_manager = self.canonical_parent.component_map['ModeManager']
        ZEncoder.action_resolver = self.canonical_parent.component_map['ActionResolver']
        ZEncoder.song = self.song
        ZEncoder.session_ring = self.canonical_parent._session_ring_custom

        for encoder_name, encoder_def in flat_config.items():

            encoder_obj = ZEncoder(
                self.canonical_parent,
                encoder_def,
                encoder_name,
            )

            if encoder_name in self._encoders:
                raise CriticalConfigurationError(f'Multiple definitions for encoder {encoder_name}'
                                         f'\n{encoder_def}')

            self._encoders[encoder_name] = encoder_obj
            
            if 'group_name' in encoder_def['context']:
                    self.add_encoder_to_group(encoder_name, encoder_def['context']['group_name'])

        hw_interface = self.canonical_parent.component_map['HardwareInterface']

        for encoder_name, encoder_obj in self._encoders.items():
            state = getattr(hw_interface, encoder_name)
            element = state._control_element
            encoder_obj._control_element = element
            encoder_obj._state = state

            encoder_obj.setup()

    def flatten_encoder_config(self, raw_config) -> dict:
        self.debug(f'Flattening encoder config')

        def merge_configs(base, override):
            """Deep merge two configurations, ensuring override values take precedence"""
            merged = copy.deepcopy(base)
            for key, value in override.items():
                if (
                        key in merged
                        and isinstance(merged[key], dict)
                        and isinstance(value, dict)
                ):
                    merged[key] = merge_configs(merged[key], value)
                else:
                    merged[key] = copy.deepcopy(value)
            return merged

        flat_defs = {}
        grouped_defs = {}

        try:
            for encoder_name, encoder_def in raw_config.items():
                if encoder_name.startswith('__'):
                    grouped_defs[encoder_name] = encoder_def
                else:
                    flat_defs[encoder_name] = encoder_def
        except ConfigurationError as e:
            # todo: allow continue based on preference
            raise

        for group_name, group_def in grouped_defs.items():
            group_context = {
                'group_name': group_name,
            }

            group_def = copy.deepcopy(group_def)
            included_encoders = group_def.get('includes')
            override_dict = group_def.get('encoders', {})

            if included_encoders is None:
                raise ConfigurationError(
                    f'Encoder group {group_name} has no `includes` key'
                    f'\n{group_def}'
                )

            del group_def['includes']

            for i, encoder_name in enumerate(included_encoders):
                item_def_copy = copy.deepcopy(group_def)

                if encoder_name in override_dict:
                    override_def = override_dict[encoder_name]
                else:
                    override_def = {}

                merged_def = merge_configs(item_def_copy, override_def)

                group_context_copy = copy.deepcopy(group_context)
                group_context_copy['group_name'] = group_name.lstrip('__')

                this_context = {
                    'me': {
                        'index': i,
                        'Index': i + 1,
                        'group_index': i,
                        'group_Index': i + 1,
                        'name': encoder_name,
                    }
                }

                this_context = group_context_copy | this_context
                merged_def['context'] = this_context

                full_item_config = merged_def

                flat_defs[encoder_name] = full_item_config

        for i, (encoder_name, encoder_def) in enumerate(flat_defs.items()):
            if 'context' in encoder_def:
                continue
            else:
                context = {
                    'me': {
                        'index': i,
                        'Index': i + 1,
                        'group_index': i,
                        'group_Index': i + 1,
                        'name': encoder_name,
                    }
                }

                encoder_def['context'] = context

        return flat_defs

    def create_osc_watchers(self):
        if OscEncoderWatcher._osc_server is None:
            self.error('No OSC server configured')
            return

        from . import PREF_MANAGER
        user_prefs = PREF_MANAGER.user_prefs

        osc_prefs = user_prefs.get('osc_output', False)

        if not osc_prefs:
            return

        if isinstance(osc_prefs, dict):
            encoder_prefs = osc_prefs.get('encoders', False)
            if not encoder_prefs:
                self.debug(f'encoder osc output disabled by user preference/')
                return
            OscEncoderWatcher.send_name = encoder_prefs.get('name', False)
            OscEncoderWatcher.send_string = encoder_prefs.get('value', False)
            OscEncoderWatcher.send_int = encoder_prefs.get('int', False)
            OscEncoderWatcher.send_float = encoder_prefs.get('float', False)

        for encoder in self._encoders.values():
            watcher = OscEncoderWatcher(encoder)
    
    def add_encoder_to_group(self, encoder, group_name):
        if group_name in self.__encoder_groups:
            self.__encoder_groups[group_name].append(encoder)
        else:
            self.__encoder_groups[group_name] = [encoder]
    
    def get_encoder_group(self, group_name):
        if group_name in self.__encoder_groups:
            return self.__encoder_groups[group_name]
        else:
            self.error(f'No encoder group for {group_name}. Registered groups are:\n'
                     f'{self.__encoder_groups.keys()}')
            return None

    def get_encoder(self, encoder_name):
        if encoder_name in self._encoders:
            return self._encoders[encoder_name]
        else:
            self.log(f'No encoder called {encoder_name}. Registered encoders are:\n'
                     f'{self._encoders.keys()}')
            return None


class SelectedDeviceWatcher(EventObject):

    def __init__(self, encoder_manager, song, *a, **kw):
        super().__init__(*a, **kw)
        self._encoder_manager = encoder_manager
        self._song = song
        self._selected_track = None
        self.__selected_device = None
        self.__selected_rack = None
        self.__selected_chain = None
        self.selected_track_listener.subject = self._song.view
        self.selected_track_listener()

    def log(self, *msg):
        self._encoder_manager.debug(*msg)

    @listenable_property
    def selected_device(self):
        return self.__selected_device

    @selected_device.setter
    def selected_device(self, device):
        self.__selected_device = device
        self.notify_selected_device(device)

    @listenable_property
    def selected_rack(self):
        return self.__selected_rack

    @selected_rack.setter
    def selected_rack(self, rack):
        self.__selected_rack = rack
        self.notify_selected_rack(rack)

    @listenable_property
    def selected_chain(self):
        return self.__selected_chain

    @selected_chain.setter
    def selected_chain(self, chain):
        self.__selected_chain = chain
        self.notify_selected_chain(chain)

    @listens('selected_track')
    def selected_track_listener(self):
        if hasattr(self, '_selected_track') and self._selected_track is not None:
            self.selected_device_listener.subject = None

        self._selected_track = self._song.view.selected_track
        if self._selected_track is not None:
            self.selected_device_listener.subject = self._selected_track.view
            self.selected_device_listener()
            self.log(f'selected track: {self._selected_track.name}')
        else:
            self.selected_device = None
            self.log('No track selected')

    @listens('selected_device')
    def selected_device_listener(self):
        self.log(f'selected device changed')
        new_device = None if self._selected_track is None else self._selected_track.view.selected_device
        self.selected_device = new_device

        try:
            if new_device is not None:
                self.log(f'selected device: {new_device.name}')
        except AttributeError:
            pass

        self.selected_chain_listener.subject = None

        if new_device is None or not new_device.can_have_chains:
            self.selected_rack = None
            self.selected_chain = None
            return

        self.selected_rack = new_device

        if hasattr(new_device, 'view') and new_device.view is not None:
            self.selected_chain_listener.subject = new_device.view
            self.selected_chain = new_device.view.selected_chain
        else:
            self.selected_chain = None

    @listens('selected_chain')
    def selected_chain_listener(self):
        if self.selected_rack is not None and hasattr(self.selected_rack, 'view'):
            self.selected_chain = self.selected_rack.view.selected_chain
