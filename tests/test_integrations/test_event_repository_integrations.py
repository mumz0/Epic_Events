from datetime import datetime

from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User
from src.repositories.event_repository import EventRepository
from tests.test_integrations.run_tests import BaseTestDB


class TestEventRepositoryIntegration(BaseTestDB):

    def setUp(self):
        super().setUp()
        self.event_repository = EventRepository()

        support_user = User(email_address="support1@support.com", password="securepassword", role_id="support")
        sales_contact = User(email_address="sales2@sales.com", password="securepassword", role_id="sales")
        self.session.add(sales_contact, support_user)
        self.session.flush()

        client = Client(email_address="client13@example.com", name="Client 1", sales_contact_id=sales_contact.id)
        contract1 = Contract(id=1, client_id=client.email_address, sales_contact_id=sales_contact.id)
        contract2 = Contract(id=2, client_id=client.email_address, sales_contact_id=sales_contact.id)
        event1 = Event(
            id="EVENT1",
            name="Event 1",
            client_id=client.email_address,
            contract_id=contract1.id,
            support_user_id=support_user.email_address,
            start_date=datetime(2023, 10, 1),
            end_date=datetime(2023, 10, 2),
        )
        event2 = Event(
            id="EVENT2",
            name="Event 2",
            client_id=client.email_address,
            contract_id=contract2.id,
            support_user_id=None,
            start_date=datetime(2023, 10, 3),
            end_date=datetime(2023, 10, 4),
        )
        self.session.add_all([client, contract1, contract2, event1, event2])
        self.session.flush()

    def test_filter_by_client_email_address(self):
        result = self.event_repository.filter_by_client_email_address("client13@example.com", self.session)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, "EVENT1")
        self.assertEqual(result[1].id, "EVENT2")

    def test_filter_by_support_user_on_event(self):
        result_with_support = self.event_repository.filter_by_support_user_on_event(self.session, True)
        self.assertEqual(len(result_with_support), 1)
        self.assertEqual(result_with_support[0].id, "EVENT1")

        result_without_support = self.event_repository.filter_by_support_user_on_event(self.session, False)
        self.assertEqual(len(result_without_support), 1)
        self.assertEqual(result_without_support[0].id, "EVENT2")

    def test_filter_by_support_email_address(self):
        result = self.event_repository.filter_by_support_email_address("support1@support.com", self.session)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "EVENT1")

    def always_fail_query(self, *args, **kwargs):
        raise Exception("Test induced error")

    def test_filter_by_client_email_address_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.event_repository.filter_by_client_email_address("client13@example.com", self.session)
        self.assertIn("Error filtering events by client email address", str(context.exception))
        self.session.query = original_query

    def test_filter_by_support_user_on_event_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.event_repository.filter_by_support_user_on_event(self.session, True)
        self.assertIn("Error filtering events by support user", str(context.exception))
        self.session.query = original_query

    def test_filter_by_support_email_address_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.event_repository.filter_by_support_email_address("support1@support.com", self.session)
        self.assertIn("Error filtering events by support email address", str(context.exception))
        self.session.query = original_query

    def tearDown(self):
        self.session.rollback()
        super().tearDown()
