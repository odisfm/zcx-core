import copy
from typing import Optional
from enum import Enum

from ableton.v3.base import EventObject, listens, listens_group, listenable_property

from ..errors import ConfigurationError, CriticalConfigurationError
from ..zcx_component import ZCXComponent
from ..z_control import ZControl
from .playable_z_control import PlayableZControl
from ..consts import REPEAT_RATES
from ..colors import parse_color_definition, ALL_LIVE_COLORS
repeat_rates_lower = [rate.lower() for rate in REPEAT_RATES]

class PitchClass(Enum):
    HIDDEN = "hidden"
    IN_KEY = "in_key"
    TONIC = "tonic"
    OUT_KEY = "out_key"
    OUT_OF_RANGE = "out_of_range"

class MelodicComponent(ZCXComponent):


    def __init__(
        self,
        name="MelodicComponent",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        self.__last_repeat_rate = None
        self.__base_status_message = None
        self.__color_dict = None
        self.__pad_section = None
        self.__width = 0
        self.__height = 0
        self.__original_channel = None
        self.__playable_channel = None
        self.__coords_to_controls: list[list[PlayableZControl]] = []
        self.__og_pitch_to_translated_pitch: list[int | None] = [None for _ in range(128)]
        self.__og_pitch_to_controls: list[PlayableZControl | None] = [None for _ in range(128)]
        self.__translated_pitches_to_controls: list[list[PlayableZControl]] = [[] for _ in range(128)]
        self.__concerned_pitches: list[int] = []
        self.__note_layout = "fourths"
        self.__octave = 3
        self.__does_exist = False
        self.__sounding_pitches = []
        self.__repeat_rate = 0
        self.__chromatic = False
        self.__full_velo = False
        self.__selected_track_color_index = None

    def _unload(self):
        self.__base_status_message = None
        self.__color_dict = None
        self.__pad_section = None
        self.__width = 0
        self.__height = 0
        self.__original_channel = None
        self.__playable_channel = None
        self.__coords_to_controls: list[list[PlayableZControl]] = []
        self.__og_pitch_to_translated_pitch: list[int | None] = [None for _ in range(128)]
        self.__og_pitch_to_controls: list[PlayableZControl | None] = [None for _ in range(128)]
        self.__translated_pitches_to_controls: list[list[PlayableZControl]] = [[] for _ in range(128)]
        self.__concerned_pitches: list[int] = []
        self.__note_layout = "fourths"
        self.__octave = 3
        self.__does_exist = False
        self.__sounding_pitches = []
        self.__repeat_rate = 0
        self.__chromatic = False
        self.__full_velo = False
        self.__selected_track_color_index = None

    @listens('scale_name')
    def _on_scale_name_change(self):
        self.update_translation()

    @listens("root_note")
    def _on_root_note_change(self):
        self.update_translation()

    @property
    def does_exist(self) -> bool:
        return self.__does_exist

    @listenable_property
    def octave(self):
        return self.__octave

    @octave.setter
    def octave(self, value):
        self.log("setting octave to {value}".format(value=value))
        if not isinstance(value, int):
            raise TypeError('Octave must be an integer')
        if not -1 < value < 11:
            raise ValueError('Octave must be between 0 and 10')
        self.__octave = value
        self.log("updating translation with octave {value}".format(value=value))
        self.update_translation()
        self.notify_octave(value)
        self.log("notified octave")

    @listenable_property
    def repeat_rate(self):
        return self.__repeat_rate

    @repeat_rate.setter
    def repeat_rate(self, value):
        value = value.lower()
        if value not in repeat_rates_lower:
            if value == "on":
                if self.__last_repeat_rate:
                    return setattr(self, "repeat_rate", self.__last_repeat_rate)
                else:
                    return setattr(self, "repeat_rate", "1/4")
            elif value == "toggle":
                if self.__repeat_rate == 0:
                    return setattr(self, "repeat_rate", "on")
                else:
                    return setattr(self, "repeat_rate", "off")
            raise ValueError(f'Invalid repeat rate `{value}`. Valid: {REPEAT_RATES}')
        self.canonical_parent.component_map["ActionResolver"].execute_command_bundle(
            None,
            f'CS "{self.canonical_parent.name}" RPT {value}',
            {},
            {}
        )
        if value != "off":
            self.__last_repeat_rate = value
        self.__repeat_rate = repeat_rates_lower.index(value.lower())
        self.notify_repeat_rate(value)

    @listenable_property
    def full_velo(self):
        return self.__full_velo

    @full_velo.setter
    def full_velo(self, value):
        if value == "toggle":
            self.full_velo = not self.full_velo
            return
        if not isinstance(value, bool):
            raise TypeError('Full velo must be a boolean')
        self.canonical_parent.component_map["ActionResolver"].execute_command_bundle(
            None,
            f'CS "{self.canonical_parent.name}" FULLVELO {"ON" if value else "OFF"}',
            {},
            {}
        )
        self.__full_velo = value
        self.notify_full_velo(value)

    @listenable_property
    def chromatic(self):
        return self.__chromatic

    @chromatic.setter
    def chromatic(self, value):
        if value == "toggle":
            self.chromatic = not self.chromatic
            return
        if not isinstance(value, bool):
            raise TypeError('Chromatic must be a boolean')
        self.__chromatic = value
        self.update_translation()
        self.notify_chromatic(value)

    @listenable_property
    def note_layout(self):
        return self.__note_layout

    @note_layout.setter
    def note_layout(self, value):
        if not value in NOTE_LAYOUTS:
            raise ValueError('Note layout must be one of {}'.format(NOTE_LAYOUTS))
        self.__note_layout = value
        self.update_translation()
        self.notify_note_layout(value)

    def increment_octave(self, increment: int):
        self.log(f"incrementing octave to {self.octave} += {increment}")
        self.octave = self.octave + increment

    def setup(self):
        section_def = self.component_map["PageManager"].get_special_section_definition('__keyboard')
        if section_def is None:
            self.debug('No __keyboard section defined')
            return

        zcx_matrix = self.component_map['HardwareInterface'].button_matrix_state

        self.__original_channel = zcx_matrix.get_control(0, 0)._control_element.message_channel()

        fake_nested = self.canonical_parent.elements.playable_matrix._nested_control_elements
        first_element = next(iter(fake_nested))
        self.__playable_channel = first_element.message_channel()

        section_obj: 'PadSection' = self.component_map["PageManager"].build_section(
            '__keyboard',
            section_def
        )
        self.__pad_section = section_obj

        self.__width = section_obj.width
        self.__height = section_obj.height

        self.__coords_to_controls = [[None for i in range(self.__width)] for j in range(self.__height)]


        for coord in section_obj.owned_coordinates:
            control = PlayableZControl(
                root_cs=self.canonical_parent,
                parent_section=section_obj,
                raw_config={},
                button_name=None,
            )
            state = zcx_matrix.get_control(coord[0], coord[1])
            control.bind_to_state(state)
            control.setup()
            _id = control._control_element.message_identifier()
            control._original_id = _id
            self.__concerned_pitches.append(_id)
            self.__og_pitch_to_controls[_id] = control
            x, y = (coord[0] - section_obj.bounds["min_y"], coord[1] - section_obj.bounds["min_x"])
            self.__coords_to_controls[x][y] = control
        self.__coords_to_controls.reverse()

        control_array = []
        controls = section_obj.owned_controls

        assert len(controls) == self.__width * self.__height

        for x in range(self.__width):
            column = []
            for y in range(self.__height):
                idx = x + (self.__width * y)
                column.append(controls[idx])
            control_array.append(column)

        base_status_message = 144 if controls[0]._control_element.message_type() == 0 else 176
        self.__base_status_message = base_status_message


        self.component_map["PageManager"].register_special_section_object(section_obj, '__keyboard')
        self.component_map["ZManager"].register_special_section_object(section_obj, '__keyboard')

        test_ctr = section_obj.owned_controls[0]
        color_dict = {
            "pressed": parse_color_definition("play_green", test_ctr).midi_value,
            "in_key": parse_color_definition("white", test_ctr).midi_value,
            "out_key": parse_color_definition("off", test_ctr).midi_value,
            "tonic": "track",
        }

        color_def_dict = section_def.get("colors", {})
        if not isinstance(color_def_dict, dict):
            raise ConfigurationError(f"Invalid color definition for `__keyboard`. Must be of type `dict` or absent.\n{color_def_dict}")

        for color_def in ["pressed", "in_key", "out_key", "tonic"]:
            _def = color_def_dict.get(color_def)
            if _def:
                if isinstance(_def, int) and 0 <= _def < 128:
                    color_dict[color_def] = _def
                elif isinstance(_def, str):
                    if "${" in _def:
                        self.warning(f"`__keyboard` color definition cannot use template strings. Using default color.")
                        continue
                    try:
                        if _def == "track":
                            color_dict[color_def] = "track"
                            continue
                        parse = parse_color_definition(_def, test_ctr)
                        if hasattr(parse, "midi_value") and 0 < parse.midi_value < 128:
                            color_dict[color_def] = parse.midi_value
                    except Exception as e:
                        self.warning(f"Failed to parse __keyboard color definition: {e}\n{section_def.get('colors')}")

        self.__color_dict = color_dict

        initial_octave_def = section_def.get("octave")
        if not initial_octave_def:
            pass
        elif not isinstance(initial_octave_def, int) or not 0 <= initial_octave_def <= 10:
            self.warning(f'Keyboard: invalid setting for octave `{initial_octave_def}`. Using default octave `{self.octave}`')
        else:
            self.__octave = initial_octave_def

        from .playable_state import PlayableState
        PlayableState.State.melodic_component = self
        self.__does_exist = True
        self._on_scale_name_change.subject = self.song
        if "track" in list(self.__color_dict.values()):
            self._on_selected_track_changed.subject = self.song.view
            self._on_color_index_changed.subject = self.song.view.selected_track

    def update_translation(self):
        if self.does_exist:
            self.canonical_parent._doing_note_translations = True
            self.canonical_parent.request_rebuild_midi_map()
            self._calculate_translations()
            self._apply_translation()
            self.canonical_parent._doing_note_translations = False
            self.refresh_all_feedback()

    def debug_translation(self):
        for i in range(128):
            o_p = self.__og_pitch_to_translated_pitch[i]
            if o_p:
                self.log(f'note {i} -> play note {o_p}')

    def _calculate_translations(
            self,
            scale_intervals: Optional[list[int]] = None,
            octave=None,
            chromatic=None,
            tonic_index=None,  # C♮
            layout=None
    ) -> None:

        if scale_intervals is None:
            scale_intervals = list(self.song.scale_intervals)
        if tonic_index is None:
            tonic_index = self.song.root_note
        if layout is None:
            layout = self.note_layout
        if chromatic is None:
            chromatic = self.chromatic
        if octave is None:
            octave = self.octave

        scale_len = len(scale_intervals)

        base_pitch = (octave * 12) + tonic_index

        self.__og_pitch_to_translated_pitch: list[int | None] = [None for _ in range(128)]
        self.__translated_pitches_to_controls: list[list[PlayableZControl]] = [[] for _ in range(128)]

        if not chromatic:
            if layout == "fourths":
                row_degrees = 3
            elif layout == "thirds":
                row_degrees = 2
            else:
                raise ValueError(f"Invalid layout: {layout}")

            for i, row in enumerate(self.__coords_to_controls):
                row_start_degree = i * row_degrees

                for j, control in enumerate(row):
                    og_pitch = control._original_id

                    current_scale_degree = row_start_degree + j
                    scale_degree_index = current_scale_degree % scale_len

                    octave_offset = (current_scale_degree // scale_len) * 12

                    scale_interval = scale_intervals[scale_degree_index]

                    if scale_interval == 0:
                        control._pitch_class = PitchClass.TONIC
                    else:
                        control._pitch_class = PitchClass.IN_KEY

                    pitch = base_pitch + scale_interval + octave_offset

                    if pitch < 0 or pitch > 127:
                        control._pitch_class = PitchClass.OUT_OF_RANGE
                    else:
                        self.__og_pitch_to_translated_pitch[og_pitch] = pitch
                        self.__translated_pitches_to_controls[pitch].append(control)
        else:
            if layout == "fourths":
                row_degrees = 5
            elif layout == "thirds":
                row_degrees = 4
            else:
                raise ValueError(f"Invalid layout: {layout}")

            for i, row in enumerate(self.__coords_to_controls):
                row_start_pitch = base_pitch + (i * row_degrees)
                for j, control in enumerate(row):
                    og_pitch = control._original_id

                    pitch = row_start_pitch + j

                    if pitch < 0 or pitch > 127:
                        control._pitch_class = PitchClass.OUT_OF_RANGE
                    else:
                        self.__og_pitch_to_translated_pitch[og_pitch] = pitch
                        self.__translated_pitches_to_controls[pitch].append(control)

                        semitone_distance_from_tonic = (pitch - base_pitch) % 12

                        if semitone_distance_from_tonic in scale_intervals:
                            scale_degree_index = scale_intervals.index(semitone_distance_from_tonic)
                            if scale_degree_index == 0:
                                control._pitch_class = PitchClass.TONIC
                            else:
                                control._pitch_class = PitchClass.IN_KEY
                        else:
                            control._pitch_class = PitchClass.OUT_KEY

    def _apply_translation(self):

        for p in range(128):
            if p not in self.__concerned_pitches:
                continue
            translated_pitch = self.__og_pitch_to_translated_pitch[p]

            control = self.__og_pitch_to_controls[p]
            control_in_view = control.in_view
            if translated_pitch is None or not control_in_view:
                new_pitch = p
                new_channel = self.__original_channel
                control._state.set_mode(1)
            else:
                new_pitch = translated_pitch
                new_channel = self.__playable_channel
                control._state.set_mode(2)

            self.canonical_parent._c_instance.set_note_translation(
                p,
                self.__original_channel,
                new_pitch,
                new_channel
            )

    @listens('selected_track')
    def _on_selected_track_changed(self):
        self._on_color_index_changed.subject = self.song.view.selected_track
        self._on_color_index_changed()

    @listens("color_index")
    def _on_color_index_changed(self):
        self.__update_selected_track_color_val()
        self.refresh_all_feedback()

    def _on_value(self, _id, value):
        if value:
            self.__add_sounding_pitch(_id)
        else:
            self.__remove_sounding_pitch(_id)

        self.refresh_single_pitch(_id)

    def get_color_for_pitch_class(self, pitch_class: PitchClass):
        match pitch_class:
            case PitchClass.HIDDEN:
                return 0
            case PitchClass.TONIC:
                return self._color_tonic
            case PitchClass.IN_KEY:
                return self._color_in_key
            case PitchClass.OUT_KEY:
                return self._color_out_key
            case PitchClass.OUT_OF_RANGE:
                return 0

    def __update_selected_track_color_val(self):
        self.__selected_track_color_index = ALL_LIVE_COLORS[self.song.view.selected_track.color_index].midi_value

    @property
    def selected_track_color(self):
        if not self.__selected_track_color_index:
            self.__update_selected_track_color_val()
        return self.__selected_track_color_index or ALL_LIVE_COLORS[self.song.view.selected_track.color_index].midi_value

    @property
    def _color_in_key(self):
        if self.__color_dict["in_key"] == "track":
            return self.selected_track_color
        return self.__color_dict["in_key"]

    @property
    def _color_out_key(self):
        if self.__color_dict["out_key"] == "track":
            return self.selected_track_color
        return self.__color_dict["out_key"]

    @property
    def _color_tonic(self):
        if self.__color_dict["tonic"] == "track":
            return self.selected_track_color
        return self.__color_dict["tonic"]

    @property
    def _color_pressed(self):
        if self.__color_dict["pressed"] == "track":
            return self.selected_track_color
        return self.__color_dict["pressed"]

    def refresh_single_pitch(self, t_pitch: int):
        try:
            messages = []
            controls = self.__translated_pitches_to_controls[t_pitch]
            if t_pitch in self.__sounding_pitches:
                vel = self._color_pressed
            else:
                vel = self.get_color_for_pitch_class(controls[0]._pitch_class)
            for control in controls:
                if not control.in_view or control._pitch_class in [PitchClass.OUT_OF_RANGE, PitchClass.HIDDEN]:
                    continue
                messages.append((self.__base_status_message + self.__original_channel, control._control_element.message_identifier(), vel))

            for msg in messages:
                self.canonical_parent._send_midi(msg)

        except Exception as e:
            self.error(e)

    def refresh_all_feedback(self):
        try:
            messages = []
            for i, t_pitch in enumerate(self.__og_pitch_to_translated_pitch):
                if not t_pitch:
                    continue
                control = self.__og_pitch_to_controls[i]
                if not control.in_view:
                    continue
                if t_pitch in self.__sounding_pitches:
                    vel = self._color_pressed
                else:
                    vel = self.get_color_for_pitch_class(control._pitch_class)
                messages.append((self.__base_status_message + self.__original_channel, i, vel))

            for msg in messages: # iterate again here to reduce time between each message
                self.canonical_parent._send_midi(msg)

        except Exception as e:
            self.critical(e)

    def __add_sounding_pitch(self, pitch):
        if pitch not in self.__sounding_pitches:
            self.__sounding_pitches.append(pitch)

    def __remove_sounding_pitch(self, pitch):
        if pitch in self.__sounding_pitches:
            self.__sounding_pitches.remove(pitch)
