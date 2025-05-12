import unittest
from unittest.mock import MagicMock, patch

from src.models.client import Client
from src.repositories.client_repository import ClientRepository
from src.services.client_service import ClientService
from src.services.user_service import UserService


class TestClientService(unittest.TestCase):

    def setUp(self):
        self.client_service = ClientService()
        self.mock_session = MagicMock()

    def test_list_to_dict(self):
        client1 = MagicMock(spec=Client)
        client1.id = 1
        client1.to_dict.return_value = {"id": 1, "name": "Client 1"}

        client2 = MagicMock(spec=Client)
        client2.id = 2
        client2.to_dict.return_value = {"id": 2, "name": "Client 2"}

        client_list = [client1, client2]
        expected_dict = {1: {"id": 1, "name": "Client 1"}, 2: {"id": 2, "name": "Client 2"}}

        result = self.client_service.list_to_dict(client_list)
        self.assertEqual(result, expected_dict)

    @patch.object(UserService, "get_user")
    @patch.object(ClientRepository, "update_obj")
    def test_prepare_data_and_update(self, mock_update_obj, mock_get_user):
        data = {
            "Sales contact": "sales@example.com",
            "Phone": "1234567890",
            "Compagny": "Example Inc.",
            "Name": "John Doe",
            "Email address": "john.doe@example.com",
        }

        user = MagicMock()
        user.email_address = "sales@example.com"
        mock_get_user.return_value = user

        obj = MagicMock()
        obj.id = 1

        expected_data = {
            "phone": "1234567890",
            "compagny": "Example Inc.",
            "name": "John Doe",
            "email_address": "john.doe@example.com",
            "sales_contact_id": "sales@example.com",
        }

        self.client_service.prepare_data_and_update(data, obj, self.mock_session)
        mock_update_obj.assert_called_once_with(obj.id, expected_data, self.mock_session)

    @patch.object(UserService, "get_user")
    def test_prepare_data_and_update_user_not_found(self, mock_get_user):
        data = {
            "Sales contact": "sales@example.com",
            "Phone": "1234567890",
            "Compagny": "Example Inc.",
            "Name": "John Doe",
            "Email address": "john.doe@example.com",
        }

        mock_get_user.return_value = None

        obj = MagicMock()
        obj.id = 1

        with self.assertRaises(ValueError) as context:
            self.client_service.prepare_data_and_update(data, obj, self.mock_session)

        self.assertEqual(str(context.exception), "Contact Sales not found.")
