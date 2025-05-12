import unittest
from datetime import datetime

from src.models.client import Client
from src.models.contract import Contract
from src.models.user import User
from src.repositories.contract_repository import ContractRepository
from tests.test_integrations.run_tests import BaseTestDB


class TestContractRepositoryIntegration(BaseTestDB):
    def setUp(self):
        super().setUp()
        self.contract_repository = ContractRepository()

        self.sales_user = User(email_address="sales4@example.com", password="password", role_id="sales")
        self.client = Client(email_address="client@example.com", name="Test Client", sales_contact_id=self.sales_user.email_address)
        self.contract_signed = Contract(
            id="CONTRACT1",
            client_id=self.client.email_address,
            sales_contact_id=self.sales_user.email_address,
            status_id="Signed",
            price=1000,
            Outstanding_balance=0,
        )
        self.contract_pending = Contract(
            id="CONTRACT2",
            client_id=self.client.email_address,
            sales_contact_id=self.sales_user.email_address,
            status_id="Pending",
            price=2000,
            Outstanding_balance=500,
        )
        self.session.add_all([self.sales_user, self.client, self.contract_signed, self.contract_pending])
        self.session.flush()

    def test_filter_by_sales_email_address(self):
        contracts = self.contract_repository.filter_by_sales_email_address("sales4@example.com", self.session)
        self.assertEqual(len(contracts), 2)
        self.assertTrue(any(contract.id == "CONTRACT1" for contract in contracts))
        self.assertTrue(any(contract.id == "CONTRACT2" for contract in contracts))

    def test_filter_by_client_email_address(self):
        contracts = self.contract_repository.filter_by_client_email_address("client@example.com", self.session)
        self.assertEqual(len(contracts), 2)
        self.assertTrue(any(contract.id == "CONTRACT1" for contract in contracts))
        self.assertTrue(any(contract.id == "CONTRACT2" for contract in contracts))

    def test_filtered_by_contract_signed_or_pending(self):
        signed_contracts = self.contract_repository.filtered_by_contract_signed_or_pending(self.session, "Signed")
        self.assertEqual(len(signed_contracts), 1)
        self.assertEqual(signed_contracts[0].id, "CONTRACT1")

        pending_contracts = self.contract_repository.filtered_by_contract_signed_or_pending(self.session, "Pending")
        self.assertEqual(len(pending_contracts), 1)
        self.assertEqual(pending_contracts[0].id, "CONTRACT2")

    def test_filtered_by_contract_payed_or_not(self):
        payed_contracts = self.contract_repository.filtered_by_contract_payed_or_not(self.session, True)
        self.assertEqual(len(payed_contracts), 1)
        self.assertEqual(payed_contracts[0].id, "CONTRACT1")

        not_payed_contracts = self.contract_repository.filtered_by_contract_payed_or_not(self.session, False)
        self.assertEqual(len(not_payed_contracts), 1)
        self.assertEqual(not_payed_contracts[0].id, "CONTRACT2")

    def test_find_existing_uid(self):
        existing_contract = self.contract_repository.find_existing_uid(self.session, "CONTRACT1")
        self.assertIsNotNone(existing_contract)
        self.assertEqual(existing_contract.id, "CONTRACT1")

        non_existing_contract = self.contract_repository.find_existing_uid(self.session, "NONEXISTENT")
        self.assertIsNone(non_existing_contract)

    def tearDown(self):
        self.session.rollback()
        super().tearDown()
