from .zcx_component import ZCXComponent
from typing import TYPE_CHECKING
from .z_controls.session_clip_control import SessionClipControl
from ableton.v3.base import listens
from .colors import parse_color_definition, Pulse, Blink, RgbColor

if TYPE_CHECKING:
    from .page_manager import PageManager
    from .pad_section import PadSection
    from .session_ring import SessionRing

DEFAULT_GESTURES = {
    "pressed": '"${track_name}" / PLAY ${scene_number}',
    "pressed__select": '"${track_name}" / SEL ${scene_number}'
}

class SessionView(ZCXComponent):

    def __init__(
            self,
            name="SessionView",
            *a,
            **k,
    ):
        super().__init__(name=name, *a, **k)
        self.__pad_section = None
        self.__page_manager: 'PageManager' = None
        self._session_ring = None
        self.__color_dict_lookup = []
        self.__empty_color_dict = {}
        self.__width = 0
        self.__height = 0
        self.__control_array = None

    def setup(self):
        self.__page_manager: 'PageManager' = self.component_map['PageManager']
        self._session_ring = self.canonical_parent._session_ring_custom

        section_def = self.__page_manager.get_special_section_definition('__session_view')
        if section_def is None:
            self.debug('No session view section defined')
            return

        mode_manager = self.component_map['ModeManager']
        if not "select" in mode_manager.all_modes:
            del DEFAULT_GESTURES["pressed__select"]

        control_config = {}
        gesture_def= section_def.get('template', {}).get('gestures', {})
        control_config["gestures"] = DEFAULT_GESTURES | gesture_def

        matrix_state = self.component_map['HardwareInterface'].button_matrix_state

        section_obj: 'PadSection' = self.__page_manager.build_section(
            '__session_view',
            section_def
        )
        self.__pad_section = section_obj

        self.__width = section_obj.width
        self.__height = section_obj.height

        self.__create_color_dict_lookup()

        SessionClipControl.session_view_component = self
        SessionClipControl.empty_color_dict = self.__empty_color_dict

        for coord in section_obj.owned_coordinates:
            control = SessionClipControl(
                root_cs=self.canonical_parent,
                parent_section=section_obj,
                raw_config=control_config,
                button_name=None,
            )
            state = matrix_state.get_control(coord[0], coord[1])
            control.bind_to_state(state)
            control.setup()

        control_array = []
        controls = section_obj.owned_controls

        assert len(controls) == self.__width * self.__height

        for x in range(self.__width):
            column = []
            for y in range(self.__height):
                idx = x + (self.__width * y)
                column.append(controls[idx])
            control_array.append(column)

        self.__control_array = control_array

        self.ring_offsets_changed.subject = self._session_ring
        self.tracks_changed.subject = self._song
        self.update_clip_slot_assignments()
        self.pad_section.current_page_listener()

    def _unload(self):
        super()._unload()
        self.__pad_section = None
        self.__page_manager: 'PageManager' = None
        self._session_ring = None
        self.__color_dict_lookup = []
        self.__empty_color_dict = {}
        self.__width = 0
        self.__height = 0
        self.__control_array = None

    @listens('offsets')
    def ring_offsets_changed(self):
        self.update_clip_slot_assignments()

    def __create_color_dict_lookup(self):
        lookup = []

        play_green = parse_color_definition("green")
        red = parse_color_definition("red")
        arm = parse_color_definition("arm_red")
        off = parse_color_definition(0)
        triggered_to_record = parse_color_definition({"blink": {
            "a": "red",
            "b": 0
        }}
        )

        for i in range(70):
            base_color = parse_color_definition({"live": i})

            color_dict = {"base": base_color}

            color_dict['playing'] = parse_color_definition({"pulse": {
                "a": 'play_green',
                "b": '0',
                'speed': 0
            }})
            color_dict['recording'] = parse_color_definition({"pulse": {
                "a": "red",
                "b": "0",
                "speed": 1
                }}
            )
            color_dict['triggered_to_play'] = parse_color_definition({"blink": {
                "a": "play_green",
                "b": {"live": i}
            }}
            )
            color_dict['triggered_to_record'] = triggered_to_record
            color_dict['arm'] = arm

            lookup.append(color_dict)

        self.__empty_color_dict = {
            "base": off,
            "playing": off,
            "triggered_to_play": parse_color_definition({"blink": {
                "a": 'play_green',
                "b": '0',
                "speed": 1,
            }}),
            "triggered_to_record": triggered_to_record,
            "recording": off,
            "arm": arm
        }

        self.__color_dict_lookup = lookup

    def get_color_dict(self, color_index):
        return self.__color_dict_lookup[color_index]

    def update_clip_slot_assignments(self):
        tracks_to_use = self._session_ring.tracks_in_view
        scene_offset = self._session_ring.offsets['scene_offset']

        if len(tracks_to_use) > len(self.__control_array):
            tracks_to_use = tracks_to_use[:len(self.__control_array)]

        for i, track in enumerate(tracks_to_use):
            controls = self.__control_array[i]
            for j, control in enumerate(controls):
                control.set_clip_slot(track.clip_slots[j + scene_offset])

    @listens('tracks')
    def tracks_changed(self):
        self.update_clip_slot_assignments()

    @property
    def pad_section(self):
        return self.__pad_section
