from src.repositories.role_repository import RoleRepository
from tests.test_integrations.run_tests import BaseTestDB


class TestIntegrationUserService(BaseTestDB):
    def setUp(self):
        super().setUp()
        self.role_repository = RoleRepository()

    def test_get_all_excludes_admin(self):
        roles = self.role_repository.get_all(self.session)

        self.assertEqual(len(roles), 3)
        role_names = [role.name for role in roles]
        self.assertNotIn("admin", role_names)
        self.assertIn("sales", role_names)
        self.assertIn("support", role_names)
        self.assertIn("management", role_names)

    def test_get_by_name_success(self):
        role = self.role_repository.get_by_name("sales", self.session)

        self.assertIsNotNone(role)
        self.assertEqual(role.name, "sales")

    def test_get_by_name_not_found(self):
        with self.assertRaises(ValueError) as context:
            self.role_repository.get_by_name("nonexistent", self.session)

        self.assertIn("Role with name nonexistent not found.", str(context.exception))
