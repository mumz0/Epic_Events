import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.models.event import Event
from src.services.event_service import EventService


class TestEventService(unittest.TestCase):
    def setUp(self):
        self.event_service = EventService()
        self.mock_session = MagicMock()

    def test_list_to_dict(self):
        mock_event = MagicMock()
        mock_event.id = "123"
        event_list = [mock_event]

        result = self.event_service.list_to_dict(event_list)

        self.assertEqual(result["ID"], "123")

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_list_to_dict_exception(self, mock_capture_exception):
        result = self.event_service.list_to_dict(None)

        self.assertEqual(result, {})
        mock_capture_exception.assert_called_once()

    def test_filter_by_support_email_adress(self):
        self.event_service.repository.filter_by_support_email_address = MagicMock(return_value=["event1", "event2"])
        result = self.event_service.filter_by_support_email_adress("support@example.com", self.mock_session)

        self.assertEqual(result, ["event1", "event2"])

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_filter_by_support_email_adress_exception(self, mock_capture_exception):
        self.event_service.repository.filter_by_support_email_address = MagicMock(side_effect=Exception("Error"))
        result = self.event_service.filter_by_support_email_adress("support@example.com", self.mock_session)

        self.assertEqual(result, [])
        mock_capture_exception.assert_called_once()

    def test_filter_by_email_adress(self):
        self.event_service.repository.filter_by_client_email_address = MagicMock(return_value=["event1", "event2"])
        result = self.event_service.filter_by_email_adress("client@example.com", self.mock_session)

        self.assertEqual(result, ["event1", "event2"])

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_filter_by_email_adress_exception(self, mock_capture_exception):
        self.event_service.repository.filter_by_client_email_address = MagicMock(side_effect=Exception("Error"))
        result = self.event_service.filter_by_email_adress("client@example.com", self.mock_session)

        self.assertEqual(result, [])
        mock_capture_exception.assert_called_once()

    def test_string_date_to_datetime(self):
        date_string = "2023/10/01"
        result = self.event_service.string_date_to_datetime(date_string)

        self.assertEqual(result, datetime(2023, 10, 1))

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_string_date_to_datetime_exception(self, mock_capture_exception):
        result = self.event_service.string_date_to_datetime("invalid_date")

        self.assertIsNone(result)
        mock_capture_exception.assert_called_once()

    @patch("src.services.event_service.uuid.uuid4")
    def test_generate_uid(self, mock_uuid4):
        mock_uuid4.return_value = MagicMock(hex="1234567890ABCDEF")
        self.mock_session.query().filter().first.return_value = None

        result = self.event_service.generate_uid(self.mock_session, length=8)

        self.assertTrue(result.startswith("EVENT"))
        self.assertEqual(len(result), 13)

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_generate_uid_exception(self, mock_capture_exception):
        self.mock_session.query().filter().first.side_effect = Exception("Error")
        result = self.event_service.generate_uid(self.mock_session)

        self.assertIsNone(result)
        mock_capture_exception.assert_called_once()

    def test_filter_by_support_user_on_event(self):
        self.event_service.repository.filter_by_support_user_on_event = MagicMock(return_value=["event1", "event2"])
        result = self.event_service.filter_by_support_user_on_event(self.mock_session, True)

        self.assertEqual(result, ["event1", "event2"])

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_filter_by_support_user_on_event_exception(self, mock_capture_exception):
        self.event_service.repository.filter_by_support_user_on_event = MagicMock(side_effect=Exception("Error"))
        result = self.event_service.filter_by_support_user_on_event(self.mock_session, True)

        self.assertEqual(result, [])
        mock_capture_exception.assert_called_once()

    def test_prepare_data_and_update(self):
        mock_obj = MagicMock()
        mock_obj.id = "123"
        self.event_service.repository.update_obj = MagicMock(return_value={"updated": True})
        data = {"Start Date": "2023/10/01", "End Date": "2023/10/02"}

        result = self.event_service.prepare_data_and_update(data, mock_obj, self.mock_session)

        self.assertEqual(result, {"updated": True})
        self.assertEqual(data["start_date"], datetime(2023, 10, 1))
        self.assertEqual(data["end_date"], datetime(2023, 10, 2))

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_prepare_data_and_update_exception(self, mock_capture_exception):
        mock_obj = MagicMock()
        mock_obj.id = "123"
        self.event_service.repository.update_obj = MagicMock(side_effect=Exception("Error"))
        data = {"Start Date": "invalid_date", "End Date": "2023/10/02"}

        result = self.event_service.prepare_data_and_update(data, mock_obj, self.mock_session)

        self.assertEqual(result, {})
        mock_capture_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()
