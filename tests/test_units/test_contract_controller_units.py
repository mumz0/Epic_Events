import unittest
from unittest.mock import patch, MagicMock

from utils.decorators import require_valid_token
from src.controllers.contract_controller import ContractController
from src.services.contract_service import ContractService
from src.services.base_service import BaseService
from src.repositories.contract_repository import ContractRepository
from src.views.paginated_view import PaginatedView


class Dummy:
    def __init__(self):
        self.session = "SESSION"
        self.base_view = "VIEW"
        self.history = []
        self.current_user = MagicMock()

    @require_valid_token
    def foo(self, arg):
        return f"foo:{arg}"


class TestContractController(unittest.TestCase):
    def setUp(self):
        self.d = Dummy()
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.base_view.loop = MagicMock()
        self.history = []
        self.current_user = MagicMock()
        self.ctrl = ContractController(self.session, self.base_view, self.current_user, self.history)

    def test_non_string_token_calls_original(self):
        # token n'est pas une str → on appelle directement foo
        self.d.current_user.token = 12345
        out = self.d.foo("bar")
        self.assertEqual(out, "foo:bar")

    @patch("src.controllers.auth_controller.AuthController")
    def test_empty_string_token_triggers_popup(self, mock_authctrl_cls):
        # token vide → on doit afficher le popup d'expiration
        popup_ret = "POPUP"
        inst = MagicMock()
        inst.show_expired_token_popup.return_value = popup_ret
        mock_authctrl_cls.return_value = inst

        self.d.current_user.token = ""
        out = self.d.foo("X")

        mock_authctrl_cls.assert_called_once_with(
            self.d.session, self.d.base_view, self.d.current_user, self.d.history
        )
        inst.show_expired_token_popup.assert_called_once()
        self.assertEqual(out, popup_ret)

    @patch("src.controllers.auth_controller.AuthController")
    @patch("utils.decorators.AuthService.verify_token")
    def test_verify_token_none_triggers_popup(self, mock_verify, mock_authctrl_cls):
        # verify_token retourne None → popup d'expiration
        mock_verify.return_value = None
        inst = MagicMock()
        inst.show_expired_token_popup.return_value = "POP2"
        mock_authctrl_cls.return_value = inst

        self.d.current_user.token = "ANY"
        out = self.d.foo("Z")

        mock_verify.assert_called_once_with("ANY")
        inst.show_expired_token_popup.assert_called_once()
        self.assertEqual(out, "POP2")

    @patch("src.controllers.auth_controller.AuthController")
    @patch("utils.decorators.AuthService.verify_token")
    def test_valid_token_calls_original(self, mock_verify, mock_authctrl_cls):
        # verify_token retourne un payload → on exécute foo normalement
        mock_verify.return_value = {"user_id": 1}
        self.d.current_user.token = "VALID"
        out = self.d.foo("Q")

        mock_verify.assert_called_once_with("VALID")
        # AuthController is always instantiated to verify token
        mock_authctrl_cls.assert_called_once_with(
            self.d.session, self.d.base_view, self.d.current_user, self.d.history
        )
        inst = mock_authctrl_cls.return_value
        inst.show_expired_token_popup.assert_not_called()
        self.assertEqual(out, "foo:Q")

import unittest
from unittest.mock import patch, MagicMock, call, ANY

import sentry_sdk
import urwid

from src.controllers.contract_controller import ContractController
from src.repositories.contract_repository import ContractRepository
from src.services.base_service import BaseService
from src.services.contract_service import ContractService


class DummyUser:
    def __init__(self):
        self.email_address = "user@mail.com"
        role = MagicMock()
        role.name = "admin"
        role.permissions = []
        self.role = role


