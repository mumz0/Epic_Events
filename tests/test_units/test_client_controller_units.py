import sys
import unittest
from unittest.mock import MagicMock, patch, ANY

import urwid
import sentry_sdk

from src.controllers.client_controller import ClientController
from src.models.client import Client
from src.repositories.client_repository import ClientRepository
from src.services.base_service import BaseService
from src.services.client_service import ClientService
from src.services.user_service import UserService
from src.views.paginated_view import PaginatedView


class DummyPerm:
    def __init__(self, action):
        self.action = action


class DummyClient:
    def __init__(self, id, sales_contact_id=None, email_address="e@mail"):
        self.id = id
        self.sales_contact_id = sales_contact_id or "sales@mail"
        self.email_address = email_address

    def to_dict(self):
        return {"id": self.id, "email_address": self.email_address}


class TestClientController(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.base_view.loop = MagicMock()
        self.history = ["first"]
        # current_user with role and permissions
        self.current_user = MagicMock()
        role = MagicMock()
        role.name = "user"
        role.permissions = []
        self.current_user.role = role
        self.current_user.email_address = "sales@mail"
        self.ctrl = ClientController(self.session, self.base_view, self.current_user, self.history)

    @patch("src.controllers.client_controller.PaginatedView")
    @patch("src.controllers.client_controller.ClientService")
    @patch("src.controllers.client_controller.BaseService")
    @patch.object(ClientController, "create_paginated_buttons_signal")
    def test_all_clients_renders_paginated(
        self, mock_setup_signals, mock_base_svc_cls, mock_client_svc_cls, mock_pv_cls
    ):
        # arrange
        clients = [DummyClient("C1"), DummyClient("C2")]
        svc_inst = mock_base_svc_cls.return_value
        svc_inst.get_all.return_value = clients
        dict_out = {"C1": {}, "C2": {}}
        mock_client_svc_cls.return_value.list_to_dict.return_value = dict_out

        pv_inst = mock_pv_cls.return_value
        layout = MagicMock()
        buttons = {"buttons_items": []}
        pv_inst.display_page.return_value = (layout, buttons)

        # act
        self.ctrl.all_clients()

        # assert BaseService.get_all and ClientService.list_to_dict called
        mock_base_svc_cls.assert_called_once_with(self.current_user, ANY)
        svc_inst.get_all.assert_called_once_with(self.session)
        mock_client_svc_cls.return_value.list_to_dict.assert_called_once_with(clients)
        # PaginatedView created with dict and title
        mock_pv_cls.assert_called_once_with(dict_out, "> Home > Clients")
        pv_inst.display_page.assert_called_once_with(0, ANY)
        mock_setup_signals.assert_called_once_with(pv_inst, buttons, clients)
        # history and screen updated
        self.assertIn(layout, self.history)
        self.base_view.update_screen.assert_called_with(layout)

    @patch("src.controllers.client_controller.urwid.connect_signal")
    @patch.object(ClientController, "select_item_in_lst")
    @patch.object(ClientController, "connect_button_signals")
    def test_create_paginated_buttons_signal_sets_up_buttons(
        self, mock_connect_nav, mock_select, mock_connect_signal
    ):
        # arrange two client items and dummy buttons
        c1 = DummyClient("A", sales_contact_id="sales@mail")
        c2 = DummyClient("B", sales_contact_id="other@mail")
        buttons = {"buttons_items": [MagicMock(label="A"), MagicMock(label="B")], "buttons": []}
        # select_item_in_lst returns matching client object
        mock_select.side_effect = [c1, c2]
        # grant permissions: update and read
        self.current_user.role.permissions = [DummyPerm("client_update"), DummyPerm("client_read")]

        # act
        self.ctrl.create_paginated_buttons_signal(MagicMock(), buttons, [c1, c2])

        # item buttons get connect_signal
        self.assertEqual(mock_connect_signal.call_count, 2)
        # navigation actions passed to connect_button_signals
        nav_calls = mock_connect_nav.call_args[0][1]
        labels = [lbl for lbl, _ in nav_calls]
        self.assertIn("Previous", labels)
        self.assertIn("Next", labels)
        # no Create for user role
        self.assertNotIn("Create", labels)

    @patch("src.controllers.client_controller.urwid.connect_signal")
    def test_client_creation_view(self, mock_connect_signal):
        # arrange form layout
        btn = MagicMock()
        layout_dict = {"buttons": [btn], "edits": [], "layout": "LAY"}
        self.base_view.create_form_layout.return_value = layout_dict

        # act
        self.ctrl.client_creation()

        # assert signal and update_screen
        mock_connect_signal.assert_called_once_with(btn, "click", ANY)
        self.base_view.update_screen.assert_called_once_with("LAY")

    @patch("src.controllers.client_controller.BaseService.create")
    @patch("src.controllers.client_controller.UserService")
    def test_handle_client_creation_success(self, mock_usvc_cls, mock_base_create):
        # arrange a layout with four edits
        edits = []
        texts = ["N", "e@mail", "123", "Co"]
        for txt in texts:
            e = MagicMock()
            e.get_edit_text.return_value = txt
            edits.append(e)
        layout_dict = {"edits": edits}
        self.ctrl.history = ["orig", "step"]
        # stub get_by_email returns truthy
        mock_usvc_cls.return_value.get_by_email.return_value = True

        # act
        self.ctrl.handle_client_creation_button_event(layout_dict)

        # assert BaseService.create called with correct data and session
        expected = {
            "name": "N",
            "email_address": "e@mail",
            "phone": "123",
            "compagny": "Co",
            "sales_contact_id": "sales@mail",
        }
        mock_base_create.assert_called_once_with(expected, self.session)
        # history popped and update_screen called
        self.assertEqual(self.ctrl.history, ["orig"])
        self.base_view.update_screen.assert_called_once_with("orig")

    @patch("src.controllers.client_controller.UserService")
    def test_handle_client_creation_no_user(self, mock_usvc_cls):
        # arrange edits (not used)
        layout_dict = {"edits": []}
        mock_usvc_cls.return_value.get_by_email.return_value = None

        # act
        self.ctrl.handle_client_creation_button_event(layout_dict)

        # assert display_message
        self.base_view.display_message.assert_called_once_with(
            "Sales contact does not exist. Please try again."
        )

    @patch("src.controllers.client_controller.BaseService.remove_attributes_from_object")
    @patch("src.controllers.client_controller.sentry_sdk.capture_message")
    @patch.object(ClientController, "connect_button_signals")
    def test_create_details_view_buttons_signal(
        self, mock_connect_nav, mock_capture_msg, mock_remove_attrs
    ):
        # arrange client object and initial buttons dict
        client = DummyClient("X", sales_contact_id="s@mail", email_address="c@mail")
        buttons = MagicMock()
        # to_dict returns base dict
        # act
        self.ctrl.create_details_view_buttons_signal(buttons, client)

        # remove_attributes called with template and fields
        mock_remove_attrs.assert_called_once_with(client.to_dict(), ["Creation date", "Last update"])
        mock_capture_msg.assert_called_once_with("client_email: c@mail")
        # connect_button_signals called with same buttons and 4 actions
        args_buttons, actions = mock_connect_nav.call_args[0]
        self.assertIs(args_buttons, buttons)
        self.assertEqual(len(actions), 4)
        labels = [lbl for lbl, _ in actions]
        self.assertCountEqual(labels, ["Modify", "Delete", "Contracts", "Events"])
