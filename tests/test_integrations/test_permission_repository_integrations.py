import unittest

from src.models.permission import Permission
from src.models.role import Role
from src.models.role_permission import RolePermission
from src.repositories.permission_repository import PermissionRepository
from tests.test_integrations.run_tests import BaseTestDB


class TestPermissionRepositoryIntegration(BaseTestDB):

    def setUp(self):
        super().setUp()
        self.permission_repository = PermissionRepository()

    def test_get_permissions_by_role(self):
        result = self.permission_repository.get_permissions_by_role("admin", self.session)

        self.assertEqual(len(result), 16)
        self.assertTrue(any(p.action == "user_create" for p in result))
        self.assertTrue(any(p.action == "user_read" for p in result))
        self.assertTrue(any(p.action == "user_update" for p in result))
        self.assertTrue(any(p.action == "user_update" for p in result))
        self.assertTrue(any(p.action == "client_create" for p in result))
        self.assertTrue(any(p.action == "client_create" for p in result))
        self.assertTrue(any(p.action == "client_update" for p in result))
        self.assertTrue(any(p.action == "client_update" for p in result))
        self.assertTrue(any(p.action == "contract_create" for p in result))
        self.assertTrue(any(p.action == "contract_read" for p in result))
        self.assertTrue(any(p.action == "contract_update" for p in result))
        self.assertTrue(any(p.action == "contract_delete" for p in result))
        self.assertTrue(any(p.action == "event_create" for p in result))
        self.assertTrue(any(p.action == "event_read" for p in result))
        self.assertTrue(any(p.action == "event_read" for p in result))
        self.assertTrue(any(p.action == "event_delete" for p in result))
