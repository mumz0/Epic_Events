import unittest
from unittest.mock import MagicMock, patch

from src.repositories.event_repository import EventRepository
from src.models.event import Event

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


class TestEventRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.repo = EventRepository()

    def test_filter_by_client_email_address_success(self):
        fake_events = ["e1", "e2"]
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = fake_events
        self.session.query.return_value = q

        result = self.repo.filter_by_client_email_address("client@mail", self.session)

        # session.query should be called with Event
        self.session.query.assert_called_once_with(Event)
        self.assertEqual(result, fake_events)

    @patch('src.repositories.event_repository.sentry_sdk.capture_exception')
    def test_filter_by_client_email_address_exception(self, mock_exc):
        self.session.query.side_effect = RuntimeError("db fail")
        with self.assertRaises(ValueError) as cm:
            self.repo.filter_by_client_email_address("x", self.session)
        self.assertIn("Error filtering events by client email address", str(cm.exception))
        mock_exc.assert_called_once()

    def test_filter_by_support_user_on_event_true(self):
        fake = ["s1"]
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = fake
        self.session.query.return_value = q

        result = self.repo.filter_by_support_user_on_event(self.session, True)

        # session.query should be called with Event
        self.session.query.assert_called_once_with(Event)
        self.assertEqual(result, fake)

    def test_filter_by_support_user_on_event_false(self):
        fake = ["s2"]
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = fake
        self.session.query.return_value = q

        result = self.repo.filter_by_support_user_on_event(self.session, False)

        # session.query should be called with Event
        self.session.query.assert_called_once_with(Event)
        self.assertEqual(result, fake)

    @patch('src.repositories.event_repository.sentry_sdk.capture_exception')
    def test_filter_by_support_user_on_event_exception(self, mock_exc):
        bad_q = MagicMock()
        bad_q.filter.side_effect = Exception("err")
        self.session.query.return_value = bad_q

        with self.assertRaises(ValueError) as cm:
            self.repo.filter_by_support_user_on_event(self.session, False)
        self.assertIn("Error filtering events by support user", str(cm.exception))
        mock_exc.assert_called_once()

    def test_filter_by_support_email_address_success(self):
        fake = ["e3"]
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = fake
        self.session.query.return_value = q

        result = self.repo.filter_by_support_email_address("support@mail", self.session)

        # session.query should be called with Event
        self.session.query.assert_called_once_with(Event)
        self.assertEqual(result, fake)

    @patch('src.repositories.event_repository.sentry_sdk.capture_exception')
    def test_filter_by_support_email_address_exception(self, mock_exc):
        self.session.query.side_effect = RuntimeError("fail")
        with self.assertRaises(ValueError) as cm:
            self.repo.filter_by_support_email_address("x", self.session)
        self.assertIn("Error filtering events by support email address", str(cm.exception))
        mock_exc.assert_called_once()
        