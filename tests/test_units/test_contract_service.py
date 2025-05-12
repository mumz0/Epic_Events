import unittest
from unittest.mock import MagicMock, patch

from src.models.contract import Contract
from src.services.contract_service import ContractService


class TestContractService(unittest.TestCase):
    def setUp(self):
        self.contract_service = ContractService()
        self.mock_session = MagicMock()

    @patch("src.services.contract_service.sentry_sdk")
    def test_list_to_dict(self, mock_sentry):
        contract1 = MagicMock(id=1, to_dict=MagicMock(return_value={"id": 1, "name": "Contract 1"}))
        contract2 = MagicMock(id=2, to_dict=MagicMock(return_value={"id": 2, "name": "Contract 2"}))
        contract_list = [contract1, contract2]

        result = self.contract_service.list_to_dict(contract_list)

        self.assertEqual(result, {1: {"id": 1, "name": "Contract 1"}, 2: {"id": 2, "name": "Contract 2"}})
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filter_by_sales_email_adress(self, mock_sentry):
        self.contract_service.repository.filter_by_sales_email_address = MagicMock(return_value=["contract1", "contract2"])
        email = "sales@example.com"

        result = self.contract_service.filter_by_sales_email_adress(email, self.mock_session)

        self.assertEqual(result, ["contract1", "contract2"])
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filter_by_email_adress(self, mock_sentry):
        self.contract_service.repository.filter_by_client_email_address = MagicMock(return_value=["contract1", "contract2"])
        email = "client@example.com"

        result = self.contract_service.filter_by_email_adress(email, self.mock_session)

        self.assertEqual(result, ["contract1", "contract2"])
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.UserService")
    @patch("src.services.contract_service.sentry_sdk")
    def test_prepare_data_and_update(self, mock_sentry, mock_user_service):
        mock_user_service().get_user.return_value = MagicMock(email_address="sales@example.com")
        self.contract_service.repository.update_obj = MagicMock(return_value={"updated": True})
        data = {
            "Sales contact": "sales@example.com",
            "Price": 1000,
            "Outstanding balance": 500,
            "Status": "Pending",
        }
        obj = MagicMock(id=1)

        result = self.contract_service.prepare_data_and_update(data, obj, self.mock_session)

        self.assertEqual(result, {"updated": True})
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.sentry_sdk")
    def test_generate_uid(self, mock_sentry):
        self.contract_service.repository.find_existing_uid = MagicMock(return_value=False)

        result = self.contract_service.generate_uid(self.mock_session, length=8)

        self.assertTrue(result.startswith("CONTRACT"))
        self.assertEqual(len(result), 16)  # "CONTRACT" + 8 characters
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filtered_by_contract_signed_or_pending(self, mock_sentry):
        self.contract_service.repository.filtered_by_contract_signed_or_pending = MagicMock(return_value=["contract1"])

        result = self.contract_service.filtered_by_contract_signed_or_pending(self.mock_session, "Signed")

        self.assertEqual(result, ["contract1"])
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filtered_by_contract_payed_or_not(self, mock_sentry):
        self.contract_service.repository.filtered_by_contract_payed_or_not = MagicMock(return_value=["contract1"])

        result = self.contract_service.filtered_by_contract_payed_or_not(self.mock_session, "Payed")

        self.assertEqual(result, ["contract1"])
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.sentry_sdk")
    def test_check_if_contract_is_signed(self, mock_sentry):
        contract = MagicMock(status_id="Signed")
        self.contract_service.repository.get = MagicMock(return_value=contract)

        result = self.contract_service.check_if_contract_is_signed(self.mock_session, "contract_id")

        self.assertTrue(result)
        mock_sentry.capture_message.assert_not_called()

    @patch("src.services.contract_service.sentry_sdk")
    def test_list_to_dict_fail(self, mock_sentry):
        # Simuler une exception lors de la conversion
        contract_list = [MagicMock(id=1, to_dict=MagicMock(side_effect=Exception("Error")))]

        result = self.contract_service.list_to_dict(contract_list)

        self.assertEqual(result, {})
        mock_sentry.capture_message.assert_called_once_with("Error converting contract list to dictionary")
        mock_sentry.capture_exception.assert_called_once()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filter_by_sales_email_adress_fail(self, mock_sentry):
        # Simuler une exception lors du filtrage
        self.contract_service.repository.filter_by_sales_email_address = MagicMock(side_effect=Exception("Error"))
        email = "sales@example.com"

        result = self.contract_service.filter_by_sales_email_adress(email, self.mock_session)

        self.assertEqual(result, [])
        mock_sentry.capture_message.assert_called_once_with("Error filtering contracts by sales email address")
        mock_sentry.capture_exception.assert_called_once()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filter_by_email_adress_fail(self, mock_sentry):
        # Simuler une exception lors du filtrage
        self.contract_service.repository.filter_by_client_email_address = MagicMock(side_effect=Exception("Error"))
        email = "client@example.com"

        result = self.contract_service.filter_by_email_adress(email, self.mock_session)

        self.assertEqual(result, [])
        mock_sentry.capture_message.assert_called_once_with("Error filtering contracts by email address")
        mock_sentry.capture_exception.assert_called_once()

    @patch("src.services.contract_service.sentry_sdk")
    def test_prepare_data_and_update_fail(self, mock_sentry):
        # Simuler une exception lors de la mise à jour
        self.contract_service.repository.update_obj = MagicMock(side_effect=Exception("Error"))
        data = {
            "Sales contact": "sales@example.com",
            "Price": 1000,
            "Outstanding balance": 500,
            "Status": "Pending",
        }
        obj = MagicMock(id=1)

        result = self.contract_service.prepare_data_and_update(data, obj, self.mock_session)

        self.assertEqual(result, {})
        mock_sentry.capture_message.assert_called_once_with("Error preparing data and updating contract")
        mock_sentry.capture_exception.assert_called_once()

    @patch("src.services.contract_service.sentry_sdk")
    def test_generate_uid_fail(self, mock_sentry):
        # Simuler une exception lors de la génération d'UID
        self.contract_service.repository.find_existing_uid = MagicMock(side_effect=Exception("Error"))

        result = self.contract_service.generate_uid(self.mock_session, length=8)

        self.assertIsNone(result)
        mock_sentry.capture_message.assert_called_once_with("Error generating UID")
        mock_sentry.capture_exception.assert_called_once()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filtered_by_contract_signed_or_pending_fail(self, mock_sentry):
        # Simuler une exception lors du filtrage
        self.contract_service.repository.filtered_by_contract_signed_or_pending = MagicMock(side_effect=Exception("Error"))

        result = self.contract_service.filtered_by_contract_signed_or_pending(self.mock_session, "Signed")

        self.assertEqual(result, [])
        mock_sentry.capture_message.assert_called_once_with("Error filtering contracts by signed status")
        mock_sentry.capture_exception.assert_called_once()

    @patch("src.services.contract_service.sentry_sdk")
    def test_filtered_by_contract_payed_or_not_fail(self, mock_sentry):
        # Simuler une exception lors du filtrage
        self.contract_service.repository.filtered_by_contract_payed_or_not = MagicMock(side_effect=Exception("Error"))

        result = self.contract_service.filtered_by_contract_payed_or_not(self.mock_session, "Payed")

        self.assertEqual(result, [])
        mock_sentry.capture_message.assert_called_once_with("Error filtering contracts by payed status")
        mock_sentry.capture_exception.assert_called_once()

    @patch("src.services.contract_service.sentry_sdk")
    def test_check_if_contract_is_signed_fail(self, mock_sentry):
        # Simuler une exception lors de la vérification
        self.contract_service.repository.get = MagicMock(side_effect=Exception("Error"))

        result = self.contract_service.check_if_contract_is_signed(self.mock_session, "contract_id")

        self.assertFalse(result)
        mock_sentry.capture_message.assert_called_once_with("Error checking if contract is signed")
        mock_sentry.capture_exception.assert_called_once()
