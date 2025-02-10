import copy
from functools import wraps, partial
from copy import deepcopy

from ableton.v2.base import EventObject
from ableton.v3.base import listens
from ableton.v3.control_surface import ControlSurface
from ableton.v2.base.task import TimerTask

from .encoder_element import EncoderElement
from .template_manager import TemplateManager
from .errors import ConfigurationError, CriticalConfigurationError
from .cxp_bridge import CxpBridge
from .encoder_state import EncoderState
from .encoder_element import EncoderElement
from .mode_manager import ModeManager
from .encoder_element import EncoderElement
from .action_resolver import ActionResolver


class ZEncoder(EventObject):

    root_cs: ControlSurface = None
    mode_manager: ModeManager = None
    action_resolver: ActionResolver = None
    song = None

    def __init__(
            self,
            root_cs,
            raw_config,
            name
    ):
        super().__init__()
        self._control_element = None
        self.root_cs = root_cs
        self._raw_config = raw_config
        self._name = name
        self._logger = self.root_cs.component_map['EncoderManager']._logger.getChild(self._name)
        self._control_element: EncoderElement = None
        self._state: EncoderState = None
        self._context = {}
        self._vars = {}
        self._default_map = None
        self._mapped_parameter = None
        self._concerned_modes = []
        self._current_mode_string = ''
        self._binding_dict = {}
        self._active_map = {}
        self.modes_changed.subject = self.mode_manager

    def log(self, *msg):
        for msg in msg:
            self._logger.info(msg)

    def setup(self):
        self._context = self._raw_config['context']
        self._vars = self._raw_config.get('vars', {})

        bindings = self._raw_config.get('binding', {})
        if isinstance(bindings, dict):
            pass
        elif isinstance(bindings, str):
            bindings = {"default": bindings}
        else:
            raise CriticalConfigurationError(
                f'Invalid binding config for {self._name}'
                f'\n`bindings` key must be a dict or a string'
                f'\n{self._raw_config}'
            )

        binding_dict = {}
        concerned_modes = []

        for binding_mode, binding_def in bindings.items():
            if isinstance(binding_def, str):
                binding_params = {}
            elif isinstance(binding_def, dict):
                binding_params = copy.deepcopy(binding_def)
                if 'target' in binding_params:
                    binding_def = binding_params['target']
                    del binding_params['target']
                else:
                    pass
            else:
                raise CriticalConfigurationError(
                    f'Invalid binding config for {self._name}'
                    f'\nBinding definitions must be a dict or a string'
                    f'\n{self._raw_config}'
                )

            these_modes = binding_mode.split('__')
            for mode in these_modes:
                if mode not in concerned_modes:
                    concerned_modes.append(mode)

            these_modes.sort()
            sorted_mode_string = '__'.join(these_modes)

            parsed_target_string, status = self.action_resolver.compile(
                binding_def,
                self._vars,
                self._context,
            )

            if status != 0:
                raise ConfigurationError(
                    f'Unparseable target\n'
                    f'{binding_def}'
                )

            target_map = self.action_resolver.parse_target_path(parsed_target_string)

            if target_map['error'] is not None:
                raise ConfigurationError(target_map['error'])

            binding_dict[sorted_mode_string] = target_map

        if 'default' in binding_dict:
            self._default_map = binding_dict['default']
        else:
            self._default_map = list(binding_dict.values())[0]

        concerned_modes.sort()
        self._concerned_modes = concerned_modes
        self._binding_dict = binding_dict
        self._active_map = self._default_map

    def bind_to_active(self):
        if self._active_map is None:
            return
        self.map_self_to_par(self._active_map)
        dynamism = self.assess_dynamism(self._active_map)
        self.apply_listeners(dynamism)
        self.bind_control()

    def apply_listeners(self, listen_dict):

        if listen_dict.get('selected_track'):
            self.selected_track_listener.subject = self.song.view
        else:
            self.selected_track_listener.subject = None

        if listen_dict.get('track_list'):
            self.track_list_listener.subject = self.song
        else:
            self.track_list_listener.subject = None

        if listen_dict.get('device_list'):
            pass
        else:
            pass

        if listen_dict.get('parameter_list'):
            pass
        else:
            pass

        if listen_dict.get('chain_list'):
            pass
        else:
            pass

        if listen_dict.get('sends_list'):
            self.return_list_listener.subject = self.song
        else:
            self.return_list_listener.subject = None

        if listen_dict.get('selected_parameter'):
            self.selected_parameter_listener.subject = self.song.view
        else:
            self.selected_parameter_listener.subject = None

    def bind_control(self):
        if self._control_element is None:
            return
        self._control_element.connect_to(self._mapped_parameter)

    def map_self_to_par(self, target_map):
        try:
            par_type = target_map.get('parameter_type')
            if par_type is not None and par_type.lower() == 'selp':
                self._mapped_parameter = self.song.view.selected_parameter
                return True

            if target_map.get('device') is None:
                if target_map.get('track') is None:
                    raise ConfigurationError(f'Neither track nor device targeted:\n'
                                             f'{self._full_path}\n'
                                             f'{target_map}')

                track_def = target_map.get('track')
                track_obj = self.get_track(track_def)
                if track_obj is None:
                    raise ConfigurationError(f'No track found for {track_def}')

                par_type = target_map.get('parameter_type')
                if par_type is None:
                    raise ConfigurationError('Missing parameter_type')

                par_type = par_type.lower()

                if par_type == 'vol':
                    self._mapped_parameter = track_obj.mixer_device.volume
                    return True
                elif par_type == 'send':
                    try:
                        send_letter = target_map.get('send').upper()
                        send_num = ord(send_letter) - 65  # `A` in ASCII
                        sends_count = len(list(self.song.return_tracks))
                        if send_num < 0 or send_num >= sends_count:
                            raise ConfigurationError(f'Invalid send: {send_letter} | {send_num} | sends_count {sends_count}')

                        self._mapped_parameter = track_obj.mixer_device.sends[send_num]
                        return True
                    except Exception as e:
                        self.log(e)
                        raise ConfigurationError(f'Failed to bind to send: {e}')

                elif par_type == 'pan':
                    self._mapped_parameter = track_obj.mixer_device.panning
                    return True
                elif par_type == 'panl':
                    self._mapped_parameter = track_obj.mixer_device.left_split_stereo
                    return True
                elif par_type == 'panr':
                    self._mapped_parameter = track_obj.mixer_device.right_split_stereo
                    return True
                elif par_type == 'cue':
                    self._mapped_parameter = track_obj.mixer_device.cue_volume
                    return True
                elif par_type == 'xfader':
                    self._mapped_parameter = track_obj.mixer_device.crossfader
                    return True
                else:
                    raise ConfigurationError(f'Unsupported parameter type: {par_type}')
            else:
                track_def = target_map.get('track', 'SEL')
                track_obj = self.get_track(track_def)
                if track_obj is None:
                    raise ConfigurationError(f'No track found for {track_def}')

                device_def = target_map.get('device')

                par_def = target_map.get('parameter_name')

                if device_def.lower() == 'sel':
                    device_obj = track_obj.view.selected_device
                else:
                    try:
                        device_def = int(device_def) - 1
                        device_obj = list(track_obj.devices)[device_def]
                    except ValueError:
                        device_obj = self.get_device_from_list_by_name(list(track_obj.devices), device_def)
                    except IndexError as e:
                        return False

                if device_obj is None:
                    raise ConfigurationError(f'No device found for {device_def}')

                par_num = target_map.get('parameter_number')
                par_name = target_map.get('parameter_name')

                if isinstance(par_name, str):
                    if '${' in par_name:
                        parsed_par_name, status = self.action_resolver.parse_target_path(par_num)
                        if status != 0:
                            raise ConfigurationError(f'Failed to parse parameter: {par_num}')  # todo
                        par_name = parsed_par_name

                    for par in device_obj.parameters:
                        if par.name == par_name:
                            self._mapped_parameter = par
                            return True

                    raise ConfigurationError(f'Parameter "{par_def}" not found on device {device_def}')
                else:
                    if isinstance(par_num, str) and '${' in par_num:
                        parsed_par_num, status = self.action_resolver.parse_target_path(par_num)
                        if status != 0:
                            raise ConfigurationError(f'Failed to parse parameter: {par_num}') #todo
                        par_num = parsed_par_num
                    elif isinstance(par_num, int):
                        pass
                    else:
                        try:
                            par_num = int(par_num)
                        except ValueError:
                            raise ConfigurationError(f'Failed to parse parameter: {par_num}')
                    try:
                        self._mapped_parameter = device_obj.parameters[par_num]
                    except IndexError as e:
                        return False
                    return True

        except Exception as e:
            self.log(f'Error in map_self_to_par: {e}')
            raise

    @classmethod
    def get_device_from_list_by_name(cls, device_list, device_name):
        for device in device_list:
            if device.name == device_name:
                return device
            elif hasattr(device, 'chains'):
                for chain in device.chains:
                    result = cls.get_device_from_list_by_name(chain.devices, device_name)
                    if result is not None:
                        return result
        return None

    def assess_dynamism(self, target_map) -> dict:

        listen_dict = {
            "selected_track": False,
            "track_list": False,
            "device_list": False,
            "parameter_list": False,
            "chain_list": False,
            "sends_list": False,
            "selected_parameter": False,
        }

        track_def = target_map.get('track')
        if track_def is None:
            pass
        elif track_def.lower() == 'sel':
            listen_dict['selected_track'] = True
        else:
            listen_dict['track_list'] = True

        device_def = target_map.get('device')
        if device_def is None:
            pass
        elif device_def.lower() == 'sel':
            listen_dict['device_list'] = True

        chain_map = target_map.get('chain_map')
        if chain_map is None:
            pass
        else:
            listen_dict['chain_list'] = True

        sends_def = target_map.get('send_track')
        if sends_def is None:
            pass
        else:
            listen_dict['sends_list'] = True

        return listen_dict

    def rebind_from_dict(self, lookup_key:str):
        target_map = self._binding_dict.get(lookup_key)
        if map is None:
            return

        self._active_map = target_map
        self.bind_to_active()

    @listens('current_modes')
    def modes_changed(self, _):
        self.update_mode_string(_)
        if self._current_mode_string == '':
            mode_string = 'default'
        else:
            mode_string = self._current_mode_string
        self.rebind_from_dict(mode_string)

    def update_mode_string(self, mode_states):
        if len(self._concerned_modes) == 0:
            self._current_mode_string = ''
            return

        active_concerned_modes = [mode for mode in self._concerned_modes if mode_states.get(mode, False)]
        if not active_concerned_modes:
            self._current_mode_string = ""
        else:
            self._current_mode_string = "__" + "__".join(active_concerned_modes)

    @classmethod
    def get_track(cls, track_def):
        tracklist = list(cls.song.tracks)
        try:
            track_num = int(track_def) - 1
            return tracklist[track_num]
        except (ValueError, IndexError):
            track_obj = None
            if track_def.lower() == 'sel':
                return cls.song.view.selected_track
            elif track_def.lower() == 'mst':
                return cls.song.master_track
            else:
                for track in tracklist:
                    if track.name == track_def:
                        return track
                if track_obj is None:
                    return None

    @listens('selected_track')
    def selected_track_listener(self):
        self.bind_to_active()

    @listens('selected_parameter')
    def selected_parameter_listener(self):
        self.bind_to_active()

    @listens('selected_chain')
    def selected_chain_listener(self):
        self.bind_to_active()

    @listens('selected_device')
    def selected_device_listener(self):
        self.bind_to_active()

    @listens('devices')
    def device_list_listener(self):
        self.bind_to_active()

    @listens('tracks')
    def track_list_listener(self):
        self.bind_to_active()

    @listens('chains')
    def chain_list_listener(self):
        self.bind_to_active()

    @listens('parameters')
    def parameter_list_listener(self):
        self.bind_to_active()

    @listens('return_tracks')
    def return_list_listener(self):
        self.bind_to_active()
    