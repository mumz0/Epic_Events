import unittest
from unittest.mock import MagicMock, patch

import urwid

from src.controllers.user_controller import UserController
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.views.paginated_view import PaginatedView


class TestUserController(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_base_view = MagicMock()
        self.mock_current_user = MagicMock()
        self.mock_current_user.role.permissions = []
        self.mock_history = []
        self.controller = UserController(self.mock_session, self.mock_base_view, self.mock_current_user, self.mock_history)

    @patch.object(UserRepository, "get_all")
    @patch.object(UserService, "list_to_dict", return_value={"userA": {}})
    @patch("src.controllers.user_controller.PaginatedView")
    def test_all_users(self, mock_paginated, mock_list_dict, mock_repo_get_all):
        user_mock = MagicMock()
        user_mock.email_address = "userA@example.com"
        mock_repo_get_all.return_value = [user_mock]

        # Return a dict with "buttons_items"
        mock_paginated.return_value.display_page.return_value = (MagicMock(), {"buttons_items": []})
        self.controller.all_users()

        mock_repo_get_all.assert_called_once_with(self.mock_session)
        mock_list_dict.assert_called_once_with([user_mock])
        self.assertTrue(self.mock_base_view.update_screen.called)
        self.assertEqual(len(self.mock_history), 1)

    @patch.object(AuthService, "signup_process", return_value=True)
    def test_handle_user_creation_button_event_success(self, mock_signup):
        layout_dict = {
            "edits": [
                MagicMock(get_edit_text=lambda: "new_user@example.com"),
                MagicMock(get_edit_text=lambda: "password"),
                MagicMock(get_edit_text=lambda: "management"),
            ]
        }
        self.mock_history.extend(["layout1", "previous_layout"])

        self.controller.handle_user_creation_button_event(layout_dict)

        mock_signup.assert_called_once()
        self.assertTrue(self.mock_base_view.update_screen.called)
        self.assertEqual(self.mock_history, ["layout1"])

    @patch.object(AuthService, "signup_process", return_value=False)
    @patch("urwid.connect_signal")
    def test_handle_user_creation_button_event_already_exists(self, mock_connect_signal, mock_signup):
        self.mock_base_view.create_message_popup.return_value = (MagicMock(), [MagicMock()])

        layout_dict = {
            "edits": [
                MagicMock(get_edit_text=lambda: "existing_user@example.com"),
                MagicMock(get_edit_text=lambda: "password"),
                MagicMock(get_edit_text=lambda: "sales"),
            ]
        }

        self.controller.handle_user_creation_button_event(layout_dict)
        mock_signup.assert_called_once()
        self.mock_base_view.create_message_popup.assert_called_once_with("User already exists. Please try again.")
        self.assertTrue(mock_connect_signal.called)
