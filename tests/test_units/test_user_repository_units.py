import unittest
from unittest.mock import MagicMock, patch

from src.repositories.user_repository import UserRepository
from src.models.user import User

class TestUserRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.repo = UserRepository()

    def test_init_sets_model(self):
        self.assertIs(self.repo.model, User)

    def test_find_by_email_success(self):
        user = User(email_address="u@e.com")
        q = MagicMock()
        q.filter.return_value.first.return_value = user
        self.session.query.return_value = q

        result = self.repo.find_by_email("u@e.com", self.session)
        self.session.query.assert_called_once_with(User)
        q.filter.assert_called_once()
        self.assertIs(result, user)

    @patch('src.repositories.user_repository.sentry_sdk.capture_message')
    def test_find_by_email_not_found(self, mock_msg):
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        self.session.query.return_value = q

        with self.assertRaises(ValueError) as cm:
            self.repo.find_by_email("no@one.com", self.session)
        mock_msg.assert_called_once_with("User with email no@one.com not found.")
        self.assertIn("User with email no@one.com not found.", str(cm.exception))

    @patch('src.repositories.user_repository.sentry_sdk.capture_exception')
    def test_find_by_email_exception(self, mock_exc):
        self.session.query.side_effect = RuntimeError("fail")
        with self.assertRaises(ValueError) as cm:
            self.repo.find_by_email("x", self.session)
        mock_exc.assert_called_once()
        self.assertIn("Error finding user by email: fail", str(cm.exception))

    def test_update_token_success(self):
        user = MagicMock(token=None)
        q = MagicMock()
        q.get.return_value = user
        self.session.query.return_value = q

        self.repo.update_token(42, "TOKEN", self.session)
        self.session.query.assert_called_once_with(User)
        q.get.assert_called_once_with(42)
        self.assertEqual(user.token, "TOKEN")
        self.session.commit.assert_called_once()

    @patch('src.repositories.user_repository.sentry_sdk.capture_message')
    def test_update_token_not_found(self, mock_msg):
        q = MagicMock(get=MagicMock(return_value=None))
        self.session.query.return_value = q

        with self.assertRaises(ValueError) as cm:
            self.repo.update_token(99, "T", self.session)
        mock_msg.assert_called_once_with("User with ID 99 not found.")
        self.assertIn("User with ID 99 not found.", str(cm.exception))

    @patch('src.repositories.user_repository.sentry_sdk.capture_exception')
    def test_update_token_exception(self, mock_exc):
        q = MagicMock()
        q.get.side_effect = Exception("oops")
        self.session.query.return_value = q

        with self.assertRaises(ValueError) as cm:
            self.repo.update_token(1, "T", self.session)
        mock_exc.assert_called_once()
        self.assertIn("Error updating token for user ID 1: oops", str(cm.exception))

    def test_get_all_success(self):
        users = [User(email_address="a@e.com"), User(email_address="b@e.com")]
        q = MagicMock()
        q.filter.return_value.all.return_value = users
        self.session.query.return_value = q

        result = self.repo.get_all(self.session)
        self.session.query.assert_called_once_with(User)
        q.filter.assert_called_once()
        self.assertEqual(result, users)

    @patch('src.repositories.user_repository.sentry_sdk.capture_exception')
    def test_get_all_exception(self, mock_exc):
        self.session.query.side_effect = RuntimeError("db err")
        with self.assertRaises(ValueError) as cm:
            self.repo.get_all(self.session)
        mock_exc.assert_called_once()
        self.assertIn("Error retrieving all users except admin: db err", str(cm.exception))
