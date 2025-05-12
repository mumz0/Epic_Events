import unittest
from unittest.mock import MagicMock, patch

from src.models.role import Role
from src.services.role_service import RoleService


class TestRoleService(unittest.TestCase):
    def setUp(self):
        self.role_service = RoleService()
        self.mock_session = MagicMock()

    @patch("src.repositories.role_repository.RoleRepository.get_all")
    def test_get_all_success(self, mock_get_all):
        # Arrange
        mock_roles = [Role(name="sales"), Role(name="support")]
        mock_get_all.return_value = mock_roles

        # Act
        result = self.role_service.get_all(self.mock_session)

        # Assert
        self.assertEqual(result, mock_roles)
        mock_get_all.assert_called_once_with(self.mock_session)

    @patch("src.repositories.role_repository.RoleRepository.get_all")
    @patch("sentry_sdk.capture_exception")
    def test_get_all_exception(self, mock_capture_exception, mock_get_all):
        # Arrange
        mock_get_all.side_effect = Exception("Database error")

        # Act
        result = self.role_service.get_all(self.mock_session)

        # Assert
        self.assertEqual(result, [])
        mock_capture_exception.assert_called_once()
        mock_get_all.assert_called_once_with(self.mock_session)

    @patch("src.repositories.role_repository.RoleRepository.get_by_name")
    def test_get_by_name_success(self, mock_get_by_name):
        # Arrange
        mock_role = Role(name="sales")
        mock_get_by_name.return_value = mock_role

        # Act
        result = self.role_service.get_by_name("Admin", self.mock_session)

        # Assert
        self.assertEqual(result, mock_role)
        mock_get_by_name.assert_called_once_with("Admin", self.mock_session)

    @patch("src.repositories.role_repository.RoleRepository.get_by_name")
    @patch("sentry_sdk.capture_exception")
    def test_get_by_name_exception(self, mock_capture_exception, mock_get_by_name):
        # Arrange
        mock_get_by_name.side_effect = Exception("Database error")

        # Act
        result = self.role_service.get_by_name("Admin", self.mock_session)

        # Assert
        self.assertIsNone(result)
        mock_capture_exception.assert_called_once()
        mock_get_by_name.assert_called_once_with("Admin", self.mock_session)
