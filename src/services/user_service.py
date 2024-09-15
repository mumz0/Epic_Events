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
