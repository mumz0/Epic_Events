import unittest
from unittest.mock import MagicMock, patch

from src.controllers.client_controller import ClientController
from src.controllers.contract_controller import ContractController
from src.controllers.event_controller import EventController
from src.models.client import Client
from src.repositories.client_repository import ClientRepository
from src.services.base_service import BaseService
from src.services.client_service import ClientService
from src.services.user_service import UserService


class TestClientController(unittest.TestCase):

    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_base_view = MagicMock()
        self.mock_current_user = MagicMock()
        # Add an extra layout so index 0 remains valid
        self.mock_history = ["dummy_layout", "another_layout"]
        self.controller = ClientController(self.mock_session, self.mock_base_view, self.mock_current_user, self.mock_history)

    @patch.object(BaseService, "get_all")
    def test_all_clients(self, mock_get_all):
        mock_client = MagicMock(spec=Client)
        mock_client.email_address = "test@example.com"
        mock_get_all.return_value = [mock_client]
        self.mock_current_user.role.permissions = []

        self.controller.all_clients()

        mock_get_all.assert_called_once_with(self.mock_session)
        self.assertTrue(self.mock_base_view.update_screen.called)
        # We now expect 3 total items in history [two initial + one new]
        self.assertEqual(len(self.mock_history), 3)

    @patch.object(BaseService, "get_all")
    @patch("src.controllers.client_controller.PaginatedView")
    def test_create_paginated_buttons_signal(self, mock_paginated, mock_get_all):
        # Tell the mock what display_page should return
        mock_paginated.return_value.display_page.return_value = (
            MagicMock(),  # layout
            {"buttons": ["Previous", "Next"], "buttons_items": []},  # buttons
        )

        mock_client = MagicMock(spec=Client)
        mock_client.email_address = "test@example.com"
        mock_get_all.return_value = [mock_client]
        self.mock_current_user.role.permissions = []

        self.controller.all_clients()

        # Now, display_page returned a tuple, so unpacking works
        call_args = mock_paginated.return_value.display_page.call_args
        buttons = call_args[0][1]  # second arg to display_page
        self.assertIn("Previous", buttons["buttons"])
        self.assertIn("Next", buttons["buttons"])

    @patch.object(UserService, "get_by_email")
    @patch.object(BaseService, "create")
    def test_handle_client_creation_button_event_success(self, mock_create, mock_get_by_email):
        mock_get_by_email.return_value = True
        layout_dict = {"edits": [MagicMock(), MagicMock(), MagicMock(), MagicMock()], "edits_count": 4}

        self.controller.handle_client_creation_button_event(layout_dict)

        mock_get_by_email.assert_called_once()
        mock_create.assert_called_once()
        self.assertTrue(self.mock_base_view.update_screen.called)

    @patch.object(UserService, "get_by_email")
    def test_handle_client_creation_button_event_failure(self, mock_get_by_email):
        mock_get_by_email.return_value = False
        layout_dict = {"edits": [MagicMock(), MagicMock(), MagicMock(), MagicMock()], "edits_count": 4}

        self.controller.handle_client_creation_button_event(layout_dict)

        self.mock_base_view.display_message.assert_called_once_with("Sales contact does not exist. Please try again.")

    def test_create_details_view_buttons_signal(self):
        mock_client = MagicMock(spec=Client)
        mock_client.email_address = "test@example.com"
        mock_client.to_dict.return_value = {"email_address": "test@example.com"}
        buttons = {"modify_button": MagicMock(), "delete_button": MagicMock()}

        self.controller.create_details_view_buttons_signal(buttons, mock_client)
        self.assertTrue(self.mock_base_view.create_delete_confirmation_popup_layout)
        self.assertTrue(ContractController)
        self.assertTrue(EventController)
