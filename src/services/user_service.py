"""This file defines the UserService class for handling operations related to User entities."""

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.base_service import BaseService


class UserService(BaseService):
    """
    UserService handles operations related to User entities.

    :param BaseService: Inherits from BaseService to utilize common service functionalities.
    :type BaseService: class
    """

    def __init__(self):
        """
        Initializes the UserService with the User model and repository.

        :param User: The User model class.
        :type User: class
        """
        repository = UserRepository()
        super().__init__(User, repository)

    def get_user(self, email: str, session) -> bool:
        """
        Authenticate user against the database.

        :param email: The user's email.
        :type email: str
        :param password: The user's password.
        :type password: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: True if authentication is successful, False otherwise.
        :rtype: bool
        """
        user = self.repository.find_by_email(email, session)
        return user
