from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from tests.test_integrations.run_tests import BaseTestDB


class TestIntegrationUserService(BaseTestDB):
    def setUp(self):
        super().setUp()
        self.user_service = UserService()
        self.user_repository = UserRepository()

    def test_find_by_email_user_exists(self):
        user = User(email_address="test@example.com", password="securepassword", role_id="admin")
        self.session.add(user)
        self.session.flush()

        result = self.user_repository.find_by_email("test@example.com", self.session)
        self.assertIsNotNone(result)
        self.assertEqual(result.email_address, "test@example.com")

        self.session.rollback()

    def test_find_by_email_user_does_not_exist(self):
        with self.assertRaises(ValueError) as context:
            self.user_repository.find_by_email("nonexistent@example.com", self.session)
        self.assertIn("User with email nonexistent@example.com not found.", str(context.exception))

    def test_find_by_email_invalid_email(self):
        with self.assertRaises(ValueError) as context:
            self.user_repository.find_by_email("", self.session)
        self.assertIn("Error finding user by email", str(context.exception))

        result = self.user_repository.find_by_email("test@example.com", self.session)
        self.assertIsNotNone(result)
        self.assertEqual(result.email_address, "test@example.com")

        self.session.rollback()

    def test_find_by_email_user_does_not_exist(self):
        with self.assertRaises(ValueError) as context:
            self.user_repository.find_by_email("nonexistent@example.com", self.session)
        self.assertIn("User with email nonexistent@example.com not found.", str(context.exception))

    def test_find_by_email_invalid_email(self):
        with self.assertRaises(ValueError) as context:
            self.user_repository.find_by_email("", self.session)
        self.assertIn("Error finding user by email", str(context.exception))

    def test_update_token_user_exists(self):
        """
        Vérifie que la méthode update_token met à jour le token si le user existe.
        """
        user = User(email_address="tokenuser@example.com", password="password", role_id="user")
        self.session.add(user)
        self.session.flush()

        self.user_repository.update_token(user.id, "NEW_TOKEN_123", self.session)

        updated_user = self.session.query(User).get(user.id)
        self.assertEqual(updated_user.token, "NEW_TOKEN_123")

    def test_update_token_user_not_found(self):
        """
        Vérifie que la méthode update_token lève une ValueError si le user n’existe pas.
        """
        with self.assertRaises(ValueError) as context:
            self.user_repository.update_token(9999, "SHOULD_NOT_WORK", self.session)
        self.assertIn("User with ID 9999 not found.", str(context.exception))

    def test_get_all_excluding_admin(self):
        """
        Vérifie que la méthode get_all retourne les utilisateurs hors administrateur.
        """
        user_regular = User(email_address="user@example.com", password="pass", role_id="2")
        user_admin = User(email_address="admin@example.com", password="pass", role_id="1")
        self.session.add_all([user_regular, user_admin])
        self.session.commit()

        users = self.user_repository.get_all(self.session)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email_address, "user@example.com")

    def tearDown(self):
        self.session.query(User).delete()
        self.session.commit()
        super().tearDown()
