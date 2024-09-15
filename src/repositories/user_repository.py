"""This file defines the UserRepository class for handling operations related to User entities."""

from src.models.user import User
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """
    UserRepository handles operations related to User entities.

    :param BaseRepository: Inherits from BaseRepository to utilize common repository functionalities.
    :type BaseRepository: class
    """

    def __init__(self):
        """
        Initializes the UserRepository with the User model.

        :param User: The User model class.
        :type User: class
        """
        super().__init__(User)
