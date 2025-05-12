import unittest
from unittest.mock import MagicMock, patch

from src.controllers.event_controller import EventController
from src.repositories.event_repository import EventRepository
from src.services.base_service import BaseService
from src.services.contract_service import ContractService
from src.services.event_service import EventService
from src.views.paginated_view import PaginatedView


class TestEventController(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_base_view = MagicMock()
        self.mock_current_user = MagicMock()
        self.mock_history = []
        self.controller = EventController(self.mock_session, self.mock_base_view, self.mock_current_user, self.mock_history)

    @patch.object(BaseService, "get_all")
    @patch.object(EventService, "list_to_dict", return_value={})
    @patch("src.controllers.event_controller.PaginatedView")
    def test_paginated_events_displayed(self, mock_paginated, mock_list_to_dict, mock_get_all):
        # Return a dictionary rather than MagicMock to avoid TypeError
        mock_paginated.return_value.display_page.return_value = (MagicMock(), {"buttons_items": []})

        self.controller.paginated_events_displayed("> Home > Events", "all")

        mock_get_all.assert_called_once()
        mock_list_to_dict.assert_called_once()
        self.assertTrue(self.mock_base_view.update_screen.called)
        self.assertEqual(len(self.mock_history), 1)

    def test_define_data_to_display_all(self):
        with patch.object(BaseService, "get_all", return_value=["eventA"]):
            self.mock_current_user.email_address = "test@user.com"
            result = self.controller.define_data_to_display("all")
            self.assertEqual(result, ["eventA"])

    @patch.object(EventService, "filter_by_email_adress", return_value=["evtClient"])
    def test_define_data_to_display_client(self, mock_filter):
        result = self.controller.define_data_to_display("client", "client@domain.com")
        mock_filter.assert_called_once_with("client@domain.com", self.mock_session)
        self.assertEqual(result, ["evtClient"])

    @patch.object(EventService, "filter_by_support_email_adress", return_value=["evtSupport"])
    def test_define_data_to_display_current_user(self, mock_filter):
        self.mock_current_user.email_address = "support@domain.com"
        result = self.controller.define_data_to_display("current_user")
        mock_filter.assert_called_once_with("support@domain.com", self.mock_session)
        self.assertEqual(result, ["evtSupport"])

    @patch.object(EventService, "filter_by_support_user_on_event", return_value=["evtNoSupport"])
    def test_define_data_to_display_no_support(self, mock_filter):
        result = self.controller.define_data_to_display("no support")
        mock_filter.assert_called_once_with(self.mock_session, False)
        self.assertEqual(result, ["evtNoSupport"])

    @patch("src.controllers.event_controller.PaginatedView")
    def test_define_page_buttons_signal_needded_all(self, mock_paginated):
        mock_buttons = {"buttons_items": []}
        self.controller.create_all_events_paginated_buttons_signal = MagicMock()
        self.controller.define_page_buttons_signal_needded(mock_paginated, mock_buttons, [], "all", None)
        self.controller.create_all_events_paginated_buttons_signal.assert_called_once()

    @patch.object(EventService, "string_date_to_datetime", return_value="2023-10-01")
    @patch.object(EventService, "generate_uid", return_value="EVENT123")
    @patch.object(ContractService, "check_if_contract_is_signed", return_value=False)
    def test_handle_client_creation_button_event_not_signed(self, mock_check_signed, mock_uid, mock_date_to_dt):
        from urwid import Button

        # Return mock Buttons with a valid "click" signal:
        mock_button_1 = MagicMock(spec=Button)
        mock_button_2 = MagicMock(spec=Button)
        self.mock_base_view.create_message_popup.side_effect = [
            (MagicMock(), [mock_button_1]),
            (MagicMock(), mock_button_2),
        ]

        layout_dict = {
            "edits": [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()],
        }
        self.controller.handle_client_creation_button_event(layout_dict, "client@domain.com")
        mock_check_signed.assert_called_once()
