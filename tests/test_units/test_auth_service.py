import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
from cryptography.fernet import Fernet
from passlib.hash import argon2

from src.models.user import User
from src.services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        # Préparer un session factice et un AuthService
        self.session = MagicMock()
        os.environ.pop("ENCRYPTION_KEY", None)
        os.environ.pop("ENCRYPTED_TOKEN", None)
        self.auth = AuthService(current_user=None)

    def test_signup_process_no_role(self):
        result = self.auth.signup_process(email="a@b.com", password="pwd", role=None, session=self.session)
        self.assertFalse(result)

    def test_signup_process_existing_user(self):
        self.session.query().filter_by().first.return_value = User(email_address="x", password="p", role_id="r")
        result = self.auth.signup_process("x", "p", "r", self.session)
        self.assertTrue(result)

    @patch("src.services.auth_service.BaseService.create")
    def test_signup_process_create_success(self, mock_create):
        mock_create.return_value = User(email_address="n", password="h", role_id="r")
        # s'assurer qu'il n'y a pas d'utilisateur existant
        self.session.query().filter_by().first.return_value = None
        result = self.auth.signup_process("n", "p", "r", self.session)
        self.assertTrue(result)
        mock_create.assert_called_once()

    @patch("src.services.auth_service.BaseService.create")
    def test_signup_process_create_fail(self, mock_create):
        mock_create.return_value = None
        # s'assurer qu'il n'y a pas d'utilisateur existant
        self.session.query().filter_by().first.return_value = None
        result = self.auth.signup_process("n", "p", "r", self.session)
        self.assertFalse(result)

    def test_load_or_generate_key_new(self):
        key = self.auth.load_or_generate_key()
        self.assertIsNotNone(key)
        self.assertEqual(os.getenv("ENCRYPTION_KEY"), key)

    def test_generate_and_verify_token(self):
        os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        payload = {"foo": "bar"}
        token = self.auth.generate_token(payload, expiration=1)
        decoded = self.auth.verify_token(Fernet(os.getenv("ENCRYPTION_KEY")).encrypt(token.encode()).decode())
        self.assertIn("foo", decoded)

    def test_encrypt_and_store_token_calls_update(self):
        os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        dummy_token = "tok"
        self.auth.repository = MagicMock()
        self.auth.encrypt_and_store_token(dummy_token, user_id=123, session=self.session)
        self.auth.repository.update_attr.assert_called_with(123, "token", unittest.mock.ANY, self.session)

    def test_load_and_decrypt_token(self):
        os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        token = "hello"
        encrypted = Fernet(os.getenv("ENCRYPTION_KEY")).encrypt(token.encode()).decode()
        os.environ["ENCRYPTED_TOKEN"] = encrypted
        out = self.auth.load_and_decrypt_token()
        self.assertEqual(out, token)

    @patch("src.services.auth_service.UserService.get_user")
    def test_signin_process_user_not_found(self, mock_get_user):
        mock_get_user.return_value = None
        out = self.auth.signin_process("e", "p", self.session)
        self.assertIsNone(out)

    @patch("src.services.auth_service.UserService.get_user")
    def test_signin_process_invalid_password(self, mock_get_user):
        u = User(email_address="e", password=argon2.hash("right"), role_id="r")
        mock_get_user.return_value = u
        out = self.auth.signin_process("e", "wrong", self.session)
        self.assertIsNone(out)

    @patch("src.services.auth_service.UserService.get_user")
    def test_signin_process_valid(self, mock_get_user):
        # setup user without token
        u = User(email_address="e", password=argon2.hash("pwd"), role_id="r")
        u.id = 1
        u.token = None
        mock_get_user.return_value = u

        # stub methods de génération
        with patch.object(self.auth, "_generate_and_store_token") as gen, \
             patch.object(self.auth, "verify_token", return_value={"user_id": 1}):
            out = self.auth.signin_process("e", "pwd", self.session)
            self.assertIsNotNone(out)
            gen.assert_called()

    def test_revoke_token(self):
        self.auth.current_user = User(email_address="e", password="p", role_id="r")
        self.auth.current_user.id = 42
        self.auth.repository = MagicMock()
        self.auth.revoke_token(self.session)
        self.auth.repository.update_attr.assert_called_with(42, "token", None, self.session)
