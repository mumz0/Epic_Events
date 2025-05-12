import unittest
from unittest.mock import MagicMock, patch

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.role_service import RoleService
from src.services.user_service import UserService


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()
        self.session_mock = MagicMock()
        self.user_repository_mock = MagicMock(spec=UserRepository)
        self.role_service_mock = MagicMock(spec=RoleService)
        self.user_service.repository = self.user_repository_mock

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_get_user_success(self, mock_capture_exception, mock_capture_message):
        email = "test@example.com"
        user = User(id=1, email_address=email)
        self.user_repository_mock.find_by_email.return_value = user

        result = self.user_service.get_user(email, self.session_mock)

        self.assertEqual(result, user)
        self.user_repository_mock.find_by_email.assert_called_once_with(email, self.session_mock)
        mock_capture_message.assert_not_called()
        mock_capture_exception.assert_not_called()

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_get_user_failure(self, mock_capture_exception, mock_capture_message):
        email = "test@example.com"
        self.user_repository_mock.find_by_email.side_effect = Exception("Database error")

        result = self.user_service.get_user(email, self.session_mock)

        self.assertFalse(result)
        mock_capture_message.assert_called_once_with("Error retrieving user")
        mock_capture_exception.assert_called_once()

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_create_user_success(self, mock_capture_exception, mock_capture_message):
        data = {"email_address": "test@example.com"}
        user = User(**data)
        self.user_repository_mock.add.return_value = user

        result = self.user_service.create_user(data, self.session_mock)

        self.assertEqual(result, user)
        self.user_repository_mock.add.assert_called_once()
        mock_capture_message.assert_not_called()
        mock_capture_exception.assert_not_called()

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_create_user_failure(self, mock_capture_exception, mock_capture_message):
        data = {"email_address": "test@example.com"}
        self.user_repository_mock.add.side_effect = Exception("Database error")

        with self.assertRaises(ValueError):
            self.user_service.create_user(data, self.session_mock)

        mock_capture_message.assert_called_once_with("Error creating user")
        mock_capture_exception.assert_called_once()

    @patch("src.services.role_service.RoleService.get_by_name")
    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_prepare_data_and_update_success(self, mock_capture_exception, mock_capture_message, mock_get_by_name):
        data = {"Email address": "updated@example.com", "Role": "Admin"}
        user = User(id=1, email_address="old@example.com")
        role = MagicMock(name="Admin")
        mock_get_by_name.return_value = role

        self.user_service.prepare_data_and_update(data, user, self.session_mock)

        self.user_repository_mock.update_obj.assert_called_once_with(
            user.id, {"email_address": "updated@example.com", "role_id": role.name}, self.session_mock
        )
        mock_capture_message.assert_not_called()
        mock_capture_exception.assert_not_called()

    @patch("src.services.role_service.RoleService.get_by_name")
    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_prepare_data_and_update_role_not_found(self, mock_capture_exception, mock_capture_message, mock_get_by_name):

        data = {"Email address": "updated@example.com", "Role": "NonExistentRole"}
        user = User(id=1, email_address="old@example.com")
        mock_get_by_name.return_value = None

        with self.assertRaises(ValueError):
            self.user_service.prepare_data_and_update(data, user, self.session_mock)

        mock_capture_message.assert_called_once_with("Role 'NonExistentRole' not found")
        mock_capture_exception.assert_not_called()

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_list_to_dict_success(self, mock_capture_exception, mock_capture_message):
        user1 = MagicMock(id=1, to_dict=MagicMock(return_value={"id": 1, "email": "user1@example.com"}))
        user2 = MagicMock(id=2, to_dict=MagicMock(return_value={"id": 2, "email": "user2@example.com"}))
        user_list = [user1, user2]

        result = self.user_service.list_to_dict(user_list)

        self.assertEqual(result, {1: {"id": 1, "email": "user1@example.com"}, 2: {"id": 2, "email": "user2@example.com"}})
        mock_capture_message.assert_not_called()
        mock_capture_exception.assert_not_called()

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_list_to_dict_failure(self, mock_capture_exception, mock_capture_message):
        user_list = [MagicMock(id=1, to_dict=MagicMock(side_effect=Exception("Error")))]

        result = self.user_service.list_to_dict(user_list)

        self.assertEqual(result, {})
        mock_capture_message.assert_called_once_with("Error converting user list to dictionary")
        mock_capture_exception.assert_called_once()

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_get_by_email_success(self, mock_capture_exception, mock_capture_message):
        email = "test@example.com"
        user = User(id=1, email_address=email)
        self.user_repository_mock.find_by_email.return_value = user

        result = self.user_service.get_by_email(email, self.session_mock)

        self.assertEqual(result, user)
        self.user_repository_mock.find_by_email.assert_called_once_with(email, self.session_mock)
        mock_capture_message.assert_not_called()
        mock_capture_exception.assert_not_called()

    @patch("sentry_sdk.capture_message")
    @patch("sentry_sdk.capture_exception")
    def test_get_by_email_failure(self, mock_capture_exception, mock_capture_message):
        email = "test@example.com"
        self.user_repository_mock.find_by_email.side_effect = Exception("Database error")

        result = self.user_service.get_by_email(email, self.session_mock)

        self.assertIsNone(result)
        mock_capture_message.assert_called_once_with("Error retrieving user by email")
        mock_capture_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()
