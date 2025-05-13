import unittest
from unittest.mock import patch, MagicMock, ANY
import urwid

from src.controllers.user_controller import UserController
from src.services.auth_service import AuthService


class DummyPerm:
    def __init__(self, action):
        self.action = action


class DummyUser:
    def __init__(self):
        self.id = 42
        role = MagicMock()
        role.permissions = []
        self.role = role


class TestUserController(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.base_view.loop = MagicMock()
        self.history = []
        self.current_user = DummyUser()
        self.ctrl = UserController(self.session, self.base_view, self.current_user, self.history)

    @patch.object(UserController, "create_paginated_buttons_signal")
    @patch("src.controllers.user_controller.sentry_sdk.capture_message")
    @patch("src.controllers.user_controller.PaginatedView")
    @patch("src.controllers.user_controller.UserService")
    @patch("src.controllers.user_controller.UserRepository")
    def test_all_users(
        self, mock_repo_cls, mock_usvc_cls, mock_pv_cls, mock_capture, mock_create_sig
    ):
        # arrange repository and service
        users = [MagicMock(), MagicMock()]
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = users
        mock_repo_cls.return_value = mock_repo

        dict_out = {"u1": {}, "u2": {}}
        mock_usvc = MagicMock()
        mock_usvc.list_to_dict.return_value = dict_out
        mock_usvc_cls.return_value = mock_usvc

        layout = "LAYOUT"
        buttons = {"buttons_items": []}
        pv_inst = mock_pv_cls.return_value
        pv_inst.display_page.return_value = (layout, buttons)

        # give create permission
        self.current_user.role.permissions = [DummyPerm("user_create")]

        # act: bypass decorator
        UserController.all_users.__wrapped__(self.ctrl)

        # assert
        mock_capture.assert_called_with(f"all users: {self.current_user.id}")
        mock_repo.get_all.assert_called_once_with(self.session)
        mock_usvc.list_to_dict.assert_called_once_with(users)
        mock_pv_cls.assert_called_once_with(dict_out, "> Home > Users")
        self.assertEqual(pv_inst.loop, self.base_view.loop)
        pv_inst.display_page.assert_called_once_with(0, ANY)
        mock_create_sig.assert_called_once_with(pv_inst, buttons, users)
        self.assertIn(layout, self.history)
        self.base_view.update_screen.assert_called_once_with(layout)

    @patch("urwid.connect_signal")
    @patch.object(UserController, "connect_button_signals")
    def test_create_paginated_buttons_signal(self, mock_conn_nav, mock_conn_sig):
        btn = MagicMock()
        btn.get_label.return_value = "U1"
        user_obj = MagicMock(email_address="u@e.com", id="U1")
        self.current_user.role.permissions = [DummyPerm("user_update"), DummyPerm("user_delete")]
        pag = MagicMock()
        buttons = {"buttons_items": [btn]}

        self.ctrl.create_paginated_buttons_signal(pag, buttons, [user_obj])

        # detail button connect
        mock_conn_sig.assert_called_once()
        # navigation actions include Create
        actions = mock_conn_nav.call_args[0][1]
        labels = [lbl for lbl, _ in actions]
        self.assertIn("Previous", labels)
        self.assertIn("Next", labels)
        self.assertIn("Create", labels)

    @patch.object(UserController, "connect_button_signals")
    @patch("src.controllers.user_controller.BaseService.remove_attributes_from_object")
    def test_create_details_view_buttons_signal(self, mock_remove, mock_connect_sig):
        buttons = [MagicMock(), MagicMock()]
        user_obj = MagicMock(email_address="u@e.com")
        user_obj.to_dict.return_value = {"ID": 1, "Email": "u@e.com"}
        mock_remove.return_value = {"Email": "u@e.com"}

        self.ctrl.create_details_view_buttons_signal(buttons, user_obj)

        mock_remove.assert_called_once_with(user_obj.to_dict(), ["ID"])
        mock_connect_sig.assert_called_once_with(buttons, ANY)

    @patch("urwid.connect_signal")
    def test_user_creation(self, mock_connect):
        btn = MagicMock()
        layout_dict = {"buttons": [btn], "edits": [], "layout": "LAY"}
        self.base_view.create_form_layout.return_value = layout_dict

        self.ctrl.user_creation()

        mock_connect.assert_called_once_with(btn, "click", ANY)
        self.base_view.update_screen.assert_called_once_with("LAY")

    @patch.object(AuthService, "signup_process", return_value=True)
    def test_handle_user_creation_button_event_success(self, mock_signup):
        self.ctrl.history = ["prev", "init"]
        layout_dict = {"edits": [MagicMock(), MagicMock(), MagicMock()]}
        self.ctrl.handle_user_creation_button_event(layout_dict)
        # history popped
        self.assertEqual(self.ctrl.history, ["prev"])
        self.base_view.update_screen.assert_called_once_with("prev")

    @patch.object(AuthService, "signup_process", return_value=False)
    @patch("urwid.connect_signal")
    def test_handle_user_creation_button_event_failure(self, mock_connect, mock_signup):
        popup = MagicMock()
        btn = MagicMock()
        self.base_view.create_message_popup.return_value = (popup, [btn])
        layout = {"edits": [MagicMock(), MagicMock(), MagicMock()]}

        self.ctrl.handle_user_creation_button_event(layout)

        mock_connect.assert_called_once_with(btn, "click", ANY)
        self.base_view.update_screen.assert_called_once_with(popup)


if __name__ == "__main__":
    unittest.main()