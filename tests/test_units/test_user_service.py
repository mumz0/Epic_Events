import unittest
from unittest.mock import MagicMock, patch

from src.services.user_service import UserService


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.service = UserService()
        self.session = MagicMock()
        # remplacer le repository par un mock
        self.service.repository = MagicMock()

    def test_get_user_success(self):
        expected = MagicMock()
        self.service.repository.find_by_email.return_value = expected

        result = self.service.get_user("user@example.com", self.session)

        self.assertEqual(result, expected)
        self.service.repository.find_by_email.assert_called_once_with("user@example.com", self.session)

    @patch("src.services.user_service.sentry_sdk.capture_exception")
    @patch("src.services.user_service.sentry_sdk.capture_message")
    def test_get_user_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.find_by_email.side_effect = Exception("db fail")

        result = self.service.get_user("x@x.com", self.session)

        self.assertFalse(result)
        mock_capture_message.assert_called_with("Error retrieving user")
        mock_capture_exception.assert_called_once()

    def test_create_user_success(self):
        data = {"email_address": "u@e.com", "password": "pwd", "role_id": "r"}
        expected = MagicMock()
        self.service.repository.add.return_value = expected

        result = self.service.create_user(data, self.session)

        self.assertEqual(result, expected)
        add_args = self.service.repository.add.call_args[0]
        self.assertIsInstance(add_args[0], type(self.service.model(**data)))
        self.assertEqual(add_args[1], self.session)

    @patch("src.services.user_service.sentry_sdk.capture_exception")
    @patch("src.services.user_service.sentry_sdk.capture_message")
    def test_create_user_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.add.side_effect = Exception("db error")
        data = {"email_address": "u@e.com"}

        with self.assertRaises(ValueError) as cm:
            self.service.create_user(data, self.session)
        self.assertEqual(str(cm.exception), "Error creating user")
        mock_capture_message.assert_called_with("Error creating user")
        mock_capture_exception.assert_called_once()

    @patch("src.services.user_service.RoleService")
    def test_prepare_data_and_update_success(self, mock_rs_cls):
        # stub RoleService.get_by_name
        mock_rs = MagicMock()
        mock_role = MagicMock()
        mock_role.name = "roleA"
        mock_rs.get_by_name.return_value = mock_role
        mock_rs_cls.return_value = mock_rs

        obj = MagicMock(id=5)
        updated = MagicMock()
        self.service.repository.update_obj.return_value = updated
        data = {"Role": "roleA", "Email address": "u@e.com"}

        result = self.service.prepare_data_and_update(data, obj, self.session)

        self.assertEqual(result, updated)
        mock_rs.get_by_name.assert_called_once_with("roleA", self.session)
        self.service.repository.update_obj.assert_called_once_with(
            5,
            {"email_address": "u@e.com", "role_id": "roleA"},
            self.session,
        )

    @patch("src.services.user_service.sentry_sdk.capture_message")
    def test_prepare_data_and_update_no_role(self, mock_capture_message):
        with patch("src.services.user_service.RoleService") as mock_rs_cls:
            mock_rs_cls.return_value.get_by_name.return_value = None
            obj = MagicMock(id=6)
            data = {"Role": "unknown"}

            with self.assertRaises(ValueError) as cm:
                self.service.prepare_data_and_update(data, obj, self.session)
            self.assertEqual(str(cm.exception), "Role 'unknown' not found")
            mock_capture_message.assert_called_with("Role 'unknown' not found")

    @patch("src.services.user_service.sentry_sdk.capture_exception")
    @patch("src.services.user_service.sentry_sdk.capture_message")
    def test_prepare_data_and_update_exception(self, mock_capture_message, mock_capture_exception):
        with patch("src.services.user_service.RoleService") as mock_rs_cls:
            mock_rs_cls.return_value.get_by_name.return_value = MagicMock(name="roleB")
            self.service.repository.update_obj.side_effect = Exception("fail")
            obj = MagicMock(id=7)
            data = {"Role": "roleB", "Email address": "x@y.com"}

            with self.assertRaises(ValueError) as cm:
                self.service.prepare_data_and_update(data, obj, self.session)
            self.assertEqual(str(cm.exception), "Error while updating user data")
            mock_capture_message.assert_called_with("Error while updating user data")
            mock_capture_exception.assert_called_once()

    def test_list_to_dict_success(self):
        u1 = MagicMock(id=1)
        u1.to_dict.return_value = {"a": 1}
        u2 = MagicMock(id=2)
        u2.to_dict.return_value = {"b": 2}

        result = self.service.list_to_dict([u1, u2])

        self.assertEqual(result, {1: {"a": 1}, 2: {"b": 2}})

    @patch("src.services.user_service.sentry_sdk.capture_exception")
    @patch("src.services.user_service.sentry_sdk.capture_message")
    def test_list_to_dict_exception(self, mock_capture_message, mock_capture_exception):
        bad = MagicMock()
        bad.to_dict.side_effect = RuntimeError("oops")

        result = self.service.list_to_dict([bad])

        self.assertEqual(result, {})
        mock_capture_message.assert_called_with("Error converting user list to dictionary")
        mock_capture_exception.assert_called_once()

    def test_get_by_email_success(self):
        expected = MagicMock()
        self.service.repository.find_by_email.return_value = expected

        result = self.service.get_by_email("e@mail.com", self.session)

        self.assertEqual(result, expected)
        self.service.repository.find_by_email.assert_called_once_with("e@mail.com", self.session)

    @patch("src.services.user_service.sentry_sdk.capture_exception")
    @patch("src.services.user_service.sentry_sdk.capture_message")
    def test_get_by_email_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.find_by_email.side_effect = Exception("db err")

        result = self.service.get_by_email("f@f.com", self.session)

        self.assertIsNone(result)
        mock_capture_message.assert_called_with("Error retrieving user by email")
        mock_capture_exception.assert_called_once()
