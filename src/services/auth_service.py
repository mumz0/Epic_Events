"""
This module contains the AuthService class, which provides authentication services.
"""

import os
from datetime import datetime, timedelta

import jwt
import sentry_sdk
from cryptography.fernet import Fernet
from passlib.hash import argon2

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.base_service import BaseService
from src.services.user_service import UserService


class AuthService(BaseService):
    """
    AuthService provides methods for user authentication and authorization.

    :param BaseService: Inherits from BaseService.
    :type BaseService: BaseService
    """

    def __init__(self, current_user):
        super().__init__(User, UserRepository())
        self.current_user = current_user
        
    def signup_process(self, email: str, password: str, role: str, session):
        """
        Handles the signup process for a new user.

        :param email: The user's email address.
        :type email: str
        :param password: The user's password.
        :type password: str
        :param role: The user's role.
        :type role: str
        :param session: The database session.
        :type session: Session
        :return: The created user or None if creation fails.
        :rtype: User or None
        """
        try:
            if role is None:
                raise Exception()
            existing_user = session.query(User).filter_by(email_address=email).first()
            if existing_user:
                return True

            user_data = {"email_address": email, "password": argon2.hash(password), "role_id": role}
            user = BaseService(User).create(user_data, session)
            if user:
                return True
            return False

        except Exception as e:
            error_message = "Error during signup process"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)
            return False

    def signin_process(self, email: str, password: str, session):
        """
        Authenticates a user by their email and password.

        :param email: The user's email address.
        :type email: str
        :param password: The user's password.
        :type password: str
        :param session: The database session.
        :type session: Session
        :return: The authenticated user or None if authentication fails.
        :rtype: User or None
        """
        try:
            user = UserService().get_user(email, session)
            if not user:
                sentry_sdk.capture_message("User not found")
                return None
            if not argon2.verify(password, user.password):
                sentry_sdk.capture_message("Invalid password")
                return None

            self.current_user = user
            data = {"user_id": user.id}

            # Check if the token exists; otherwise, generate a new token
            if not user.token:
                self._generate_and_store_token(data, user.id, session)
                user = session.query(User).get(user.id)
                self.current_user = user

            # Verify the token (decrypting + decoding JWT)
            try:
                payload = self.verify_token(user.token)
                if not payload:
                    raise jwt.InvalidTokenError("Token verification failed")
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                sentry_sdk.capture_exception(e)
                sentry_sdk.capture_message("Token expired or invalid, regenerating token")
                self._generate_and_store_token(data, user.id, session)
                user = session.query(User).get(user.id)
                self.current_user = user
                # Vérify new token
                payload = self.verify_token(user.token)
                if not payload:
                    sentry_sdk.capture_message("New token verification failed")
                    return None

            return self.current_user

        except Exception as e:
            error_message = "Error during signin process"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)
            return None

    def _generate_and_store_token(self, data, user_id, session):
        """
        Generates a new token, encrypts it, and stores it in the database.

        :param data: The data to include in the token payload.
        :type data: dict
        :param user_id: The ID of the user.
        :type user_id: int
        :param session: The database session.
        :type session: Session
        """
        try:
            self.generate_new_encryption_key()
            token = self.generate_token(data)
            self.encrypt_and_store_token(token, user_id, session)
            os.environ["ENCRYPTED_TOKEN"] = token
        except Exception as e:
            error_message = "Error generating and storing token"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)

    def load_or_generate_key(self):
        """
        Loads the encryption key from the environment variable or generates a new one if not present.
        """
        try:
            key = os.getenv("ENCRYPTION_KEY")
            if key is None:
                key = Fernet.generate_key().decode()
                os.environ["ENCRYPTION_KEY"] = key
            return key
        except Exception as e:
            error_message = "Error loading or generating encryption key"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)
            return None

    def generate_token(self, data, expiration=20):
        """
        Generates a JWT token.

        :param data: The data to include in the token payload.
        :type data: dict
        :param expiration: The expiration time of the token in seconds.
        :type expiration: int
        :return: The generated JWT token.
        :rtype: str
        """
        try:
            payload = data.copy()
            payload["exp"] = datetime.utcnow() + timedelta(seconds=expiration)
            return jwt.encode(payload, os.getenv("ENCRYPTION_KEY"), algorithm="HS256")
        except Exception as e:
            error_message = "Error generating token"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)
            return None

    def encrypt_and_store_token(self, token, user_id, session):
        """
        Encrypts and stores the token in the database.

        :param token: The JWT token to encrypt and store.
        :type token: str
        :param user_id: The ID of the user.
        :type user_id: int
        :param session: The database session.
        :type session: Session
        """
        try:
            encrypted_token = Fernet(os.getenv("ENCRYPTION_KEY")).encrypt(token.encode()).decode()
            self.repository.update_attr(user_id, "token", encrypted_token, session)
        except Exception as e:
            error_message = "Error encrypting and storing token"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)

    def load_and_decrypt_token(self):
        """
        Loads and decrypts the token from an environment variable.

        :return: The decrypted JWT token.
        :rtype: str
        """
        try:
            encrypted_token = os.getenv("ENCRYPTED_TOKEN")
            if encrypted_token:
                return Fernet(os.getenv("ENCRYPTION_KEY")).decrypt(encrypted_token.encode()).decode()
            return None
        except Exception as e:
            error_message = "Error loading and decrypting token"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)
            return None
    
    @staticmethod
    def verify_token(token):
        """
        Verifies the JWT token.

        :param token: The encrypted JWT token to verify.
        :type token: str
        :return: The decoded payload.
        :rtype: dict
        """
        try:
            decrypted_token = Fernet(os.getenv("ENCRYPTION_KEY")).decrypt(token.encode())
            return jwt.decode(decrypted_token, os.getenv("ENCRYPTION_KEY"), algorithms=["HS256"])
        except Exception as e:
            error_message = "Error verifying token"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)
            return None

    def generate_new_encryption_key(self):
        """
        Generates a new encryption key and updates the environment variable.
        """
        try:
            os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        except Exception as e:
            error_message = "Error generating new encryption key"
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(error_message)
    
    def revoke_token(self, session):
        """
        Removes the authentication token from the database for the given user.
        """
        self.repository.update_attr(self.current_user.id, "token", None, session)