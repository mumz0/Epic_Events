import unittest
from unittest.mock import MagicMock, patch

from src.controllers.permission_controller import PermissionController
from src.services.permission_service import PermissionService


class TestPermissionController(unittest.TestCase):
    @patch("os.getenv", return_value="create,read,update,delete")
    @patch.object(PermissionService, "create_instance", side_effect=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
    def test_create_permissions(self, mock_create_instance, mock_getenv):
        controller = PermissionController()
        result = controller.create_permissions()

        mock_getenv.assert_called_once_with("PERMISSIONS")
        self.assertEqual(mock_create_instance.call_count, 4)
        self.assertEqual(len(result), 4)
