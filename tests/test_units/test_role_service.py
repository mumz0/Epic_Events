import unittest
from unittest.mock import MagicMock, patch

from src.services.role_service import RoleService


class TestRoleService(unittest.TestCase):
    def setUp(self):
        self.service = RoleService()
        self.session = MagicMock()
        # inject a fake repository
        self.service.repository = MagicMock()

    def test_get_all_success(self):
        expected = [MagicMock(), MagicMock()]
        self.service.repository.get_all.return_value = expected

        result = self.service.get_all(self.session)

        self.assertEqual(result, expected)
        self.service.repository.get_all.assert_called_once_with(self.session)

    @patch("src.services.role_service.sentry_sdk.capture_exception")
    @patch("src.services.role_service.sentry_sdk.capture_message")
    def test_get_all_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.get_all.side_effect = Exception("db error")

        result = self.service.get_all(self.session)

        self.assertEqual(result, [])
        mock_capture_message.assert_called_with("Error retrieving all roles")
        mock_capture_exception.assert_called_once()

    def test_get_by_name_success(self):
        expected = MagicMock()
        self.service.repository.get_by_name.return_value = expected

        result = self.service.get_by_name("admin", self.session)

        self.assertEqual(result, expected)
        self.service.repository.get_by_name.assert_called_once_with("admin", self.session)

    @patch("src.services.role_service.sentry_sdk.capture_exception")
    @patch("src.services.role_service.sentry_sdk.capture_message")
    def test_get_by_name_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.get_by_name.side_effect = Exception("db error")

        result = self.service.get_by_name("user", self.session)

        self.assertIsNone(result)
        mock_capture_message.assert_called_with("Error retrieving role by name")
        mock_capture_exception.assert_called_once()