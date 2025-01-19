import logging
import os
from functools import partial

from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from ableton.v3.control_surface import ElementsBase, create_matrix_identifiers
from ableton.v3.control_surface.elements import ButtonElement
from .consts import REQUIRED_HARDWARE_SPECS, APP_NAME
from .errors import HardwareSpecificationError
from .vendor.yaml import safe_load as load_yaml


class Elements(ElementsBase):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.logger = logging.getLogger(__name__)
        self.log = partial(self.logger.info, *a)

        self.named_buttons = {}

        specs_dict = self.load_specifications()
        self.specs = specs_dict['specs']

        cc_button_globals = self.specs['cc_buttons']
        cc_button_yaml = specs_dict['cc_buttons']

        if cc_button_globals is None:
            pass
        else:
            self.process_cc_buttons(cc_button_globals.copy(), cc_button_yaml)

        note_button_globals = self.specs['note_buttons']
        note_button_yaml = specs_dict['note_buttons']

        if note_button_globals is None:
            pass
        else:
            self.process_note_buttons(note_button_globals.copy(), note_button_yaml)

        matrix_config = self.specs.get('button_matrix')

        if matrix_config is None:
            raise HardwareSpecificationError(
                f'{APP_NAME} requires a button_matrix defined in hardware/specs.yaml to function')

        matrix_msg_type = matrix_config['msg_type']
        if matrix_msg_type not in ['note', 'cc']:
            raise HardwareSpecificationError(f'button_matrix msg_type must be "note" or "cc", not {matrix_msg_type}')

        matrix_button_factory = partial(self.element_factory, msg_type=matrix_msg_type)

        id_start, id_end, width = matrix_config['id_start'], matrix_config['id_end'], matrix_config['width']
        channel = matrix_config.get('channel') or specs_dict.get('channel') or 0

        identifiers = create_matrix_identifiers(id_start, id_end, width, flip_rows=True)

        self.button_matrix = self.add_matrix(
            identifiers=identifiers,
            base_name='button_matrix',
            channels=channel,
            element_factory=matrix_button_factory,
            is_private=False
        )

        self.log(self.button_matrix)

    def process_cc_buttons(self, cc_button_globals: dict, cc_button_yaml: dict) -> None:
        self.log('Parsing cc buttons')

        global_channel = cc_button_globals.get('channel', 0)
        global_momentary = cc_button_globals.get('momentary', True)
        global_feedback = cc_button_globals.get('feedback', 'basic')

        for button_name, button_def in cc_button_yaml.items():
            cc_number = button_def['cc']
            channel = button_def.get('channel', global_channel)
            momentary = button_def.get('momentary', global_momentary)
            feedback = button_def.get('feedback', global_feedback)

            element = self.element_factory(
                identifier=cc_number,
                channel=channel,
                msg_type=MIDI_CC_TYPE,
                is_momentary=momentary
            )

            # setattr(element, feedback_type, feedback) todo

            self.register_named_button(element, button_name)

    def process_note_buttons(self, note_button_globals: dict, note_button_yaml: dict) -> None:
        self.log('Parsing note buttons')

        global_channel = note_button_globals.get('channel', 0)
        global_momentary = note_button_globals.get('momentary', True)
        global_feedback = note_button_globals.get('feedback', 'basic')

        for button_name, button_def in note_button_yaml.items():
            note_number = button_def['note']
            channel = button_def.get('channel', global_channel)
            momentary = button_def.get('momentary', global_momentary)
            feedback = button_def.get('feedback', global_feedback)

            element = self.element_factory(
                identifier=note_number,
                channel=channel,
                msg_type=MIDI_NOTE_TYPE,
                is_momentary=momentary
            )

            # setattr(element, feedback_type, feedback) todo

            self.register_named_button(element, button_name)

    def element_factory(self, identifier, channel=0, msg_type=MIDI_CC_TYPE, is_momentary=True, *a,
                        **k) -> ButtonElement:
        return ButtonElement(identifier, channel=channel, msg_type=msg_type, is_momentary=is_momentary)

    def load_specifications(self) -> dict:

        try:
            _dict = {}

            def construct_yaml_path(filename):
                this_dir = os.path.dirname(__file__)
                hardware_dir = os.path.join(this_dir, 'hardware')
                file_path = os.path.join(hardware_dir, f'{filename}.yaml')

                return file_path

            def load_yaml_file(path):
                with open(path, 'r') as file:
                    return load_yaml(file)

            root_specs_path = construct_yaml_path('specs')
            root_specs = load_yaml_file(root_specs_path)

            if root_specs is None:
                raise HardwareSpecificationError('Could not load specs.yaml')

            _dict['specs'] = root_specs

            for spec_name in REQUIRED_HARDWARE_SPECS:
                if spec_name in root_specs:
                    path = construct_yaml_path(spec_name)
                    file = load_yaml_file(path)
                    if file is None:
                        raise HardwareSpecificationError(f"Could not load {spec_name}.yaml")
                    _dict[spec_name] = file

            return _dict

        except Exception as e:
            raise HardwareSpecificationError(e)

    def register_named_button(self, button, name):
        if name in self.named_buttons:
            raise HardwareSpecificationError(f'Multiple buttons with the same name ("{name}")')

        self.named_buttons[name] = button
