import time
from zcx_test_case import ZCXTestCase


class TestUserAction(ZCXTestCase):

    def test_ua_mode(self):
        mode_to_test = "shift"
        self.assertFalse(self._mode_manager.check_mode_state(mode_to_test))
        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} MODE ON {mode_to_test}")
        self.assertTrue(self._mode_manager.check_mode_state(mode_to_test))
        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} MODE OFF {mode_to_test}")
        self.assertFalse(self._mode_manager.check_mode_state(mode_to_test))
        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} MODE TGL {mode_to_test}")
        self.assertTrue(self._mode_manager.check_mode_state(mode_to_test))
        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} MODE TGL {mode_to_test}")
        self.assertFalse(self._mode_manager.check_mode_state(mode_to_test))

    def test_ua_page(self):
        self.assertEqual(self._page_manager.current_page, 0)
        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} PAGE NEXT")
        self.assertEqual(self._page_manager.current_page, 1)
        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} PAGE PREV")
        self.assertEqual(self._page_manager.current_page, 0)
        page_names = self._page_manager.all_page_names

        for i, page_name in enumerate(page_names):
            self._cxp_bridge.trigger_action_list(f'ZCX {self.zcx.name} PAGE {page_name}')
            self.assertEqual(self._page_manager.current_page, i)

    def test_ua_color(self):
        indv_control_name = "test_ua_colors_individual"
        indv_control = self.zcx_api.get_control(indv_control_name)
        self.assertIsNotNone(indv_control)
        section_name = "test_ua_colors"
        section = self.zcx_api.get_matrix_section(section_name)
        self.assertIsNotNone(section)
        group_name = "test_ua_colors_group"
        group = self.zcx_api.get_control_group(group_name)
        self.assertIsNotNone(group)
        for i, control in enumerate(section.owned_controls):
            self.assertEqual(control.color.midi_value, 1)

        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} SET_COLOR {indv_control_name} 2")
        self.assertEqual(indv_control.color.midi_value, 2)
        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} SET_SECTION_COLOR {section_name} 2")
        for i, control in enumerate(section.owned_controls):
            self.assertEqual(control.color.midi_value, 2)

        for i, control in enumerate(group):
            self.assertEqual(control.color.midi_value, 1)

        self._cxp_bridge.trigger_action_list(f"ZCX {self.zcx.name} SET_GROUP_COLOR {group_name} 2")

        for i, control in enumerate(group):
            self.assertEqual(control.color.midi_value, 2)
