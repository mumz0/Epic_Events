import unittest
from unittest.mock import MagicMock, patch

from src.repositories.role_repository import RoleRepository
from src.models.role import Role

class TestRoleRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.repo = RoleRepository()

    def test_get_all_success(self):
        # prepare fake roles excluding admin
        roles = ["role1", "role2"]
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = roles
        self.session.query.return_value = q

        result = self.repo.get_all(self.session)

        # verify query was called and filter invoked once with correct expression
        self.session.query.assert_called_once_with(Role)
        self.assertEqual(q.filter.call_count, 1)
        expr = q.filter.call_args[0][0]
        self.assertEqual(str(expr), str(Role.name != "admin"))
        self.assertEqual(result, roles)

    @patch('src.repositories.role_repository.sentry_sdk.capture_exception')
    def test_get_all_exception(self, mock_exc):
        # simulate database error
        self.session.query.side_effect = RuntimeError("db error")
        with self.assertRaises(ValueError) as cm:
            self.repo.get_all(self.session)
        mock_exc.assert_called_once()
        self.assertIn("Error retrieving all roles except 'admin'", str(cm.exception))

    def test_get_by_name_success(self):
        # prepare a matching role
        role_obj = Role(name="support")
        q = MagicMock()
        q.filter_by.return_value = q
        q.first.return_value = role_obj
        self.session.query.return_value = q

        result = self.repo.get_by_name("support", self.session)
        self.session.query.assert_called_once_with(Role)
        q.filter_by.assert_called_once_with(name="support")
        self.assertIs(result, role_obj)

    @patch('src.repositories.role_repository.sentry_sdk.capture_message')
    def test_get_by_name_not_found(self, mock_msg):
        # first() returns None → not found
        q = MagicMock()
        q.filter_by.return_value = q
        q.first.return_value = None
        self.session.query.return_value = q

        with self.assertRaises(ValueError) as cm:
            self.repo.get_by_name("ghost", self.session)
        mock_msg.assert_called_once_with("Role with name ghost not found.")
        self.assertIn("Role with name ghost not found.", str(cm.exception))

    @patch('src.repositories.role_repository.sentry_sdk.capture_exception')
    def test_get_by_name_exception(self, mock_exc):
        # simulate filter_by or first raising
        q = MagicMock()
        q.filter_by.side_effect = Exception("fail")
        self.session.query.return_value = q

        with self.assertRaises(ValueError) as cm:
            self.repo.get_by_name("any", self.session)
        mock_exc.assert_called_once()
        self.assertIn("Error retrieving role by name:", str(cm.exception))