class TestContractControllerMethods(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.base_view.loop = MagicMock()
        self.history = []
        self.current_user = DummyUser()
        self.ctrl = ContractController(self.session, self.base_view, self.current_user, self.history)

    @patch.object(BaseService, "get_all")
    @patch.object(ContractService, "filter_by_email_adress")
    @patch.object(ContractService, "filter_by_sales_email_adress")
    @patch.object(ContractService, "filtered_by_contract_signed_or_pending")
    @patch.object(ContractService, "filtered_by_contract_payed_or_not")
    @patch("sentry_sdk.capture_message")
    def test_define_data_to_display_branches(
        self,
        mock_capture,
        mock_payed,
        mock_signed,
        mock_sales,
        mock_client,
        mock_get_all
    ):
        # all
        mock_get_all.return_value = ["A"]
        res = self.ctrl.define_data_to_display("all", None)
        mock_get_all.assert_called_once_with(self.session)
        self.assertEqual(res, ["A"])

        # client
        mock_client.return_value = ["B"]
        res = self.ctrl.define_data_to_display("client", "c@mail")
        mock_capture.assert_any_call("client_email_address: c@mail")
        mock_client.assert_called_once_with("c@mail", self.session)
        mock_capture.assert_any_call(f"contract_objects: ['B']")
        self.assertEqual(res, ["B"])

        # current_user
        mock_sales.return_value = ["C"]
        res = self.ctrl.define_data_to_display("current_user", None)
        mock_sales.assert_called_once_with(self.current_user.email_address, self.session)
        self.assertEqual(res, ["C"])

        # not signed
        mock_signed.return_value = ["D"]
        res = self.ctrl.define_data_to_display("not signed", None)
        mock_signed.assert_called_once_with(self.session, "Pending")
        self.assertEqual(res, ["D"])

        # not payed
        mock_payed.return_value = ["E"]
        res = self.ctrl.define_data_to_display("not payed", None)
        mock_payed.assert_called_once_with(self.session, False)
        self.assertEqual(res, ["E"])

        # unknown
        res = self.ctrl.define_data_to_display("foo", None)
        self.assertIsNone(res)

    @patch.object(ContractController, "create_all_contracts_paginated_buttons_signal")
    @patch.object(ContractController, "create_client_contracts_paginated_buttons_signal")
    @patch.object(ContractController, "create_filtered_contracts_paginated_buttons_signal")
    def test_define_page_buttons_signal_needded(self, mock_filt, mock_client_sig, mock_all_sig):
        pag = MagicMock()
        btns = {}
        objs = []
        # all
        self.ctrl.define_page_buttons_signal_needded(pag, btns, objs, "all", None)
        mock_all_sig.assert_called_once_with(pag, btns, objs)
        # client
        self.ctrl.define_page_buttons_signal_needded(pag, btns, objs, "client", "x@mail")
        mock_client_sig.assert_called_once_with(pag, btns, objs, "x@mail")
        # filtered
        for ft in ["current_user", "signed", "not signed", "payed", "not payed"]:
            self.ctrl.define_page_buttons_signal_needded(pag, btns, objs, ft, None)
        self.assertEqual(mock_filt.call_count, 5)

    @patch("urwid.connect_signal")
    @patch.object(ContractController, "connect_button_signals")
    def test_create_client_contracts_paginated_buttons_signal(self, mock_connect_nav, mock_conn_sig):
        btn = MagicMock(); btn.get_label.return_value = "ID1"
        obj = MagicMock(); obj.sales_contact_id = "user@mail.com"
        self.current_user.role.permissions = [MagicMock(action="contract_create")]
        pag = MagicMock()
        buttons = {"buttons_items": [btn]}

        self.ctrl.create_client_contracts_paginated_buttons_signal(pag, buttons, [obj], "user@mail")
        # detail button hook
        mock_conn_sig.assert_called_once()
        # navigation actions include Create
        actions = mock_connect_nav.call_args[0][1]
        labels = [lbl for lbl, _ in actions]
        self.assertIn("Previous", labels)
        self.assertIn("Next", labels)
        self.assertIn("Create", labels)

    @patch("urwid.connect_signal")
    @patch.object(ContractController, "connect_button_signals")
    def test_create_filtered_contracts_paginated_buttons_signal(self, mock_connect_nav, mock_conn_sig):
        btn = MagicMock(); btn.get_label.return_value = "ID2"
        obj = MagicMock(); obj.support_user_id = "other@mail.com"
        self.current_user.role.permissions = []
        pag = MagicMock()
        buttons = {"buttons_items": [btn]}

        self.ctrl.create_filtered_contracts_paginated_buttons_signal(pag, buttons, [obj])
        mock_conn_sig.assert_called_once()
        actions = mock_connect_nav.call_args[0][1]
        labels = [lbl for lbl, _ in actions]
        self.assertEqual(labels, ["Previous", "Next"])

    @patch("urwid.connect_signal")
    @patch.object(ContractController, "connect_button_signals")
    def test_create_all_contracts_paginated_buttons_signal(self, mock_connect_buttons, mock_urwid):
        btn = MagicMock(); btn.get_label.return_value = "ID3"
        obj = MagicMock(); obj.sales_contact_id = "x@mail"
        self.current_user.role.permissions = []
        pag = MagicMock()
        buttons = {"buttons_items": [btn]}

        self.ctrl.create_all_contracts_paginated_buttons_signal(pag, buttons, [obj])

        # ensure we patched urwid.connect_signal so no real error
        mock_urwid.assert_called_once()

        actions = mock_connect_buttons.call_args[0][1]
        labels = [lbl for lbl, _ in actions]
        expected = ["Previous", "Next", "My contracts", "Not signed contracts", "Not payed contracts"]
        for e in expected:
            self.assertIn(e, labels)

    def test_define_page_buttons_nedded(self):
        # all/admin
        self.current_user.role.name = "admin"; self.current_user.role.permissions = []
        res = self.ctrl.define_page_buttons_nedded(["L"], "all")
        self.assertIn("My contracts", res["buttons"])
        # client/create
        self.current_user.role.permissions = [MagicMock(action="contract_create")]
        res = self.ctrl.define_page_buttons_nedded(["L"], "client")
        self.assertIn("Create", res["buttons"])
        # filtered
        for ft in ["current_user", "not signed", "not payed"]:
            res = self.ctrl.define_page_buttons_nedded(["L"], ft)
            self.assertEqual(res["buttons"], ["Previous", "Next"])
        # unknown
        self.assertIsNone(self.ctrl.define_page_buttons_nedded(["L"], "something"))

    @patch("urwid.connect_signal")
    def test_create_client_contracts(self, mock_conn_sig):
        layout = {"buttons": [MagicMock()], "edits": [], "layout": "LAY"}
        self.base_view.create_form_layout.return_value = layout
        self.ctrl.create_client_contracts("c@mail")
        mock_conn_sig.assert_called_once_with(
            layout["buttons"][0], "click", ANY
        )
        self.base_view.update_screen.assert_called_once_with("LAY")

    @patch.object(BaseService, "create")
    @patch.object(ContractService, "generate_uid")
    def test_handle_client_creation_button_event(self, mock_uid, mock_create):
        mock_uid.return_value = "UID123"
        mock_create.return_value = True
        edits = [MagicMock(get_edit_text=MagicMock(return_value=v)) for v in ("100", "50", "X")]
        layout = {"edits": edits}
        self.ctrl.history = ["old", "current"]
        self.ctrl.handle_client_creation_button_event(layout, "client@mail")
        mock_uid.assert_called_once_with(self.session)
        mock_create.assert_called_once()
        self.base_view.update_screen.assert_called_once_with("old")

    @patch.object(ContractService, "generate_uid", return_value="DUMMY_ID")
    @patch.object(BaseService, "create")
    def test_handle_client_creation_button_event_failure(self, mock_create, mock_generate_uid):
        mock_create.return_value = False
        layout = {"edits": [MagicMock()] * 3}
        self.ctrl.handle_client_creation_button_event(layout, "c@mail")
        self.base_view.display_message.assert_called_once_with(
            "Contract creation failed. Please try again."
        )

    @patch.object(BaseService, "remove_attributes_from_object")
    @patch.object(ContractController, "connect_button_signals")
    def test_create_details_view_buttons_signal(self, mock_conn_nav, mock_remove):
        btns = [MagicMock(), MagicMock()]
        obj = MagicMock(id="ID444")
        obj.to_dict.return_value = {"a": 1, "ID": 1}
        mock_remove.return_value = {"a": 1}
        self.ctrl.create_details_view_buttons_signal(btns, obj)
        mock_remove.assert_called_once_with(
            obj.to_dict(),
            ["ID", "Client Name", "Client Email address", "Client Phone", "Client Compagny", "Creation date"]
        )
        mock_conn_nav.assert_called_once()
