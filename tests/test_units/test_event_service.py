import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.services.event_service import EventService
from src.models.event import Event


class TestEventService(unittest.TestCase):
    def setUp(self):
        self.service = EventService()
        self.session = MagicMock()
        # replace real repository with a mock
        self.service.repository = MagicMock()

    def test_list_to_dict_success(self):
        e1 = MagicMock(id="E1")
        e2 = MagicMock(id="E2")
        result = self.service.list_to_dict([e1, e2])
        # code overwrites same key, so last id remains
        self.assertEqual(result, {"ID": "E2"})

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    @patch("src.services.event_service.sentry_sdk.capture_message")
    def test_list_to_dict_exception(self, mock_capture_message, mock_capture_exception):
        # passing None causes TypeError in iteration
        result = self.service.list_to_dict(None)
        self.assertEqual(result, {})
        mock_capture_message.assert_called_with("Error converting event list to dictionary")
        mock_capture_exception.assert_called_once()

    def test_filter_by_support_email_adress_success(self):
        expected = ["ev1", "ev2"]
        self.service.repository.filter_by_support_email_address.return_value = expected
        result = self.service.filter_by_support_email_adress("a@b.com", self.session)
        self.assertEqual(result, expected)
        self.service.repository.filter_by_support_email_address.assert_called_once_with("a@b.com", self.session)

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    @patch("src.services.event_service.sentry_sdk.capture_message")
    def test_filter_by_support_email_adress_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.filter_by_support_email_address.side_effect = Exception("err")
        result = self.service.filter_by_support_email_adress("a@b.com", self.session)
        self.assertEqual(result, [])
        mock_capture_message.assert_called_with("Error filtering events by support email address")
        mock_capture_exception.assert_called_once()

    def test_filter_by_email_adress_success(self):
        expected = ["ev"]
        self.service.repository.filter_by_client_email_address.return_value = expected
        result = self.service.filter_by_email_adress("c@d.com", self.session)
        self.assertEqual(result, expected)
        self.service.repository.filter_by_client_email_address.assert_called_once_with("c@d.com", self.session)

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    @patch("src.services.event_service.sentry_sdk.capture_message")
    def test_filter_by_email_adress_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.filter_by_client_email_address.side_effect = Exception("oops")
        result = self.service.filter_by_email_adress("c@d.com", self.session)
        self.assertEqual(result, [])
        mock_capture_message.assert_called_with("Error filtering events by email address")
        mock_capture_exception.assert_called_once()

    def test_string_date_to_datetime_success(self):
        ds = "2022/12/31"
        dt = self.service.string_date_to_datetime(ds)
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt, datetime(2022, 12, 31))

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    @patch("src.services.event_service.sentry_sdk.capture_message")
    def test_string_date_to_datetime_exception(self, mock_capture_message, mock_capture_exception):
        dt = self.service.string_date_to_datetime("bad-date")
        self.assertIsNone(dt)
        mock_capture_message.assert_called_with("Error converting date string to datetime")
        mock_capture_exception.assert_called_once()

    @patch("src.services.event_service.uuid.uuid4")
    def test_generate_uid_success(self, mock_uuid4):
        # stub uuid and session.query workflow
        mock_uuid4.return_value = MagicMock(hex="ABCDE12345FGHIJ")
        fake_q = MagicMock()
        fake_q.filter.return_value = fake_q
        # first return something truthy, then None
        fake_q.first.side_effect = [1, None]
        self.session.query.return_value = fake_q

        uid = EventService.generate_uid(self.session, length=5)
        self.assertEqual(uid, "EVENTABCDE")

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    @patch("src.services.event_service.sentry_sdk.capture_message")
    def test_generate_uid_exception(self, mock_capture_message, mock_capture_exception):
        self.session.query.side_effect = Exception("db fail")
        uid = EventService.generate_uid(self.session)
        self.assertIsNone(uid)
        mock_capture_message.assert_called_with("Error generating UID")
        mock_capture_exception.assert_called_once()

    def test_filter_by_support_user_on_event_success(self):
        expected = ["x"]
        self.service.repository.filter_by_support_user_on_event.return_value = expected
        result = self.service.filter_by_support_user_on_event(self.session, True)
        self.assertEqual(result, expected)
        self.service.repository.filter_by_support_user_on_event.assert_called_once_with(self.session, True)

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    @patch("src.services.event_service.sentry_sdk.capture_message")
    def test_filter_by_support_user_on_event_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.filter_by_support_user_on_event.side_effect = Exception("err")
        result = self.service.filter_by_support_user_on_event(self.session, False)
        self.assertEqual(result, [])
        mock_capture_message.assert_called_with("Error filtering events by support user")
        mock_capture_exception.assert_called_once()

    def test_prepare_data_and_update_success_start_date(self):
        # only start date
        evt = MagicMock()
        data = {"Start Date": "2023/01/05"}
        updated = {"ok": True}
        self.service.repository.update_obj.return_value = updated

        result = self.service.prepare_data_and_update(data, evt, self.session)
        self.assertEqual(result, updated)
        called_data, called_obj, called_sess = self.service.repository.update_obj.call_args[0]
        self.assertIs(called_obj, evt)
        self.assertIs(called_sess, self.session)
        self.assertIn("start_date", called_data)
        self.assertEqual(called_data["start_date"], datetime(2023, 1, 5))

    def test_prepare_data_and_update_success_end_date(self):
        # only end date
        evt = MagicMock()
        data = {"End Date": "2023/02/10"}
        updated = {"ok": False}
        self.service.repository.update_obj.return_value = updated

        result = self.service.prepare_data_and_update(data, evt, self.session)
        self.assertEqual(result, updated)
        called_data = self.service.repository.update_obj.call_args[0][0]
        self.assertIn("end_date", called_data)
        self.assertEqual(called_data["end_date"], datetime(2023, 2, 10))

    def test_prepare_data_and_update_success_both(self):
        evt = MagicMock()
        data = {"Start Date": "2021/03/04", "End Date": "2021/03/05"}
        updated = {"yes": True}
        self.service.repository.update_obj.return_value = updated

        result = self.service.prepare_data_and_update(data, evt, self.session)
        self.assertEqual(result, updated)
        called_data = self.service.repository.update_obj.call_args[0][0]
        self.assertEqual(called_data["start_date"], datetime(2021, 3, 4))
        self.assertEqual(called_data["end_date"], datetime(2021, 3, 5))

    @patch("src.services.event_service.sentry_sdk.capture_exception")
    def test_prepare_data_and_update_exception(self, mock_capture_exception):
        # repository.update_obj raises
        self.service.repository.update_obj.side_effect = Exception("fail")
        evt = MagicMock()
        data = {"Start Date": "2020/01/01"}
        result = self.service.prepare_data_and_update(data, evt, self.session)
        self.assertEqual(result, {})
        mock_capture_exception.assert_called_once()