import unittest
from unittest.mock import MagicMock, patch

import jwt
from cryptography.fernet import Fernet

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.permission_service import PermissionService
from src.services.user_service import UserService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock(spec=User)
        self.mock_user.role.name = "admin"
        self.auth_service = AuthService(current_user=self.mock_user)
        self.mock_session = MagicMock()
        self.auth_service.repository = MagicMock()

    @patch("src.services.auth_service.PermissionService.get_permissions")
    def test_check_permission_signup_success(self, mock_get_permissions):
        mock_get_permissions.return_value = [MagicMock(action="create", entity="user")]

        result = self.auth_service.check_permission_signup(self.mock_session)

        self.assertTrue(result)
        mock_get_permissions.assert_called_once_with("admin", self.mock_session)

    @patch("src.services.auth_service.PermissionService.get_permissions")
    @patch("sentry_sdk.capture_exception")
    def test_check_permission_signup_fail(self, mock_capture_exception, mock_get_permissions):
        mock_get_permissions.side_effect = Exception("Error")

        result = self.auth_service.check_permission_signup(self.mock_session)

        self.assertFalse(result)
        mock_capture_exception.assert_called_once()

    @patch("src.services.auth_service.BaseService.create")
    @patch("src.services.auth_service.User")
    def test_signup_process_success(self, mock_user_model, mock_create):
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None

        mock_create.return_value = MagicMock(spec=User)

        result = self.auth_service.signup_process(email="test@example.com", password="password", role="admin", session=self.mock_session)

        self.assertTrue(result)
        mock_create.assert_called_once()

    @patch("src.services.auth_service.BaseService.create")
    @patch("sentry_sdk.capture_exception")
    def test_signup_process_fail(self, mock_capture_exception, mock_create):
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None

        mock_create.side_effect = Exception("Error")

        result = self.auth_service.signup_process(email="test@example.com", password="password", role="admin", session=self.mock_session)

        self.assertFalse(result)
        mock_capture_exception.assert_called_once()
        mock_create.assert_called_once()

    @patch("src.services.auth_service.UserService.get_user")
    @patch("src.services.auth_service.argon2.verify")
    def test_signin_process_success(self, mock_verify, mock_get_user):
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.token = None
        mock_get_user.return_value = mock_user
        mock_verify.return_value = True

        result = self.auth_service.signin_process(email="test@example.com", password="password", session=self.mock_session)

        self.assertEqual(result, mock_user)
        mock_get_user.assert_called_once_with("test@example.com", self.mock_session)
        mock_verify.assert_called_once()

    @patch("src.services.auth_service.UserService.get_user")
    @patch("src.services.auth_service.argon2.verify")
    @patch("sentry_sdk.capture_exception")
    def test_signin_process_fail(self, mock_capture_exception, mock_verify, mock_get_user):
        mock_get_user.side_effect = Exception("Error")

        result = self.auth_service.signin_process(email="test@example.com", password="password", session=self.mock_session)

        self.assertIsNone(result)
        mock_capture_exception.assert_called_once()

    @patch("src.services.auth_service.os.getenv")
    @patch("src.services.auth_service.Fernet")
    def test_encrypt_and_store_token_success(self, mock_fernet, mock_getenv):
        mock_getenv.return_value = Fernet.generate_key().decode()
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.encrypt.return_value = b"encrypted_token"

        self.auth_service.encrypt_and_store_token(token="test_token", user_id=1, session=self.mock_session)

        mock_fernet_instance.encrypt.assert_called_once_with(b"test_token")
        self.auth_service.repository.update_attr.assert_called_once_with(1, "token", "encrypted_token", self.mock_session)

    @patch("src.services.auth_service.Fernet.encrypt")
    @patch("sentry_sdk.capture_exception")
    def test_encrypt_and_store_token_fail(self, mock_capture_exception, mock_encrypt):
        mock_encrypt.side_effect = Exception("Error")

        self.auth_service.encrypt_and_store_token(token="test_token", user_id=1, session=self.mock_session)

        mock_capture_exception.assert_called_once()

    @patch("src.services.auth_service.jwt.encode")
    def test_generate_token_success(self, mock_jwt_encode):
        mock_jwt_encode.return_value = "test_token"

        result = self.auth_service.generate_token(data={"user_id": 1})

        self.assertEqual(result, "test_token")
        mock_jwt_encode.assert_called_once()

    @patch("src.services.auth_service.jwt.encode")
    @patch("sentry_sdk.capture_exception")
    def test_generate_token_fail(self, mock_capture_exception, mock_jwt_encode):
        mock_jwt_encode.side_effect = Exception("Error")

        result = self.auth_service.generate_token(data={"user_id": 1})

        self.assertIsNone(result)
        mock_capture_exception.assert_called_once()
