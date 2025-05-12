import os
import time
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import click
import urwid

from src.views.base_view import BaseView


# Dummy class to override the Ascii dependency (used in __init__)
class DummyAscii:
    def epic_events(self):
        return "ASCII_ART"


# Dummy object with a to_dict() method for create_card and create_object_details_frame
class DummyObj:
    def to_dict(self):
        return {"name": "Test Object", "created": datetime(2023, 10, 1)}


class TestBaseView(unittest.TestCase):
    def setUp(self):
        # Patch Ascii so that ascii_art becomes deterministic.
        patcher = patch("src.views.base_view.Ascii", return_value=DummyAscii())
        self.addCleanup(patcher.stop)
        patcher.start()
        self.base_view = BaseView()
        # Create a dummy loop (with dummy screen) for methods that use self.loop
        self.dummy_loop = MagicMock()
        self.dummy_loop.screen = MagicMock()
        self.base_view.loop = self.dummy_loop

    def test_init(self):
        # __init__ should set ascii_art using DummyAscii.epic_events()
        self.assertEqual(self.base_view.ascii_art, "ASCII_ART")

    @patch("builtins.input", side_effect=["user@example.com", "secret"])
    def test_admin_signup_view(self, mock_input):
        email, password = self.base_view.admin_signup_view()
        self.assertEqual(email, "user@example.com")
        self.assertEqual(password, "secret")
        self.assertEqual(mock_input.call_count, 2)

    def test_init_main_loop(self):
        dummy_layout = MagicMock()
        dummy_unhandled = lambda x: None
        self.base_view.init_main_loop(dummy_layout, dummy_unhandled)
        self.assertIsNotNone(self.base_view.loop)
        self.assertIsInstance(self.base_view.loop, urwid.MainLoop)

    def test_update_screen(self):
        dummy_widget = MagicMock()
        self.base_view.update_screen(dummy_widget)
        self.assertEqual(self.base_view.loop.widget, dummy_widget)
        self.dummy_loop.screen.clear.assert_called_once()
        self.dummy_loop.draw_screen.assert_called_once()

    def test_create_button(self):
        button = self.base_view.create_button("Click Me")
        self.assertIsInstance(button, urwid.Button)
        self.assertEqual(button.get_label(), "Click Me")

    @patch("os.system")
    def test_clear_screen(self, mock_system):
        orig_os_name = os.name
        try:
            os.name = "nt"
            self.base_view.clear_screen()
            mock_system.assert_called_with("cls")
            mock_system.reset_mock()
            os.name = "posix"
            self.base_view.clear_screen()
            mock_system.assert_called_with("clear")
        finally:
            os.name = orig_os_name

    def test_create_header_body(self):
        title = "Menu Title"
        header = self.base_view.create_header_body(title)
        # The header list should include a Text widget (logo), a LineBox (title) and a Divider.
        self.assertIsInstance(header, list)
        self.assertTrue(any(isinstance(widget, urwid.Text) for widget in header))
        self.assertTrue(any(isinstance(widget, urwid.LineBox) for widget in header))
        self.assertTrue(any(isinstance(widget, urwid.Divider) for widget in header))

    def test_create_buttons(self):
        labels = ["One", "Two"]
        buttons = self.base_view.create_buttons(labels)
        self.assertEqual(len(buttons), 2)
        for btn_attr, label in zip(buttons, labels):
            self.assertIsInstance(btn_attr, urwid.AttrMap)
            self.assertEqual(btn_attr.original_widget.get_label(), label)

    def test_create_menu_body(self):
        header_body = [urwid.Text("Header")]
        labels = ["A", "B"]
        body, buttons = self.base_view.create_menu_body(header_body, labels)
        # body should be header followed by the buttons widgets
        self.assertTrue(all(item in body for item in header_body))
        self.assertEqual(len(buttons), 2)
        for btn in buttons:
            self.assertIsInstance(btn, urwid.AttrMap)

    def test_create_frame(self):
        body = [urwid.Text("Line1"), urwid.Text("Line2")]
        frame = self.base_view.create_frame(body)
        self.assertIsInstance(frame, urwid.Frame)

    @patch.object(BaseView, "clear_screen")
    def test_create_menu_layout(self, mock_clear_screen):
        title = "Main Menu"
        button_labels = ["Start", "Quit"]
        buttons, layout = self.base_view.create_menu_layout(title, button_labels)
        mock_clear_screen.assert_called_once()
        self.assertIsInstance(buttons, list)
        self.assertIsInstance(layout, urwid.Widget)

    def test_create_form_layout(self):
        title = "Form"
        button_labels = ["Submit"]
        edit_labels = ["Name", "Age"]
        layout_dict = self.base_view.create_form_layout(title, button_labels, edit_labels)
        self.assertIn("edits", layout_dict)
        self.assertIn("buttons", layout_dict)
        self.assertIn("layout", layout_dict)
        self.assertEqual(len(layout_dict["edits"]), 2)
        # buttons should be a list of button widgets
        self.assertIsInstance(layout_dict["buttons"], list)

    @patch("time.sleep", return_value=None)
    @patch("click.echo")
    @patch("urwid.MainLoop")
    def test_display_message(self, mock_mainloop, mock_click_echo, mock_sleep):
        dummy_loop = MagicMock()
        dummy_loop.screen = MagicMock()
        mock_mainloop.return_value = dummy_loop
        self.base_view.display_message("Hello World")
        mock_click_echo.assert_called_once_with("Hello World")
        dummy_loop.screen.start.assert_called_once()
        dummy_loop.screen.stop.assert_called_once()
        mock_sleep.assert_called_once_with(2)

    def test_create_card(self):
        dummy_obj = DummyObj()
        card = self.base_view.create_card(dummy_obj)
        self.assertIsInstance(card, urwid.Filler)
        pile = card.original_widget
        linebox = pile.contents[0][0]
        padding = linebox.original_widget
        text_widget = padding.original_widget
        text, _ = text_widget.get_text()
        self.assertIn("test object", text.lower())

    def test_create_object_details_frame(self):
        title = "Details"
        dummy_obj = DummyObj()
        buttons_labels = {"buttons_label": ["Edit", "Delete"]}
        frame, buttons = self.base_view.create_object_details_frame(title, dummy_obj, buttons_labels)
        self.assertIsInstance(frame, urwid.Frame)
        self.assertEqual(len(buttons), 2)
        # Verify that one of the buttons has the label "Edit"
        labels = [btn.get_label() for btn in buttons]
        self.assertIn("Edit", labels)

    def test_create_pre_filled_form_page(self):
        object_template = {"Name": "John", "Age": 30}
        title = "Edit User"
        layout_dict = self.base_view.create_pre_filled_form_page(object_template, title)
        self.assertIn("edits", layout_dict)
        self.assertIn("buttons", layout_dict)
        self.assertIn("layout", layout_dict)
        self.assertEqual(len(layout_dict["edits"]), 2)
        # Verify that each edit widget has the pre-filled text matching the template.
        for edit, key in zip(layout_dict["edits"], object_template.keys()):
            self.assertIsInstance(edit, urwid.Edit)
            self.assertIn(str(object_template[key]), edit.get_edit_text())

    def test_create_delete_confirmation_popup_layout(self):
        dummy_widget = MagicMock()
        self.base_view.loop.widget = dummy_widget
        popup, buttons = self.base_view.create_delete_confirmation_popup_layout()
        self.assertIsNotNone(popup)
        self.assertIsInstance(buttons, list)
        self.assertEqual(len(buttons), 2)
        # Check that popup is an Overlay by ensuring it has attribute top_w
        self.assertTrue(hasattr(popup, "top_w"))

    def test_create_message_popup(self):
        dummy_widget = MagicMock()
        self.base_view.loop.widget = dummy_widget
        popup, buttons = self.base_view.create_message_popup("Test message")
        self.assertIsNotNone(popup)
        self.assertIsInstance(buttons, list)
        self.assertEqual(len(buttons), 1)
        self.assertTrue(hasattr(popup, "top_w"))
