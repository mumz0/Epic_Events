import os
import time
import builtins
import click
import urwid
import unittest
from unittest.mock import patch, MagicMock

from src.views.base_view import BaseView

class DummyObj:
    def __init__(self, **kwargs):
        self._data = kwargs
    def to_dict(self):
        return self._data

class TestBaseView(unittest.TestCase):
    def setUp(self):
        self.view = BaseView()
        # Prepare a fake loop for update_screen and popups
        self.view.loop = MagicMock()
        self.view.loop.screen = MagicMock()

    @patch('builtins.input', side_effect=['e@mail', 'pwd'])
    def test_admin_signup_view(self, mock_input):
        email, pwd = self.view.admin_signup_view()
        self.assertEqual(email, 'e@mail')
        self.assertEqual(pwd, 'pwd')

    @patch('src.views.base_view.urwid.MainLoop')
    def test_init_main_loop(self, mock_ml):
        dummy_widget = MagicMock()
        handler = lambda x: None
        self.view.init_main_loop(dummy_widget, handler)
        mock_ml.assert_called_once_with(dummy_widget, unhandled_input=handler)
        self.assertIsNotNone(self.view.loop)

    def test_update_screen(self):
        new_layout = MagicMock()
        self.view.update_screen(new_layout)
        self.assertEqual(self.view.loop.widget, new_layout)
        self.view.loop.screen.clear.assert_called_once()
        self.view.loop.draw_screen.assert_called_once()

    def test_create_button(self):
        btn = self.view.create_button('OK')
        self.assertIsInstance(btn, urwid.Button)
        self.assertEqual(btn.get_label(), 'OK')

    @patch('os.system')
    def test_clear_screen(self, mock_system):
        # simulate nt vs posix
        with patch('os.name', 'nt'):
            self.view.clear_screen()
            mock_system.assert_called_with("cls")
        with patch('os.name', 'posix'):
            self.view.clear_screen()
            mock_system.assert_called_with("clear")

    def test_create_header_body(self):
        header = self.view.create_header_body("Title")
        # first widget is Text with ascii art, second is LineBox
        self.assertIsInstance(header[0], urwid.Text)
        self.assertIsInstance(header[1], urwid.LineBox)
        title_text = header[1].original_widget.original_widget.text
        self.assertIn("Title", title_text)

    def test_create_buttons_and_menu_body(self):
        labels = ['A', 'B']
        body, buttons = self.view.create_menu_body([], labels)
        self.assertEqual(len(body), 2)
        self.assertEqual(len(buttons), 2)
        # buttons are AttrMap wrapping Button
        for bm in buttons:
            self.assertIsInstance(bm, urwid.AttrMap)

    def test_create_frame(self):
        dummy = [urwid.Text("X")]
        frame = self.view.create_frame(dummy)
        self.assertIsInstance(frame, urwid.Frame)

    @patch.object(BaseView, 'clear_screen')
    def test_create_menu_layout(self, mock_clear):
        buttons, layout = self.view.create_menu_layout("T", ['X'])
        self.assertEqual(len(buttons), 1)
        self.assertIsInstance(layout, urwid.Frame)
        mock_clear.assert_called_once()

    def test_create_form_layout(self):
        result = self.view.create_form_layout("Form", ['OK'], ['f1','f2'])
        self.assertIn('edits', result)
        self.assertIn('buttons', result)
        self.assertIn('layout', result)
        self.assertEqual(len(result['edits']), 2)
        self.assertEqual(len(result['buttons']), 1)

    @patch('src.views.base_view.click.echo')
    @patch('src.views.base_view.urwid.MainLoop')
    @patch('time.sleep', return_value=None)
    def test_display_message(self, mock_sleep, mock_ml, mock_echo):
        # configure fake loop.screen.start/stop
        inst = mock_ml.return_value
        inst.screen = MagicMock()
        self.view.display_message("MSG")
        mock_echo.assert_called_once_with("MSG")
        inst.screen.start.assert_called_once()
        inst.screen.stop.assert_called_once()

    def test_create_card(self):
        d = DummyObj(a=1, b=2, date_built= __import__('datetime').datetime(2021,1,1))
        card = self.view.create_card(d)
        self.assertIsInstance(card, urwid.Filler)
        # ensure content contains key labels
        linebox = card.body.contents[0][0]
        text = linebox.original_widget.original_widget.text
        self.assertIn("a: 1", text)
        self.assertIn("date_built: 2021/01/01", text)

    @patch.object(BaseView, 'create_card')
    def test_create_object_details_frame(self, mock_card):
        # no selected_object
        frame, buttons = self.view.create_object_details_frame("T", None, {"buttons_label":["X"]})
        self.assertIsInstance(frame, urwid.Frame)
        self.assertEqual(len(buttons), 1)
        # with object
        mock_card.return_value = MagicMock()
        frame2, btns2 = self.view.create_object_details_frame("T", DummyObj(), {"buttons_label":["Y","Z"]})
        self.assertEqual(len(btns2), 2)

    def test_create_pre_filled_form_page(self):
        data = {"k1":"v1","k2":"v2"}
        out = self.view.create_pre_filled_form_page(data, "Title")
        self.assertIn('edits', out)
        self.assertIn('buttons', out)
        self.assertIn('layout', out)
        self.assertEqual(len(out['edits']), 2)

    def test_create_delete_confirmation_popup_layout(self):
        popup, btns = self.view.create_delete_confirmation_popup_layout()
        self.assertIsInstance(popup, urwid.Overlay)
        self.assertEqual(len(btns), 2)

    def test_create_message_popup(self):
        popup, btns = self.view.create_message_popup("Hi")
        self.assertIsInstance(popup, urwid.Overlay)
        self.assertEqual(len(btns), 1)

    def test_create_expired_token_popup(self):
        popup, btn = self.view.create_expired_token_popup()
        self.assertIsInstance(popup, urwid.Filler)
        self.assertIsInstance(btn, urwid.Button)

    def test_create_exit_confirmation_view(self):
        popup, btns = self.view.create_exit_confirmation_view()
        self.assertIsInstance(popup, urwid.Overlay)
        labels = [b.get_label() for b in btns]
        self.assertListEqual(labels, ["Yes","No"])

if __name__ == '__main__':
    unittest.main()