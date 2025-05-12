import unittest
from unittest.mock import MagicMock, patch

from src.models.role import Role
from src.repositories.role_repository import RoleRepository
from src.services.role_service import RoleService


class TestRoleService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.service = RoleService()
        self.mock_repository = MagicMock(spec=RoleRepository)
        self.service.repository = self.mock_repository

    def test_get_all_success(self):
        self.mock_repository.get_all.return_value = [MagicMock(spec=Role)]
        result = self.service.get_all(self.mock_session)
        self.mock_repository.get_all.assert_called_once_with(self.mock_session)
        self.assertTrue(len(result), 1)

    @patch("src.services.role_service.sentry_sdk.capture_exception")
    @patch("src.services.role_service.sentry_sdk.capture_message")
    def test_get_all_exception(self, mock_capture_message, mock_capture_exception):
        self.mock_repository.get_all.side_effect = Exception("Error retrieving roles")
        result = self.service.get_all(self.mock_session)
        mock_capture_message.assert_called_once_with("Error retrieving all roles")
        mock_capture_exception.assert_called_once()
        self.assertEqual(result, [])

    def test_get_by_name_success(self):
        self.mock_repository.get_by_name.return_value = MagicMock(spec=Role)
        result = self.service.get_by_name("Admin", self.mock_session)
        self.mock_repository.get_by_name.assert_called_once_with("Admin", self.mock_session)
        self.assertIsNotNone(result)

    @patch("src.services.role_service.sentry_sdk.capture_exception")
    @patch("src.services.role_service.sentry_sdk.capture_message")
    def test_get_by_name_exception(self, mock_capture_message, mock_capture_exception):
        self.mock_repository.get_by_name.side_effect = Exception("Error retrieving role by name")
        result = self.service.get_by_name("Admin", self.mock_session)
        mock_capture_message.assert_called_once_with("Error retrieving role by name")
        mock_capture_exception.assert_called_once()
        self.assertIsNone(result)
