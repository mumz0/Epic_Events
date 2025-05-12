from src.models.user import User
from src.repositories.base_repository import BaseRepository
from tests.test_integrations.run_tests import BaseTestDB


class TestBaseRepositoryIntegration(BaseTestDB):

    def setUp(self):
        super().setUp()
        self.repository = BaseRepository(User)

        self.user1 = User(email_address="user1@example.com", password="password1", role_id="admin")
        self.user2 = User(email_address="user2@example.com", password="password2", role_id="sales")
        self.session.add_all([self.user1, self.user2])
        self.session.flush()

    def test_add(self):
        new_user = User(email_address="new_user@example.com", password="password3", role_id="support")
        added_user = self.repository.add(new_user, self.session)

        self.assertIsNotNone(added_user.id)
        self.assertEqual(added_user.email_address, "new_user@example.com")

    def test_get(self):
        retrieved_user = self.repository.get(self.user1.id, self.session)

        self.assertEqual(retrieved_user.email_address, "user1@example.com")

    def test_get_all(self):
        users = self.repository.get_all(self.session)

        self.assertEqual(len(users), 2)
        self.assertIn(self.user1, users)
        self.assertIn(self.user2, users)

    def test_update_obj(self):
        updated_data = {"email_address": "updated_user1@example.com"}
        updated_user = self.repository.update_obj(self.user1.id, updated_data, self.session)

        self.assertEqual(updated_user.email_address, "updated_user1@example.com")

    def test_delete(self):
        deleted_user = self.repository.delete(self.user1.id, self.session)

        self.assertEqual(deleted_user.email_address, "user1@example.com")
        remaining_users = self.repository.get_all(self.session)
        self.assertEqual(len(remaining_users), 1)

    def test_update_attr(self):
        updated_user = self.repository.update_attr(self.user1.id, "email_address", "new_email@example.com", self.session)

        self.assertEqual(updated_user.email_address, "new_email@example.com")

    def always_fail_query(self, *args, **kwargs):
        raise Exception("Test induced error")

    def test_get_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.repository.get(self.user1.id, self.session)
        self.assertIn("Error retrieving instance by ID", str(context.exception))
        self.session.query = original_query

    def test_get_id_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.repository.get_id("user1@example.com", self.session)
        self.assertIn("Error retrieving instance by name", str(context.exception))
        self.session.query = original_query

    def test_get_all_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.repository.get_all(self.session)
        self.assertIn("Error retrieving all instances", str(context.exception))
        self.session.query = original_query

    def test_update_obj_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        updated_data = {"email_address": "fail_update@example.com"}
        with self.assertRaises(ValueError) as context:
            self.repository.update_obj(self.user1.id, updated_data, self.session)
        self.assertIn("Error updating instance", str(context.exception))
        self.session.query = original_query

    def test_update_attr_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.repository.update_attr(self.user1.id, "email_address", "fail_attr@example.com", self.session)
        self.assertIn("Error updating attribute", str(context.exception))
        self.session.query = original_query

    def test_delete_exception(self):
        original_query = self.session.query
        self.session.query = self.always_fail_query
        with self.assertRaises(ValueError) as context:
            self.repository.delete(self.user1.id, self.session)
        self.assertIn("Error deleting instance", str(context.exception))
        self.session.query = original_query

    def tearDown(self):
        self.session.query(User).delete()
        self.session.commit()
        super().tearDown()
