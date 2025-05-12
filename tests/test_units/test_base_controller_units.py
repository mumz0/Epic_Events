import sys
import unittest
from unittest.mock import MagicMock, patch

import urwid

from src.controllers.base_controller import BaseController
from src.models.contract import Contract
from src.models.event import Event


# Helpers définis au niveau du module pour éviter d'imbriquer des fonctions
def update_screen_side_effect(base_view, widget=None):
    base_view.updated_widget = widget if widget is not None else base_view.loop.widget


def create_menu_layout_side_effect(title, labels):
    buttons = []
    for label in labels:
        button = MagicMock()
        button.base_widget = button
        button.get_label.return_value = label
        buttons.append(button)
    layout = f"layout_for_{title}"
    return buttons, layout


def create_object_details_frame_side_effect(title, selected_object, buttons_labels):
    frame = f"details_frame_{title}"
    buttons = [MagicMock() for _ in buttons_labels]
    return frame, buttons


def create_pre_filled_form_page_side_effect(object_template, title):
    edit = MagicMock()
    edit.caption = "Field: "
    edit.get_edit_text.return_value = object_template.get("Field", "")
    return {"buttons": MagicMock(), "layout": f"pre_filled_layout_{title}", "edits": [edit]}


def create_delete_confirmation_popup_layout_side_effect():
    layout = "delete_confirmation_layout"
    button_yes = MagicMock()
    button_no = MagicMock()
    return layout, [button_yes, button_no]


