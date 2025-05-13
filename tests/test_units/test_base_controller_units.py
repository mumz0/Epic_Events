import sys
import unittest
from unittest.mock import MagicMock, patch, ANY

import urwid

from src.controllers.base_controller import BaseController
from src.services.auth_service import AuthService
from src.models.contract import Contract
from src.models.event import Event


class DummyObj:
    def __init__(self, id, email_address=None):
        self.id = id
        self.email_address = email_address

    def get_identifier(self):
        return f"ID{self.id}"


class TestBaseController(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.loop = MagicMock()
        self.base_view.loop = self.loop
        self.current_user = MagicMock()
        self.history = []
        self.ctrl = BaseController(self.session, self.base_view, self.current_user, self.history)

    @patch.object(AuthService, "revoke_token")
    def test_handle_exit_click_revokes_and_exits(self, mock_revoke):
        with patch('sys.exit') as mock_exit:
            with self.assertRaises(SystemExit):
                mock_exit.side_effect = SystemExit
                self.ctrl.handle_exit_click()
            mock_revoke.assert_called_once_with(self.session)

    @patch("urwid.connect_signal")
    def test_show_exit_confirmation(self, mock_connect):
        popup = MagicMock()
        btn_yes = MagicMock()
        btn_no = MagicMock()
        self.base_view.create_exit_confirmation_view.return_value = (popup, [btn_yes, btn_no])
        # call
        self.ctrl.handle_exit_confirmation()
        mock_connect.assert_any_call(btn_yes, "click", ANY)
        mock_connect.assert_any_call(btn_no, "click", ANY)
        self.assertIn(popup, self.history)
        self.assertEqual(self.loop.widget, popup)
        self.base_view.update_screen.assert_called_with(popup)


    def test_cancel_popup(self):
        w1, w2 = MagicMock(), MagicMock()
        self.history.extend([w1, w2])
        self.ctrl.handle_cancel_popup()
        # should remove last and update to previous
        self.base_view.update_screen.assert_called_once_with(w1)

    def test_remove_popup(self):
        w1, w2, w3 = MagicMock(), MagicMock(), MagicMock()
        self.history.extend([w1, w2, w3])
        self.ctrl.handle_remove_popup()
        # removes two and updates to remaining
        self.base_view.update_screen.assert_called_once_with(w1)

    def test_handle_button_pressed(self):
        executed = []
        def fn(): executed.append(True)
        self.ctrl.handle_button_pressed(fn)
        self.assertTrue(executed)

    def test_handle_back_keypress_exit(self):
        # when at root, should call show_exit_confirmation
        self.history.append("root")
        self.loop.widget = "root"
        with patch.object(self.ctrl, "show_exit_confirmation") as mock_show:
            self.ctrl.handle_back_keypress("esc")
            mock_show.assert_called_once()

    def test_handle_back_keypress_back(self):
        w1, w2 = MagicMock(), MagicMock()
        self.history.extend([w1, w2])
        self.loop.widget = w2
        self.ctrl.handle_back_keypress("esc")
        self.assertEqual(self.loop.widget, w1)
        self.base_view.update_screen.assert_called_with(w1)

    @patch("urwid.connect_signal")
    def test_menu(self, mock_connect):
        btn1, btn2 = MagicMock(), MagicMock()
        layout = MagicMock()
        self.base_view.create_menu_layout.return_value = ([btn1, btn2], layout)
        # call menu with Home in title to push history
        self.ctrl.menu("> Home", [("A", lambda: None), ("B", lambda: None)])
        mock_connect.assert_any_call(btn1.base_widget, "click", ANY)
        mock_connect.assert_any_call(btn2.base_widget, "click", ANY)
        self.assertIn(layout, self.history)
        self.base_view.update_screen.assert_called_with(layout)

    def test_select_item_in_lst(self):
        o1 = DummyObj("1"); o2 = DummyObj("2")
        # id match
        res = self.ctrl.select_item_in_lst([o1, o2], "2")
        self.assertIs(res, o2)
        # get_identifier match
        res2 = self.ctrl.select_item_in_lst([o1, o2], "ID1")
        self.assertIs(res2, o1)
        # no match
        self.assertIsNone(self.ctrl.select_item_in_lst([o1], "X"))

    def test_object_details_layout(self):
        # call underlying without token decorator
        frame = MagicMock(); buttons = MagicMock()
        self.base_view.create_object_details_frame.return_value = (frame, buttons)
        dummy_controller = MagicMock()
        BaseController.object_details_layout.__wrapped__(
            self.ctrl, "> Title", DummyObj("X"), dummy_controller, ["b1"]
        )
        dummy_controller.create_details_view_buttons_signal.assert_called_once_with(buttons, ANY)
        self.assertIn(frame, self.history)
        self.base_view.update_screen.assert_called_with(frame)

    @patch("urwid.connect_signal")
    def test_pre_filled_form_page(self, mock_connect):
        layout_dict = {"buttons": MagicMock(), "edits": [], "layout": "LAY"}
        self.base_view.create_pre_filled_form_page.return_value = layout_dict
        self.ctrl.pre_filled_form_page("T", {}, MagicMock(), MagicMock())
        mock_connect.assert_called_once()
        self.base_view.update_screen.assert_called_once_with("LAY")

    def test_handle_save_button(self):
        # prepare history and edits
        e1 = MagicMock(caption="A: "); e1.get_edit_text.return_value = "v1"
        e2 = MagicMock(caption="B: "); e2.get_edit_text.return_value = "v2"
        self.history.extend(["first", "second", "third"])
        svc = MagicMock()
        obj = MagicMock()
        self.ctrl.handle_save_button([e1, e2], obj, svc)
        svc.prepare_data_and_update.assert_called_once_with({"A": "v1", "B": "v2"}, obj, self.session)
        # pops twice, then update screen with first
        self.base_view.update_screen.assert_called_with("first")

    @patch("urwid.connect_signal")
    def test_show_delete_confirmation(self, mock_connect):
        popup = "POP"; btns = [MagicMock(), MagicMock()]
        self.base_view.create_delete_confirmation_popup_layout.return_value = (popup, btns)
        self.ctrl.show_delete_confirmation(DummyObj("X"), MagicMock())
        mock_connect.assert_any_call(btns[0], "click", ANY)
        mock_connect.assert_any_call(btns[1], "click", ANY)
        self.base_view.update_screen.assert_called_with(popup)

    def test_handle_confirmation_delete(self):
        svc = MagicMock()
        obj_id = "OID"
        with patch.object(self.ctrl, "remove_popup") as mock_rm:
            self.ctrl.handle_confirmation_delete(obj_id, svc)
            svc.delete.assert_called_once_with(obj_id, self.session)
            mock_rm.assert_called_once()

    def test_get_button_data_for_items(self):
        c = Contract(id="C1")
        e = Event(id="E1")
        u = DummyObj("U", email_address="u@mail")
        res = self.ctrl.get_button_data_for_items([c, e, u])
        self.assertEqual(res, ["C1", "E1", "u@mail"])

    @patch("urwid.connect_signal")
    def test_connect_button_signals_list(self, mock_connect):
        # create buttons with get_label
        b1 = MagicMock(); b1.get_label.return_value = "L1"
        b2 = MagicMock(); b2.get_label.return_value = "L2"
        actions = [("L1", lambda: 1), ("L2", lambda x: x)]
        self.ctrl.connect_button_signals([b1, b2], actions)
        # should connect both
        self.assertEqual(mock_connect.call_count, 2)

    @patch("urwid.connect_signal")
    def test_connect_button_signals_dict(self, mock_connect):
        b1 = MagicMock(); b1.get_label.return_value = "X"
        buttons = {"other_buttons": [b1]}
        action = [("X", lambda: None)]
        self.ctrl.connect_button_signals(buttons, action)
        mock_connect.assert_called_once()
        # wrong type raises
        with self.assertRaises(TypeError):
            self.ctrl.connect_button_signals(123, [])
