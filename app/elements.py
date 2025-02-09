import os
from functools import partial

from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from ableton.v3.control_surface import ElementsBase, create_matrix_identifiers
from ableton.v2.control_surface.elements.encoder import _map_modes
from .colors import ColorSwatches
from .consts import REQUIRED_HARDWARE_SPECS, APP_NAME
from .errors import HardwareSpecificationError
from .vendor.yaml import safe_load as load_yaml
from .z_element import ZElement
from .encoder_element import EncoderElement


class Elements(ElementsBase):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        from . import ROOT_LOGGER

        self.logger = ROOT_LOGGER.getChild(self.__class__.__name__)
        self.log = partial(self.logger.info, *a)

        self.named_buttons = {}
        self.encoders = {}

        specs_dict = self.load_specifications()
        self.specs = specs_dict["specs"]

        # cc buttons

        cc_button_globals = self.specs["cc_buttons"]
        cc_button_yaml = specs_dict["cc_buttons"]

        if cc_button_globals is None:
            pass
        else:
            self.process_cc_buttons(cc_button_globals.copy(), cc_button_yaml)

        # note buttons

        note_button_globals = self.specs["note_buttons"]
        note_button_yaml = specs_dict["note_buttons"]

        if note_button_globals is None:
            pass
        else:
            self.process_note_buttons(note_button_globals.copy(), note_button_yaml)

        # encoders

        encoder_globals = self.specs["encoders"]
        encoder_yaml = specs_dict["encoders"]

        self.process_encoders(encoder_globals, encoder_yaml)

        # matrix config todo: move to separate method

        matrix_config = self.specs.get("button_matrix")

        if matrix_config is None:
            raise HardwareSpecificationError(
                f"{APP_NAME} requires a button_matrix defined in hardware/specs.yaml to function"
            )

        matrix_msg_type = matrix_config["msg_type"]
        if matrix_msg_type == "note":
            matrix_msg_type = MIDI_NOTE_TYPE
        elif matrix_msg_type == "cc":
            matrix_msg_type = MIDI_CC_TYPE
        else:
            raise HardwareSpecificationError(
                f'button_matrix msg_type must be "note" or "cc", not {matrix_msg_type}'
            )

        matrix_button_factory = lambda *a, **k: self.element_factory(*a, **k)

        id_start, id_end, width = (
            matrix_config["id_start"],
            matrix_config["id_end"],
            matrix_config["width"],
        )
        channel = matrix_config.get("channel") or specs_dict.get("channel") or 0


        identifiers = matrix_config.get('raw_identifiers')
        if identifiers is None:
            identifiers = create_matrix_identifiers(
                id_start, id_end + 1, width, flip_rows=True
            )

        self.add_matrix(
            identifiers=identifiers,
            base_name="button_matrix",
            is_rgb=True,
            msg_type=matrix_msg_type,
            element_factory=matrix_button_factory,
        )

        feedback = matrix_config.get("feedback")
        if feedback in ['none', 'false', False, None]:
            feedback = 'basic'
        color_swatch = getattr(ColorSwatches, feedback)

        for element in self.button_matrix.nested_control_elements():
            element._color_swatch = color_swatch()
            element._feedback_type = feedback

        import sys

        mod = sys.modules[__package__]
        mod.NAMED_BUTTONS = self.named_buttons
        mod.ENCODERS = self.encoders

    def process_cc_buttons(self, cc_button_globals: dict, cc_button_yaml: dict) -> None:

        global_channel = cc_button_globals.get("channel", 0)
        global_momentary = cc_button_globals.get("momentary", True)
        global_feedback = cc_button_globals.get("feedback", "basic")

        for button_name, button_def in cc_button_yaml.items():
            cc_number = button_def["cc"]
            channel = button_def.get("channel", global_channel)
            momentary = button_def.get("momentary", global_momentary)
            feedback = button_def.get("feedback", global_feedback)
            if feedback in ['none', 'false', False, None]:
                feedback = 'basic'

            element = self.element_factory(
                identifier=cc_number,
                channel=channel,
                msg_type=MIDI_CC_TYPE,
                is_momentary=momentary,
                is_rgb=True,
            )

            color_swatch = getattr(ColorSwatches, feedback)
            element._color_swatch = color_swatch()
            element._feedback_type = feedback

            self.register_named_button(element, button_name)

    def process_note_buttons(
        self, note_button_globals: dict, note_button_yaml: dict
    ) -> None:

        global_channel = note_button_globals.get("channel", 0)
        global_momentary = note_button_globals.get("momentary", True)
        global_feedback = note_button_globals.get("feedback", "basic")

        for button_name, button_def in note_button_yaml.items():
            note_number = button_def["note"]
            channel = button_def.get("channel", global_channel)
            momentary = button_def.get("momentary", global_momentary)
            feedback = button_def.get("feedback", global_feedback)
            if feedback in ['none', 'false', False, None]:
                feedback = 'basic'

            element = self.element_factory(
                identifier=note_number,
                channel=channel,
                msg_type=MIDI_NOTE_TYPE,
                is_momentary=momentary,
                is_rgb=True,
            )

            color_swatch = getattr(ColorSwatches, feedback)
            element._color_swatch = color_swatch()
            element._feedback_type = feedback

            self.register_named_button(element, button_name)

    def process_encoders(
            self, encoders_globals: dict, encoders_yaml: dict
    ) -> None:

        global_channel = encoders_globals.get("channel", 0)
        global_feedback = encoders_globals.get("feedback", False)
        global_map_mode = encoders_globals.get("mode")
        global_sensitivity = encoders_globals.get("sensitivity", 1.0)

        for encoder_name, encoder_config in encoders_yaml.items():
            cc_number = encoder_config["cc"]
            channel = encoder_config.get("channel", global_channel)
            feedback = encoder_config.get("feedback", global_feedback)
            map_mode = encoder_config.get("mode", global_map_mode)
            sensitivity = encoder_config.get("sensitivity", global_sensitivity)

            element = self.encoder_factory(
                identifier=cc_number,
                channel=channel,
                is_feedback_enabled=feedback,
                map_mode=map_mode,
                sensitivity=sensitivity,
            )
            element.name = self.format_attribute_name(encoder_name)
            self.register_encoder(element, encoder_name)

    def element_factory(self, identifier=None, *a, **k) -> ZElement:
        element = ZElement(identifier=identifier, *a, **k)
        return element

    def encoder_factory(
            self,
            identifier=None,
            map_mode=None,
            is_feedback_enabled=False,
            channel=0,
            sensitivity=1.0,
            ):
        try:
            map_mode = getattr(_map_modes, map_mode.lower())
        except AttributeError:
            # todo: better error
            raise HardwareSpecificationError(
                f'Specified map_mode "{map_mode}" is not supported.'
            )
        element = EncoderElement(
            identifier=identifier,
            channel=channel,
            map_mode=map_mode,
            is_feedback_enabled=is_feedback_enabled,
            mapping_sensitivity=sensitivity,
        )
        return element

    def load_specifications(self) -> dict:

        try:
            _dict = {}

            def construct_yaml_path(filename):
                this_dir = os.path.dirname(__file__)
                hardware_dir = os.path.join(this_dir, "hardware")
                file_path = os.path.join(hardware_dir, f"{filename}.yaml")

                return file_path

            def load_yaml_file(path):
                with open(path, "r") as file:
                    return load_yaml(file)

            root_specs_path = construct_yaml_path("specs")
            root_specs = load_yaml_file(root_specs_path)

            if root_specs is None:
                raise HardwareSpecificationError("Could not load specs.yaml")

            _dict["specs"] = root_specs

            for spec_name in REQUIRED_HARDWARE_SPECS:
                if spec_name in root_specs:
                    path = construct_yaml_path(spec_name)
                    file = load_yaml_file(path)
                    if file is None:
                        raise HardwareSpecificationError(
                            f"Could not load {spec_name}.yaml"
                        )
                    _dict[spec_name] = file

            return _dict

        except Exception as e:
            raise HardwareSpecificationError(e)

    def register_named_button(self, button, name):
        if name in self.named_buttons:
            raise HardwareSpecificationError(
                f'Multiple buttons with the same name ("{name}")'
            )

        self.named_buttons[name] = button
        setattr(self, self.format_attribute_name(name), button)

    def register_encoder(self, encoder, name):
        if name in self.encoders:
            raise HardwareSpecificationError(
                f'Multiple encoders with the same name ("{name}")'
            )

        self.encoders[name] = encoder
        setattr(self, self.format_attribute_name(name), encoder)

    @staticmethod
    def format_attribute_name(name):
        return f"_button_{name.lower()}"
