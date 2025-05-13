import unittest
from unittest.mock import MagicMock, patch

from src.services.permission_service import PermissionService


class TestPermissionService(unittest.TestCase):
    def setUp(self):
        self.service = PermissionService()
        self.session = MagicMock()
        # replace real repository with a mock
        self.service.repository = MagicMock()

    def test_get_permissions_success(self):
        expected = ["perm_read", "perm_write"]
        self.service.repository.get_permissions_by_role.return_value = expected

        result = self.service.get_permissions("admin", self.session)

        self.assertEqual(result, expected)
        self.service.repository.get_permissions_by_role.assert_called_once_with("admin", self.session)

    @patch("src.services.permission_service.sentry_sdk.capture_exception")
    @patch("src.services.permission_service.sentry_sdk.capture_message")
    def test_get_permissions_exception(self, mock_capture_message, mock_capture_exception):
        self.service.repository.get_permissions_by_role.side_effect = Exception("db error")

        result = self.service.get_permissions("user", self.session)

        self.assertEqual(result, [])
        mock_capture_message.assert_called_with("Error retrieving permissions for role")
        mock_capture_exception.assert_called_once()