class TestBaseController(unittest.TestCase):

    def dummy_button_func(self):
        self.func_called = True

    # Ces méthodes serviront d'actions pour tester connect_button_signals.
    def action1(self, button):
        self.flag["btn1"] = True

    def action2(self, button):
        self.flag["btn2"] = True

    def setUp(self):
        self.session = {}
        self.current_user = "test_user"
        self.history = []
        self.base_view = MagicMock()
        self.base_view.loop = MagicMock()
        self.base_view.loop.widget = "initial_widget"
        # Affectation des side_effects à l'aide des helpers externes
        self.base_view.update_screen.side_effect = lambda widget=None: update_screen_side_effect(self.base_view, widget)
        self.base_view.create_menu_layout.side_effect = create_menu_layout_side_effect
        self.base_view.create_object_details_frame.side_effect = create_object_details_frame_side_effect
        self.base_view.create_pre_filled_form_page.side_effect = create_pre_filled_form_page_side_effect
        self.base_view.create_delete_confirmation_popup_layout.side_effect = create_delete_confirmation_popup_layout_side_effect

        self.controller = BaseController(self.session, self.base_view, self.current_user, self.history)

    def test_handle_exit_click_calls_sys_exit(self):
        with self.assertRaises(SystemExit):
            self.controller.handle_exit_click()

    def test_cancel_popup_updates_screen_with_last_history(self):
        self.history.extend(["screen1", "screen2"])
        self.controller.cancel_popup()
        self.assertEqual(self.history, ["screen1"])
        self.assertEqual(self.base_view.updated_widget, "screen1")

    def test_remove_popup_updates_screen_after_popping_two(self):
        self.history.extend(["screen1", "screen2", "screen3"])
        self.controller.remove_popup()
        self.assertEqual(self.history, ["screen1"])
        self.assertEqual(self.base_view.updated_widget, "screen1")

    def test_handle_button_pressed_executes_function(self):
        self.func_called = False
        self.controller.handle_button_pressed(self.dummy_button_func)
        self.assertTrue(self.func_called)

    def test_handle_back_keypress_shows_exit_confirmation_when_at_root(self):
        self.history.append("widget_root")
        self.base_view.loop.widget = "widget_root"
        with patch.object(self.controller, "show_exit_confirmation") as mock_exit_popup:
            self.controller.handle_back_keypress("esc")
            mock_exit_popup.assert_called_once()

    @patch("urwid.connect_signal", return_value=None)
    def test_menu_updates_screen_and_history_when_title_contains_home(self, mock_connect_signal):
        menu_items = [("Home Option", lambda: None), ("Other Option", lambda: None)]
        title = "Home Menu"
        self.controller.menu(title, menu_items)
        self.assertTrue(self.history)
        self.assertEqual(self.history[-1], f"layout_for_{title}")
        self.assertEqual(self.base_view.updated_widget, f"layout_for_{title}")

    def test_select_item_in_lst_returns_correct_object(self):
        # Simulation d'objets avec un get_identifier
        obj1 = MagicMock()
        obj1.get_identifier.return_value = "item1"
        obj1.id = "item1"
        obj2 = MagicMock()
        obj2.get_identifier.return_value = "item2"
        obj2.id = "item2"
        other = MagicMock()
        other.email_address = "email@example.com"
        found = self.controller.select_item_in_lst([obj1, obj2, other], "item2")
        self.assertEqual(found, obj2)
        not_found = self.controller.select_item_in_lst([obj1], "nonexistent")
        self.assertIsNone(not_found)

    def test_object_details_layout_calls_create_details_frame_and_updates_screen(self):
        selected_obj = MagicMock()
        selected_obj.id = "item1"
        buttons_labels = ["btn1", "btn2"]
        frame, _ = self.base_view.create_object_details_frame("Detail Title", selected_obj, buttons_labels)
        dummy_controller = MagicMock()
        self.controller.object_details_layout("Detail Title", selected_obj, dummy_controller, buttons_labels)
        self.assertIn(frame, self.history)
        self.assertEqual(self.base_view.updated_widget, frame)
        dummy_controller.create_details_view_buttons_signal.assert_called()

    def test_pre_filled_form_page_updates_screen(self):
        object_template = {"Field": "value"}
        title = "Form Page"
        with patch("urwid.connect_signal"):
            self.controller.pre_filled_form_page(title, object_template, MagicMock(), MagicMock())
            self.assertEqual(self.base_view.updated_widget, f"pre_filled_layout_{title}")

    def test_handle_save_button_calls_service_with_correct_data(self):
        dummy_edit = MagicMock()
        dummy_edit.caption = "Name: "
        dummy_edit.get_edit_text.return_value = "TestName"
        edit_labels = [dummy_edit]
        dummy_obj = MagicMock()
        dummy_obj.id = "123"
        service = MagicMock()
        self.history.extend(["screen1", "screen2", "screen3"])
        self.controller.handle_save_button(edit_labels, dummy_obj, service)
        service.prepare_data_and_update.assert_called_once_with({"Name": "TestName"}, dummy_obj, self.session)
        self.assertEqual(len(self.history), 1)
        self.assertEqual(self.base_view.updated_widget, self.history[0])

    def test_show_delete_confirmation_updates_screen(self):
        dummy_obj = MagicMock()
        dummy_obj.id = "123"
        service = MagicMock()
        with patch("urwid.connect_signal") as mock_connect:
            self.controller.show_delete_confirmation(dummy_obj, service)
            self.assertEqual(self.base_view.updated_widget, "delete_confirmation_layout")
            self.assertEqual(mock_connect.call_count, 2)

    def test_handle_confirmation_delete_calls_service_and_removes_popup(self):
        service = MagicMock()
        self.history.extend(["screen1", "screen2", "screen3"])
        self.controller.handle_confirmation_delete("123", service)
        service.delete.assert_called_once_with("123", self.session)
        self.assertEqual(len(self.history), 1)

    def test_get_button_data_for_items_returns_ids_or_email_address(self):
        contract = MagicMock(spec=Contract)
        contract.id = "contract1"
        event = MagicMock(spec=Event)
        event.id = "event1"
        other = MagicMock()
        other.email_address = "other@example.com"
        result = self.controller.get_button_data_for_items([contract, event, other])
        self.assertEqual(result, ["contract1", "event1", "other@example.com"])

    def test_connect_button_signals_with_dict_and_list(self):
        btn1 = MagicMock()
        btn1.get_label.return_value = "btn1"
        btn2 = MagicMock()
        btn2.get_label.return_value = "btn2"
        buttons_dict = {"other_buttons": [btn1, btn2]}
        self.flag = {"btn1": False, "btn2": False}
        button_actions = [("btn1", self.action1), ("btn2", self.action2)]
        with patch("urwid.connect_signal") as mock_connect:
            self.controller.connect_button_signals(buttons_dict, button_actions)
            self.assertEqual(mock_connect.call_count, 2)
        btn3 = MagicMock()
        btn3.get_label.return_value = "btn3"
        btn4 = MagicMock()
        btn4.get_label.return_value = "btn4"
        buttons_list = [btn3, btn4]
        button_actions = [("btn3", self.action1), ("btn4", self.action2)]
        with patch("urwid.connect_signal") as mock_connect_list:
            self.controller.connect_button_signals(buttons_list, button_actions)
            self.assertEqual(mock_connect_list.call_count, 2)
