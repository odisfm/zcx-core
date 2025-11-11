from copy import copy
from typing import TYPE_CHECKING

from ableton.v2.base.event import listenable_property, listens, listens_group

from .errors import ConfigurationError, CriticalConfigurationError
from .pad_section import PadSection
from .zcx_component import ZCXComponent

if TYPE_CHECKING:
    from .action_resolver import ActionResolver
    from .pad_section import PadSection
    from .page_manager import PageManager
    from .z_manager import ZManager
    from .z_control import ZControl


class ViewManager(ZCXComponent):

    def __init__(
        self,
        name="ViewManager",
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        self.__in_view_named_controls: "list[ZControl]" = []
        self.__in_view_matrix_controls: "list[ZControl]" = []
        self.__in_view_section_names: "list[PadSection]" = []
        self.__named_controls_section: "PadSection" = None
        self.__matrix_sections: "dict[str, PadSection]" = {}
        self.__overlay_sections: "dict[str, PadSection]" = {}
        self._z_manager: "ZManager" = None
        self._page_manager: "PageManager" = None
        self._action_resolver: "ActionResolver" = None
        self.__active_overlay_names: "list[str]" = []
        self.__overlay_details: dict[str, OverlayDetail] = {}
        self.__pages_to_overlays_in: list[list[str]] = []
        self.__pages_to_overlays_out: list[list[str]] = []
        self.__last_page_num = -1

    @property
    def in_view_controls(self):
        return copy(self.__in_view_named_controls)

    @listenable_property
    def active_overlay_names(self) -> "list[str]":
        return self.__active_overlay_names

    @property
    def all_overlay_names(self) -> "list[str]":
        return list(self.__overlay_sections.keys())

    def setup(self):
        self._z_manager: "PageManager" = self.component_map['ZManager']
        self._action_resolver: "ActionResolver" = self.component_map['ActionResolver']
        self._page_manager: "PageManager" = self.component_map['PageManager']
        matrix_sections = self._z_manager.all_matrix_sections
        self.__named_controls_section = self._z_manager.named_controls_section
        self.__matrix_sections = dict(sorted(matrix_sections.items(), key=lambda item: item[1].layer, reverse=False))
        self.__overlay_sections = dict(sorted(self._z_manager.all_overlay_sections.items(), key=lambda item: item[
            1].layer, reverse=False))

        self.__pages_to_overlays_in: list[list[int]] = [[] for _ in range(self._page_manager.page_count)]
        self.__pages_to_overlays_out: list[list[int]] = [[] for _ in range(self._page_manager.page_count)]

        for overlay_name, overlay_section_obj in self.__overlay_sections.items():
            overlay_def = overlay_section_obj.overlay_def
            overlay_detail = OverlayDetail(overlay_name, overlay_def)
            self.__overlay_details[overlay_name] = overlay_detail

            def parse_pages_def(key: str):
                pages_def = overlay_def.get(key, None )
                return_list = []
                if pages_def is None:
                    return None
                elif pages_def is True:
                    return [i for i in range(self._page_manager.page_count)]
                elif not isinstance(pages_def, list):
                    raise CriticalConfigurationError(f"Overlay `{overlay_name}` has invalid option for `{key}`. Must be a list or `true` for all pages. Provided:"
                                                     f"\n{pages_def}")
                for page in pages_def:
                    try:
                        if isinstance(page, int):
                            try:
                                test = self._page_manager.get_page_name_from_index(page)
                                return_list.append(page)
                            except IndexError:
                                raise ValueError()
                        elif isinstance(page, str):
                            _page_idx = self._page_manager.get_page_number_from_name(page)
                            if _page_idx is False:
                                raise ValueError()
                            return_list.append(_page_idx)
                        else:
                            raise ValueError()


                    except ValueError:
                        raise CriticalConfigurationError(f"Overlay `{overlay_name}` specifies page `{page}` which is not a valid page name or number."
                                                         f"\n{overlay_section_obj.overlay_def}")

                return return_list

            pages_in_parse = parse_pages_def("pages_in")
            pages_out_parse = parse_pages_def("pages_out")
            if isinstance(pages_in_parse, list) and len(pages_in_parse) > 0 and pages_out_parse is None:
                pages_out = pages_in_parse
            else:
                pages_out = pages_out_parse or []
            pages_in = pages_in_parse or []

            for page_idx in pages_in:
                self.__pages_to_overlays_in[page_idx].append(overlay_name)
            for page_idx in pages_out:
                self.__pages_to_overlays_out[page_idx].append(overlay_name)

        self._current_page_listener.subject = self._page_manager

    def _unload(self):
        self._pad_section_view_listener.replace_subjects([])

    @listens_group("in_view")
    def _pad_section_view_listener(self, pad_section: "PadSection"):
        if pad_section.name in self.__in_view_section_names:
            self.__in_view_section_names.remove(pad_section.name)
        else:
            self.__in_view_section_names.append(pad_section.name)

    @listens("current_page")
    def _current_page_listener(self):
        self._on_page_changed()
        self._update_in_view_controls()
        
    def _update_in_view_controls(self):
        named_set_in_view: "dict[str, tuple[ZControl, int, str]]" = {}
        matrix_set_in_view: "dict[tuple[int, int], tuple[ZControl, int, str]]" = {}

        overlay_matrix_section_names = set()

        for section_name, section_obj in self.__overlay_sections.items():
            if section_name not in self.__active_overlay_names:
                continue
            section_obj: "PadSection" = section_obj
            layer_idx = section_obj.layer
            overlay_detail = self.__overlay_details[section_name]
            overlay_matrix_section_names.update(overlay_detail.matrix_sections)

            for control in section_obj.owned_controls:
                if control.name.endswith(f"_{section_name}"):
                    base_name = control.name[:-len(f"_{section_name}")]
                else:
                    base_name = control.name

                existing_def = named_set_in_view.get(base_name)
                if existing_def:
                    existing_layer = existing_def[1]
                    existing_section_name = existing_def[2]
                    if existing_layer == layer_idx:
                        self.warning(f"Overlays `{section_name}` and `{existing_section_name}` share a layer ({layer_idx}) and the same control (`{base_name}`)\n"
                                     f"The control from `{section_name}` will be disabled.")
                        continue

                named_set_in_view[base_name] = (control, layer_idx, section_name)

        named_control_section_name = self.__named_controls_section.name
        for control in self.__named_controls_section.owned_controls:
            existing_def = named_set_in_view.get(control.name)
            if existing_def:
                continue
            named_set_in_view[control.name] = (control, 0, named_control_section_name)

        invoked_matrix_sections = set()
        current_page = self._page_manager.current_page
        for section_name in overlay_matrix_section_names:
            invoked_matrix_sections.add(self.__matrix_sections[section_name])
        for section_obj in self.__matrix_sections.values():
            if current_page in section_obj.in_pages:
                invoked_matrix_sections.add(section_obj)

        invoked_matrix_sections = list(invoked_matrix_sections)

        def sort_key(section):
            is_overlay = section.name in overlay_matrix_section_names
            return (is_overlay, section.layer)

        invoked_matrix_sections.sort(key=sort_key, reverse=True)

        for section_obj in invoked_matrix_sections:
            section_obj: "PadSection" = section_obj
            section_name = section_obj.name
            layer_idx = section_obj.layer
            for i, coord in enumerate(section_obj.owned_coordinates):
                control = section_obj.owned_controls[i]
                existing_def = matrix_set_in_view.get(coord)
                if existing_def:
                    existing_layer = existing_def[1]
                    existing_section_name = existing_def[2]
                    if existing_layer == layer_idx and existing_section_name not in overlay_matrix_section_names:
                        self.warning(f"Sections `{section_name}` and `{existing_section_name}` share a layer ({layer_idx}) and the same control (`idx #{i}`)\n"
                                     f"The control from `{section_name}` will be disabled.")
                    continue

                matrix_set_in_view[coord] = (control, layer_idx, section_name)
        named_to_enable = [entry[0] for entry in named_set_in_view.values()]
        matrix_to_enable = [entry[0] for entry in matrix_set_in_view.values()]

        named_to_disable = [control for control in self.__in_view_named_controls if control not in named_to_enable]
        matrix_to_disable = [control for control in self.__in_view_matrix_controls if control not in matrix_to_enable]

        for control in matrix_to_disable + named_to_disable:
            control.in_view = False
        for control in matrix_to_enable + named_to_enable:
            control.in_view = True
            control.request_color_update()

        self.__in_view_named_controls = named_to_enable
        self.__in_view_matrix_controls = matrix_to_enable
        self.component_map["MelodicComponent"].update_translation()
        self.component_map["MelodicComponent"].refresh_all_feedback()


    def debug_in_view(self):
        self.log(f"---- debug in view ----")
        for section_obj in self.__matrix_sections.values():
            self.log(f"{section_obj.name} >>")
            count = 0
            for control in section_obj.owned_controls:
                if control.in_view:
                    count += 1
            self.log(f"{count} out of {len(section_obj.owned_controls)} in view")

    def enable_overlay(self, overlay_name):
        if not overlay_name in self.__overlay_sections.keys():
            raise ValueError(f"Overlay `{overlay_name}` does not exist")
        if overlay_name not in self.__active_overlay_names:
            self.__active_overlay_names.append(overlay_name)
            self._update_in_view_controls()
        else:
            return
        detail = self.__overlay_details[overlay_name]
        bundle = detail.incoming_bundle
        if bundle is not None:
            self._action_resolver.execute_command_bundle(None, bundle, {}, detail.context)
        self.notify_active_overlay_names(self.__active_overlay_names)

    def disable_overlay(self, overlay_name):
        if not overlay_name in self.__overlay_sections.keys():
            raise ValueError(f"Overlay `{overlay_name}` does not exist")
        if overlay_name in self.__active_overlay_names:
            self.__active_overlay_names.remove(overlay_name)
            self._update_in_view_controls()
        else:
            return
        detail = self.__overlay_details[overlay_name]
        bundle = detail.outgoing_bundle
        if bundle is not None:
            self._action_resolver.execute_command_bundle(None, bundle, {}, detail.context)
        self.notify_active_overlay_names(self.__active_overlay_names)

    def toggle_overlay(self, overlay_name):
        if not overlay_name in self.__overlay_sections.keys():
            raise ValueError(f"Overlay `{overlay_name}` does not exist")
        if overlay_name in self.__active_overlay_names:
            self.disable_overlay(overlay_name)
        else:
            self.enable_overlay(overlay_name)

    def _on_page_changed(self):
        new_page_idx = self._page_manager.current_page
        names_to_remove = self.__pages_to_overlays_out[self.__last_page_num] if self.__last_page_num >= 0 else []
        names_to_add = self.__pages_to_overlays_in[new_page_idx]


        names_to_add, names_to_remove = self.remove_common_items(names_to_add, names_to_remove)
        names_to_add = self.remove_common_items(names_to_add, self.__active_overlay_names)[0]

        for overlay_name in names_to_remove:
            self.disable_overlay(overlay_name)
        for overlay_name in names_to_add:
            self.enable_overlay(overlay_name)

        self.__last_page_num = new_page_idx

    @staticmethod
    def remove_common_items(list1, list2):
        set2 = set(list2)
        set1 = set(list1)
        return ([item for item in list1 if item not in set2],
                [item for item in list2 if item not in set1]) or ([], [])

class OverlayDetail:

    def __init__(self, name, raw_config, layer=None):
        self.__name = name
        self.__raw_config = raw_config
        self.__layer = None
        self.__layer = layer or raw_config.get("layer") or 0
        self.__incoming_bundle = raw_config.get("on_enter")
        self.__outgoing_bundle = raw_config.get("on_leave")

        self.__context = {
            "overlay_name": self.__name,
            "overlay_layer": self.__layer,
        }
        self.__included_matrix_section_names = set(raw_config.get("matrix_sections", []))

    @property
    def name(self):
        return self.__name

    @property
    def layer(self):
        return self.__layer

    @property
    def incoming_bundle(self):
        return self.__incoming_bundle

    @property
    def outgoing_bundle(self):
        return self.__outgoing_bundle

    @property
    def context(self):
        return self.__context

    @property
    def matrix_sections(self) -> list[str]:
        return self.__included_matrix_section_names

