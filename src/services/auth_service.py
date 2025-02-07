"""
This module contains the AuthService class, which provides authentication services.
"""

import os
from datetime import datetime, timedelta

import jwt
from cryptography.fernet import Fernet
from passlib.hash import argon2

from logger_file import logger
from src.models.role import Role
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.base_service import BaseService
from src.services.permission_service import PermissionService
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

    def check_permission_signup(self, session):
        """
        Checks if the current user has permission to sign up a new user.

        :param session: The database session.
        :type session: Session
        :return: True if the user has permission, False otherwise.
        :rtype: bool
        """
        user_role_name = self.current_user.role.name
        role_permissions = PermissionService().get_permissions(user_role_name, session)
        return any(role_permission.action == "create" and role_permission.entity == "user" for role_permission in role_permissions)

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

        role_instance = BaseService(Role).get_id(role, session)
        user_data = {"email_address": email, "password": argon2.hash(password), "role": role_instance}
        user = BaseService(User).create(user_data, session)
        logger.info("User: %s", user)
        if user:
            logger.info("User created successfully.")
            return user
        logger.info("User creation failed.")
        return None

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
        user = UserService().get_user(email, session)
        logger.info("User: %s", user)
        if not user or not argon2.verify(password, user.password):
            return None

        self.current_user = user
        data = {"user_id": user.id}

        try:
            if os.getenv("ENCRYPTED_TOKEN") is None or user.token is None:
                self._generate_and_store_token(data, user.id, session)
            self.verify_token(user.token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            print(f"Token verification failed: {e}")
            self._generate_and_store_token(data, user.id, session)
            self.verify_token(user.token)

        return self.current_user

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
        self.generate_new_encryption_key()
        token = self.generate_token(data)
        self.encrypt_and_store_token(token, user_id, session)
        os.environ["ENCRYPTED_TOKEN"] = token

    def load_or_generate_key(self):
        """
        Loads the encryption key from the environment variable or generates a new one if not present.
        """
        key = os.getenv("ENCRYPTION_KEY")
        if key is None:
            key = Fernet.generate_key().decode()
            os.environ["ENCRYPTION_KEY"] = key
        return key

    def generate_token(self, data, expiration=3600):
        """
        Generates a JWT token.

        :param data: The data to include in the token payload.
        :type data: dict
        :param expiration: The expiration time of the token in seconds.
        :type expiration: int
        :return: The generated JWT token.
        :rtype: str
        """
        payload = data.copy()
        payload["exp"] = datetime.utcnow() + timedelta(seconds=expiration)
        return jwt.encode(payload, os.getenv("ENCRYPTION_KEY"), algorithm="HS256")

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
        encrypted_token = Fernet(os.getenv("ENCRYPTION_KEY")).encrypt(token.encode()).decode()
        self.repository.update_attr(user_id, "token", encrypted_token, session)

    def load_and_decrypt_token(self):
        """
        Loads and decrypts the token from an environment variable.

        :return: The decrypted JWT token.
        :rtype: str
        """
        encrypted_token = os.getenv("ENCRYPTED_TOKEN")
        if encrypted_token:
            return Fernet(os.getenv("ENCRYPTION_KEY")).decrypt(encrypted_token.encode()).decode()
        return None

    def verify_token(self, token):
        """
        Verifies the JWT token.

        :param token: The encrypted JWT token to verify.
        :type token: str
        :return: The decoded payload.
        :rtype: dict
        """
        decrypted_token = Fernet(os.getenv("ENCRYPTION_KEY")).decrypt(token.encode())
        return jwt.decode(decrypted_token, os.getenv("ENCRYPTION_KEY"), algorithms=["HS256"])

    def generate_new_encryption_key(self):
        """
        Generates a new encryption key and updates the environment variable.
        """
        os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
