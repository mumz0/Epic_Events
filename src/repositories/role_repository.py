"""This file defines the RoleRepository class for handling operations related to Role entities."""

from src.models.role import Role
from src.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository):
    """
    RoleRepository handles operations related to Role entities.

    :param BaseRepository: Inherits from BaseRepository to utilize common repository functionalities.
    :type BaseRepository: class
    """

    def __init__(self):
        """
        Initializes the RoleRepository with the Role model.

        :param Role: The Role model class.
        :type Role: class
        """
        super().__init__(Role)
