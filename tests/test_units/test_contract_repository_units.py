import unittest
from unittest.mock import MagicMock, patch

from src.repositories.contract_repository import ContractRepository
from src.models.contract import Contract

class QueryFake:
    def __init__(self, result=None, exc=None):
        self._result = result
        self._exc = exc

    def filter(self, *args, **kwargs):
        if self._exc:
            raise self._exc
        return self

    def all(self):
        if self._exc:
            raise self._exc
        return self._result

    def first(self):
        if self._exc:
            raise self._exc
        return self._result


class TestContractRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.repo = ContractRepository()

    def test_filter_by_sales_email_address_success(self):
        fake_contracts = ["c1", "c2"]
        q = QueryFake(result=fake_contracts)
        self.session.query.return_value = q
        result = self.repo.filter_by_sales_email_address("sales@mail", self.session)
        self.session.query.assert_called_once_with(Contract)
        self.assertEqual(result, fake_contracts)

    @patch('src.repositories.contract_repository.sentry_sdk.capture_message')
    @patch('src.repositories.contract_repository.sentry_sdk.capture_exception')
    def test_filter_by_sales_email_address_exception(self, mock_exc, mock_msg):
        self.session.query.side_effect = RuntimeError("db fail")
        result = self.repo.filter_by_sales_email_address("x", self.session)
        mock_msg.assert_called_once_with("Error retrieving contract")
        mock_exc.assert_called_once()
        self.assertFalse(result)

    def test_filter_by_client_email_address_success(self):
        fake_contracts = ["d1"]
        q = QueryFake(result=fake_contracts)
        self.session.query.return_value = q
        result = self.repo.filter_by_client_email_address("client@mail", self.session)
        self.session.query.assert_called_once_with(Contract)
        self.assertEqual(result, fake_contracts)

    @patch('src.repositories.contract_repository.sentry_sdk.capture_exception')
    def test_filter_by_client_email_address_exception(self, mock_exc):
        self.session.query.return_value = QueryFake(exc=ValueError("fail"))
        with self.assertRaises(ValueError) as cm:
            self.repo.filter_by_client_email_address("a", self.session)
        self.assertIn("Error filtering contracts by client email address: fail",
                      str(cm.exception))
        mock_exc.assert_called_once()

    def test_filtered_by_contract_signed_or_pending_success(self):
        fake = ["s1"]
        q = QueryFake(result=fake)
        self.session.query.return_value = q
        result = self.repo.filtered_by_contract_signed_or_pending(self.session, "Signed")
        self.session.query.assert_called_once_with(Contract)
        self.assertEqual(result, fake)

    @patch('src.repositories.contract_repository.sentry_sdk.capture_exception')
    def test_filtered_by_contract_signed_or_pending_exception(self, mock_exc):
        self.session.query.side_effect = Exception("oops")
        with self.assertRaises(ValueError) as cm:
            self.repo.filtered_by_contract_signed_or_pending(self.session, "Pending")
        self.assertIn("Error filtering contracts by signed status: oops",
                      str(cm.exception))
        mock_exc.assert_called_once()

    def test_filtered_by_contract_payed_or_not_true(self):
        fake = ["p1"]
        q = QueryFake(result=fake)
        self.session.query.return_value = q
        result = self.repo.filtered_by_contract_payed_or_not(self.session, True)
        self.session.query.assert_called_with(Contract)
        self.assertEqual(result, fake)

    def test_filtered_by_contract_payed_or_not_false(self):
        fake = ["p2"]
        q = QueryFake(result=fake)
        self.session.query.return_value = q
        result = self.repo.filtered_by_contract_payed_or_not(self.session, False)
        self.assertEqual(result, fake)

    @patch('src.repositories.contract_repository.sentry_sdk.capture_message')
    @patch('src.repositories.contract_repository.sentry_sdk.capture_exception')
    def test_filtered_by_contract_payed_or_not_invalid_type(self, mock_exc, mock_msg):
        with self.assertRaises(ValueError) as cm:
            self.repo.filtered_by_contract_payed_or_not(self.session, "yes")
        # outer except wraps the initial ValueError
        self.assertIn("Error filtering contracts by payed status: The value must be a boolean",
                      str(cm.exception))
        mock_msg.assert_called_with("The value must be a boolean.")
        mock_exc.assert_called_once()

    def test_find_existing_uid_success(self):
        inst = Contract(id="UID")
        q = QueryFake(result=inst)
        self.session.query.return_value = q
        result = self.repo.find_existing_uid(self.session, "UID")
        self.session.query.assert_called_once_with(Contract)
        self.assertIs(result, inst)

    @patch('src.repositories.contract_repository.sentry_sdk.capture_exception')
    def test_find_existing_uid_exception(self, mock_exc):
        self.session.query.side_effect = RuntimeError("fail")
        with self.assertRaises(ValueError) as cm:
            self.repo.find_existing_uid(self.session, "X")
        self.assertEqual(str(cm.exception), "Error finding existing UID")
        mock_exc.assert_called_once()


if __name__ == '__main__':
    unittest.main()