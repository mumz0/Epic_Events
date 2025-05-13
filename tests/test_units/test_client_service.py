import unittest
from unittest.mock import MagicMock, patch

from src.services.client_service import ClientService
from src.models.client import Client


class DummyClient:
    def __init__(self, id, data):
        self.id = id
        self._data = data

    def to_dict(self):
        return self._data


class TestClientService(unittest.TestCase):
    def setUp(self):
        self.service = ClientService()
        # replace real repository with a mock
        self.service.repository = MagicMock()
        self.session = MagicMock()

    def test_list_to_dict_success(self):
        clients = [
            DummyClient(1, {"a": 1}),
            DummyClient(2, {"b": 2})
        ]
        result = self.service.list_to_dict(clients)
        self.assertEqual(result, {1: {"a": 1}, 2: {"b": 2}})

    @patch("src.services.client_service.sentry_sdk.capture_exception")
    def test_list_to_dict_exception(self, mock_capture_exc):
        # make to_dict raise
        bad = MagicMock()
        bad.to_dict.side_effect = RuntimeError("fail")
        result = self.service.list_to_dict([bad])
        self.assertEqual(result, {})
        mock_capture_exc.assert_called_once()

    @patch("src.services.client_service.UserService.get_user")
    def test_prepare_data_and_update_success(self, mock_get_user):
        # prepare stub user and client
        user = MagicMock()
        user.email_address = "sales@example.com"
        mock_get_user.return_value = user

        client_obj = MagicMock()
        client_obj.id = 42
        # stub update_obj return
        updated = {"id": 42, "name": "X"}
        self.service.repository.update_obj.return_value = updated

        data = {
            "Sales contact": "someone",
            "Phone": "123",
            "Compagny": "Co",
            "Name": "Name",
            "Email address": "e@x.com"
        }
        result = self.service.prepare_data_and_update(data, client_obj, self.session)
        # verify repository.update_obj was called with mapped fields
        self.service.repository.update_obj.assert_called_once_with(
            42,
            {
                "phone": "123",
                "compagny": "Co",
                "name": "Name",
                "email_address": "e@x.com",
                "sales_contact_id": "sales@example.com"
            },
            self.session
        )
        self.assertEqual(result, updated)

    @patch("src.services.client_service.UserService.get_user")
    @patch("src.services.client_service.sentry_sdk.capture_message")
    def test_prepare_data_and_update_no_user(self, mock_capture_message, mock_get_user):
        mock_get_user.return_value = None
        client_obj = MagicMock()
        data = {"Sales contact": "x"}
        with self.assertRaises(ValueError) as cm:
            self.service.prepare_data_and_update(data, client_obj, self.session)
        self.assertIn("Contact Sales not found.", str(cm.exception))
        mock_capture_message.assert_called_once()

    @patch("src.services.client_service.sentry_sdk.capture_message")
    @patch("src.services.client_service.sentry_sdk.capture_exception")
    def test_prepare_data_and_update_generic_exception(self, mock_capture_exc, mock_capture_message):
        # missing keys to force KeyError
        client_obj = MagicMock()
        result = self.service.prepare_data_and_update({}, client_obj, self.session)
        self.assertEqual(result, {})
        mock_capture_message.assert_called_with("Error preparing data and updating client")
        mock_capture_exc.assert_called_once()
