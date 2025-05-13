import unittest
from unittest.mock import MagicMock, patch, ANY
from datetime import datetime

from src.controllers.event_controller import EventController
from src.services.event_service import EventService
from src.services.contract_service import ContractService
from src.services.base_service import BaseService
from src.views.paginated_view import PaginatedView


class TestEventController(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.base_view.loop = MagicMock()
        self.history = []
        self.current_user = MagicMock()
        role = MagicMock()
        role.name = "admin"
        role.permissions = []
        self.current_user.role = role
        self.current_user.email_address = "admin@mail.com"
        self.ctrl = EventController(self.session, self.base_view, self.current_user, self.history)

    @patch.object(EventService, "list_to_dict")
    @patch("src.controllers.event_controller.PaginatedView")
    @patch.object(EventController, "define_data_to_display")
    @patch.object(EventController, "define_page_buttons_signal_needded")
    def test_paginated_events_displayed(
        self, mock_define_signals, mock_define_data, mock_paginated_view_cls, mock_list_to_dict
    ):
        # Remplacement des chaînes par des objets simulés
        mock_define_data.return_value = [
            MagicMock(email_address="test1@mail.com"),
            MagicMock(email_address="test2@mail.com"),
        ]
        mock_list_to_dict.return_value = {"event1": {}, "event2": {}}
        paginated_view_instance = mock_paginated_view_cls.return_value
        paginated_view_instance.display_page.return_value = ("layout", {"buttons": []})

        self.ctrl.paginated_events_displayed("Title", "all")

        mock_define_data.assert_called_once_with("all", None)
        mock_list_to_dict.assert_called_once_with(mock_define_data.return_value)
        mock_paginated_view_cls.assert_called_once_with({"event1": {}, "event2": {}}, "Title")
        mock_define_signals.assert_called_once()
        self.base_view.update_screen.assert_called_once_with("layout")

    @patch.object(BaseService, "get_all")
    @patch.object(EventService, "filter_by_email_adress")
    @patch.object(EventService, "filter_by_support_email_adress")
    @patch.object(EventService, "filter_by_support_user_on_event")
    def test_define_data_to_display(
        self, mock_no_support, mock_support_email, mock_client_email, mock_get_all
    ):
        self.ctrl.define_data_to_display("all")
        mock_get_all.assert_called_once_with(self.session)

        self.ctrl.define_data_to_display("client", "client@mail.com")
        mock_client_email.assert_called_once_with("client@mail.com", self.session)

        self.ctrl.define_data_to_display("current_user")
        mock_support_email.assert_called_once_with(self.current_user.email_address, self.session)

        self.ctrl.define_data_to_display("no support")
        mock_no_support.assert_called_once_with(self.session, False)

        self.assertIsNone(self.ctrl.define_data_to_display("unknown"))

    @patch.object(EventController, "create_all_events_paginated_buttons_signal")
    @patch.object(EventController, "create_client_events_paginated_buttons_signal")
    @patch.object(EventController, "create_current_user_paginated_buttons_signal")
    def test_define_page_buttons_signal_needded(
        self, mock_current_user, mock_client, mock_all
    ):
        paginated_view = MagicMock()
        buttons = MagicMock()
        event_objects = ["event1"]

        self.ctrl.define_page_buttons_signal_needded(paginated_view, buttons, event_objects, "all", None)
        mock_all.assert_called_once_with(paginated_view, buttons, event_objects)

        self.ctrl.define_page_buttons_signal_needded(paginated_view, buttons, event_objects, "client", "client@mail.com")
        mock_client.assert_called_once_with(paginated_view, buttons, event_objects, "client@mail.com")

        self.ctrl.define_page_buttons_signal_needded(paginated_view, buttons, event_objects, "current_user", None)
        mock_current_user.assert_called_once_with(paginated_view, buttons, event_objects)

    @patch.object(EventService, "generate_uid")
    @patch.object(EventService, "string_date_to_datetime")
    @patch.object(ContractService, "check_if_contract_is_signed")
    @patch.object(BaseService, "create")
    def test_handle_client_creation_button_event_success(
        self, mock_create, mock_check_signed, mock_date_to_datetime, mock_generate_uid
    ):
        # Arrange mocks
        mock_generate_uid.return_value = "EVENT123"
        mock_date_to_datetime.side_effect = [
            datetime(2023, 1, 1),
            datetime(2023, 1, 2)
        ]
        mock_check_signed.return_value = True
        mock_create.return_value = True

        # Provide exactly the fields the controller will pop in order
        layout_dict = {
            "edits": [
                MagicMock(get_edit_text=MagicMock(return_value="Event Name")),      # idx 0
                MagicMock(get_edit_text=MagicMock(return_value="2023/01/01")),      # idx 1
                MagicMock(get_edit_text=MagicMock(return_value="2023/01/02")),      # idx 2
                MagicMock(get_edit_text=MagicMock(return_value="Location")),        # idx 3
                MagicMock(get_edit_text=MagicMock(return_value="100")),             # idx 4
                MagicMock(get_edit_text=MagicMock(return_value="Notes")),           # idx 5
                MagicMock(get_edit_text=MagicMock(return_value="CONTRACT123")),     # idx 6
                MagicMock(get_edit_text=MagicMock(return_value="support@mail.com")),# idx 7
            ]
        }

        # history must have at least two entries so pop() leaves one for update_screen
        self.ctrl.history = ["prev_layout", "initial_layout"]

        # Act
        self.ctrl.handle_client_creation_button_event(
            layout_dict,
            "client@mail.com"
        )

        # Assert
        mock_generate_uid.assert_called_once_with(self.session)
        mock_date_to_datetime.assert_any_call("2023/01/01")
        mock_date_to_datetime.assert_any_call("2023/01/02")
        mock_check_signed.assert_called_once_with(self.session, "CONTRACT123")
        mock_create.assert_called_once()
        # After pop(), history[0] == "prev_layout"
        self.base_view.update_screen.assert_called_once_with("prev_layout")

    @patch.object(EventController, "connect_button_signals")
    def test_create_details_view_buttons_signal(self, mock_connect_signals):
        buttons = [MagicMock()]
        event_object = MagicMock()
        event_object.to_dict.return_value = {"id": "EVENT123", "name": "Event Name"}

        self.ctrl.create_details_view_buttons_signal(buttons, event_object)

        mock_connect_signals.assert_called_once()