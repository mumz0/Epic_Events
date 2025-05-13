import unittest
from unittest.mock import MagicMock, patch, ANY

import urwid
import sentry_sdk

from src.controllers.auth_controller import AuthController


class TestAuthController(unittest.TestCase):
    def setUp(self):
        # prepare controller with dummy dependencies
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.current_user = None
        self.history = []
        self.ctrl = AuthController(self.session, self.base_view, self.current_user, self.history)

    @patch("src.controllers.auth_controller.AuthService")
    @patch("src.controllers.auth_controller.BaseView")
    def test_create_admin_user_success(self, mock_base_view_cls, mock_auth_svc_cls):
        # simulate query returning a role object
        role_obj = MagicMock()
        role_obj.name = "ADMIN"
        query = MagicMock()
        query.filter_by.return_value = query
        query.first.return_value = role_obj
        self.session.query.return_value = query

        # stub BaseView.admin_signup_view
        mock_base_view_cls.return_value.admin_signup_view.return_value = ("e@x.com", "pwd")

        # call method
        self.ctrl.create_admin_user()

        # assertions
        mock_base_view_cls.assert_called_once()
        mock_auth_svc_cls.assert_called_once_with(None)
        mock_auth_svc_cls.return_value.signup_process.assert_called_once_with(
            "e@x.com", "pwd", "ADMIN", self.session
        )

    def test_create_admin_user_no_role(self):
        # simulate no admin role found
        query = MagicMock()
        query.filter_by.return_value = query
        query.first.return_value = None
        self.session.query.return_value = query

        with self.assertRaises(ValueError) as cm:
            self.ctrl.create_admin_user()
        self.assertEqual(str(cm.exception), "Admin role not found.")

    @patch("src.controllers.auth_controller.urwid.connect_signal")
    def test_signin_layout_and_signal(self, mock_connect_signal):
        # stub layout creation
        button = MagicMock()
        layout = MagicMock()
        self.base_view.create_form_layout.return_value = {
            "buttons": [button],
            "edits": [],
            "layout": layout
        }

        # call signin
        self.ctrl.signin()

        # verify form layout and screen update
        self.base_view.create_form_layout.assert_called_once_with(
            ">Authentication", ["Sign In"], ["Email", "Password"]
        )
        mock_connect_signal.assert_called_once_with(
            button, "click", ANY
        )
        self.base_view.update_screen.assert_called_once_with(layout)

    @patch("src.controllers.auth_controller.urwid.connect_signal")
    def test_show_expired_token_popup(self, mock_connect_signal):
        popup = MagicMock()
        button = MagicMock()
        # stub popup creation
        self.base_view.create_expired_token_popup.return_value = (popup, button)
        # prepare loop
        self.base_view.loop = MagicMock()

        # call
        self.ctrl.show_expired_token_popup()

        mock_connect_signal.assert_called_once_with(button, "click", ANY)
        # widget should be set and screen updated
        self.assertEqual(self.base_view.loop.widget, popup)
        self.base_view.update_screen.assert_called_once_with(popup)

    @patch("src.controllers.auth_controller.sentry_sdk.capture_message")
    @patch("src.controllers.auth_controller.AuthService")
    def test_handle_auth_form_button_event(self, mock_auth_svc_cls, mock_capture_message):
        # prepare edits and return values
        edit1 = MagicMock()
        edit2 = MagicMock()
        edit1.get_edit_text.return_value = "u@x.com"
        edit2.get_edit_text.return_value = "secret"
        layout = {"edits": [edit1, edit2]}
        # prepare AuthService to return a user
        user = MagicMock(id=42)
        mock_auth_svc_cls.return_value.signin_process.return_value = user
        # stub menu
        self.ctrl.menu = MagicMock()

        # call
        self.ctrl.handle_auth_form_button_event(layout)

        # AuthService called with current_user
        mock_auth_svc_cls.assert_called_once_with(self.current_user)
        mock_auth_svc_cls.return_value.signin_process.assert_called_once_with(
            "u@x.com", "secret", self.session
        )
        # sentry message
        mock_capture_message.assert_called_once_with("handle_auth_form_button_event: 42")
        # menu called with home and 5 options
        args, _ = self.ctrl.menu.call_args
        self.assertEqual(args[0], "> Home")
        self.assertIsInstance(args[1], list)
        self.assertEqual(len(args[1]), 5)
