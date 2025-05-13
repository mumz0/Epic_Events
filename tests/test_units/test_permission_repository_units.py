import unittest
from unittest.mock import MagicMock, patch

from src.repositories.permission_repository import PermissionRepository
from src.models.permission import Permission
from src.models.role import Role
from src.models.role_permission import RolePermission

class TestPermissionRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.repo = PermissionRepository()

    def test_get_permissions_by_role_success(self):
        # prepare fake permissions list
        perms = [Permission(action="read"), Permission(action="write")]
        # stub query chain
        q = MagicMock()
        q.join.return_value = q
        q.filter.return_value = q
        q.all.return_value = perms
        self.session.query.return_value = q

        result = self.repo.get_permissions_by_role("admin", self.session)

        # only verify query and return value
        self.session.query.assert_called_once_with(Permission)
        self.assertEqual(result, perms)

    @patch('src.repositories.permission_repository.sentry_sdk.capture_exception')
    @patch('src.repositories.permission_repository.sentry_sdk.capture_message')
    def test_get_permissions_by_role_exception(self, mock_msg, mock_exc):
        # simulate query raising
        self.session.query.side_effect = RuntimeError("db error")
        with self.assertRaises(ValueError) as cm:
            self.repo.get_permissions_by_role("guest", self.session)
        mock_msg.assert_called_once_with("Error retrieving permissions")
        mock_exc.assert_called_once()
        self.assertIn("Error retrieving permissions", str(cm.exception))


if __name__ == '__main__':
    unittest.main()