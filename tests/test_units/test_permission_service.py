import unittest
from unittest.mock import MagicMock, patch

from src.repositories.permission_repository import PermissionRepository
from src.services.permission_service import PermissionService


class TestPermissionService(unittest.TestCase):
    def setUp(self):
        # Mock the PermissionRepository
        self.mock_repository = MagicMock(spec=PermissionRepository)
        # Patch the PermissionRepository to return the mock
        patcher = patch("src.services.permission_service.PermissionRepository", return_value=self.mock_repository)
        self.addCleanup(patcher.stop)
        patcher.start()

        # Initialize the PermissionService
        self.permission_service = PermissionService()

    def test_get_permissions_success(self):
        # Arrange
        mock_session = MagicMock()
        user_role_name = "admin"
        expected_permissions = ["user_read", "user_write", "user_delete"]
        self.mock_repository.get_permissions_by_role.return_value = expected_permissions

        # Act
        result = self.permission_service.get_permissions(user_role_name, mock_session)

        # Assert
        self.mock_repository.get_permissions_by_role.assert_called_once_with(user_role_name, mock_session)
        self.assertEqual(result, expected_permissions)

    @patch("sentry_sdk.capture_exception")
    def test_get_permissions_exception(self, mock_capture_exception):
        # Arrange
        mock_session = MagicMock()
        user_role_name = "admin"
        self.mock_repository.get_permissions_by_role.side_effect = Exception("Database error")

        # Act
        result = self.permission_service.get_permissions(user_role_name, mock_session)

        # Assert
        self.mock_repository.get_permissions_by_role.assert_called_once_with(user_role_name, mock_session)
        mock_capture_exception.assert_called_once()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
