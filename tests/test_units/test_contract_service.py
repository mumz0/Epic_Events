import unittest
from unittest.mock import MagicMock, patch
import uuid

from src.services.contract_service import ContractService


class TestContractService(unittest.TestCase):
    def setUp(self):
        self.service = ContractService()
        self.session = MagicMock()
        # replace real repository with a mock
        self.service.repository = MagicMock()

    def test_list_to_dict_success(self):
        c1 = MagicMock(id="c1")
        c1.to_dict.return_value = {"a": 1}
        c2 = MagicMock(id="c2")
        c2.to_dict.return_value = {"b": 2}
        result = self.service.list_to_dict([c1, c2])
        self.assertEqual(result, {"c1": {"a": 1}, "c2": {"b": 2}})

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_list_to_dict_exception(self, mock_msg, mock_exc):
        bad = MagicMock()
        bad.to_dict.side_effect = RuntimeError("fail")
        result = self.service.list_to_dict([bad])
        self.assertEqual(result, {})
        mock_msg.assert_called_with("Error converting contract list to dictionary")
        mock_exc.assert_called_once()

    def test_filter_by_sales_email_adress_success(self):
        expected = ["ctr1", "ctr2"]
        self.service.repository.filter_by_sales_email_address.return_value = expected
        result = self.service.filter_by_sales_email_adress("e@mail", self.session)
        self.assertEqual(result, expected)
        self.service.repository.filter_by_sales_email_address.assert_called_once_with("e@mail", self.session)

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_filter_by_sales_email_adress_exception(self, mock_msg, mock_exc):
        self.service.repository.filter_by_sales_email_address.side_effect = Exception("err")
        result = self.service.filter_by_sales_email_adress("e@mail", self.session)
        self.assertEqual(result, [])
        mock_msg.assert_called_with("Error filtering contracts by sales email address")
        mock_exc.assert_called_once()

    def test_filter_by_email_adress_success(self):
        expected = ["ctr"]
        self.service.repository.filter_by_client_email_address.return_value = expected
        result = self.service.filter_by_email_adress("e@mail", self.session)
        self.assertEqual(result, expected)
        self.service.repository.filter_by_client_email_address.assert_called_once_with("e@mail", self.session)

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_filter_by_email_adress_exception(self, mock_msg, mock_exc):
        self.service.repository.filter_by_client_email_address.side_effect = Exception("err")
        result = self.service.filter_by_email_adress("e@mail", self.session)
        self.assertEqual(result, [])
        mock_msg.assert_called_with("Error filtering contracts by email address")
        mock_exc.assert_called_once()

    @patch("src.services.contract_service.UserService.get_user")
    def test_prepare_data_and_update_success(self, mock_get_user):
        user = MagicMock(email_address="sales@mail")
        mock_get_user.return_value = user
        self.service.repository.update_obj.return_value = {"ok": True}
        data = {
            "Sales contact": "sales@mail",
            "Price": 100,
            "Outstanding balance": 20,
            "Status": "Pending",
        }
        obj = MagicMock(id="cid")
        result = self.service.prepare_data_and_update(data, obj, self.session)
        self.assertEqual(result, {"ok": True})
        mock_get_user.assert_called_once_with("sales@mail", self.session)
        self.service.repository.update_obj.assert_called_once_with(
            "cid",
            {
                "price": 100,
                "Outstanding_balance": 20,
                "status_id": "Pending",
                "sales_contact_id": "sales@mail",
            },
            self.session,
        )

    @patch("src.services.contract_service.sentry_sdk.capture_message")
    @patch("src.services.contract_service.UserService.get_user")
    def test_prepare_data_and_update_no_user(self, mock_get_user, mock_msg):
        mock_get_user.return_value = None
        data = {"Sales contact": "none@mail"}
        obj = MagicMock(id="cid")
        with self.assertRaises(ValueError) as cm:
            self.service.prepare_data_and_update(data, obj, self.session)
        self.assertEqual(str(cm.exception), "Sales contact not found")
        mock_msg.assert_called_with("Sales contact not found")

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    @patch("src.services.contract_service.UserService.get_user")
    def test_prepare_data_and_update_generic_exception(self, mock_get_user, mock_msg, mock_exc):
        mock_get_user.side_effect = Exception("fail")
        data = {"Sales contact": "x"}
        obj = MagicMock()
        result = self.service.prepare_data_and_update(data, obj, self.session)
        self.assertEqual(result, {})
        mock_msg.assert_called_with("Error preparing data and updating contract")
        mock_exc.assert_called_once()

    @patch("uuid.uuid4")
    def test_generate_uid_success(self, mock_uuid4):
        mock_uuid4.return_value = MagicMock(hex="ABCDEF0123456789")
        # first collision then unique
        self.service.repository.find_existing_uid.side_effect = [True, None]
        uid = self.service.generate_uid(self.session, length=5)
        self.assertEqual(uid, "CONTRACTABCDE")

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_generate_uid_exception(self, mock_msg, mock_exc):
        self.service.repository.find_existing_uid.side_effect = Exception("oops")
        result = self.service.generate_uid(self.session)
        self.assertIsNone(result)
        mock_msg.assert_called_with("Error generating UID")
        mock_exc.assert_called_once()

    def test_filtered_by_contract_signed_or_pending_success(self):
        expected = ["s1"]
        self.service.repository.filtered_by_contract_signed_or_pending.return_value = expected
        result = self.service.filtered_by_contract_signed_or_pending(self.session, True)
        self.assertEqual(result, expected)
        self.service.repository.filtered_by_contract_signed_or_pending.assert_called_once_with(self.session, True)

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_filtered_by_contract_signed_or_pending_exception(self, mock_msg, mock_exc):
        self.service.repository.filtered_by_contract_signed_or_pending.side_effect = Exception()
        result = self.service.filtered_by_contract_signed_or_pending(self.session, False)
        self.assertEqual(result, [])
        mock_msg.assert_called_with("Error filtering contracts by signed status")
        mock_exc.assert_called_once()

    def test_filtered_by_contract_payed_or_not_success(self):
        expected = ["p1"]
        self.service.repository.filtered_by_contract_payed_or_not.return_value = expected
        result = self.service.filtered_by_contract_payed_or_not(self.session, False)
        self.assertEqual(result, expected)
        self.service.repository.filtered_by_contract_payed_or_not.assert_called_once_with(self.session, False)

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_filtered_by_contract_payed_or_not_exception(self, mock_msg, mock_exc):
        self.service.repository.filtered_by_contract_payed_or_not.side_effect = Exception()
        result = self.service.filtered_by_contract_payed_or_not(self.session, True)
        self.assertEqual(result, [])
        mock_msg.assert_called_with("Error filtering contracts by payed status")
        mock_exc.assert_called_once()

    def test_check_if_contract_is_signed_true(self):
        ctr = MagicMock(status_id="Signed")
        self.service.repository.get.return_value = ctr
        result = self.service.check_if_contract_is_signed(self.session, "cid")
        self.assertTrue(result)
        self.service.repository.get.assert_called_once_with("cid", self.session)

    def test_check_if_contract_is_signed_false(self):
        ctr = MagicMock(status_id="Pending")
        self.service.repository.get.return_value = ctr
        result = self.service.check_if_contract_is_signed(self.session, "cid")
        self.assertFalse(result)

    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_check_if_contract_is_signed_not_found(self, mock_msg):
        self.service.repository.get.return_value = None
        with self.assertRaises(ValueError) as cm:
            self.service.check_if_contract_is_signed(self.session, "cid")
        self.assertEqual(str(cm.exception), "Contract not found")
        mock_msg.assert_called_with("Contract not found")

    @patch("src.services.contract_service.sentry_sdk.capture_exception")
    @patch("src.services.contract_service.sentry_sdk.capture_message")
    def test_check_if_contract_is_signed_exception(self, mock_msg, mock_exc):
        self.service.repository.get.side_effect = Exception("err")
        result = self.service.check_if_contract_is_signed(self.session, "cid")
        self.assertFalse(result)
        mock_msg.assert_called_with("Error checking if contract is signed")
        mock_exc.assert_called_once()