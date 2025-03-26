import copy

from .errors import ConfigurationError, CriticalConfigurationError
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

    def setup(self):
        self.debug(f'{self.name} doing setup')
        self.create_encoders()

    def bind_all_encoders(self):
        for enc_name, enc_obj in self._encoders.items():
            try:
                enc_obj.bind_to_active()
            except:
                self.error(f'Failed to bind {enc_name}')

    def create_encoders(self):
        encoder_config = self.yaml_loader.load_yaml(f'{self._config_dir}/encoders.yaml')
        if encoder_config is None:
            # todo: raise configuration warning
            return

        flat_config = self.flatten_encoder_config(encoder_config)

        ZEncoder.mode_manager = self.canonical_parent.component_map['ModeManager']
        ZEncoder.action_resolver = self.canonical_parent.component_map['ActionResolver']
        ZEncoder.song = self.song

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
            raise e

        for group_name, group_def in grouped_defs.items():
            group_context = {
                'group_name': group_name,
            }

            group_def = copy.deepcopy(group_def)
            included_encoders = group_def.get('includes')
            override_list = group_def.get('encoders', [])
            overrides = {}

            if included_encoders is None:
                raise ConfigurationError(
                    f'Encoder group {group_name} has no `includes` key'
                    f'\n{group_def}'
                )

            for i, override in enumerate(override_list):
                if override is None:
                    continue
                name = included_encoders[i]
                overrides[name] = override

            del group_def['includes']

            for i, encoder_name in enumerate(included_encoders):
                item_def_copy = copy.deepcopy(group_def)

                if encoder_name in overrides:
                    override_def = overrides[encoder_name]
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
