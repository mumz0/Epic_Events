"""This file defines the PermissionRepository class for handling operations related to Permission entities."""

from src.models.permission import Permission
from src.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository):
    """
    PermissionRepository handles operations related to Permission entities.

    :param BaseRepository: Inherits from BaseRepository to utilize common repository functionalities.
    :type BaseRepository: class
    """

    def __init__(self):
        """
        Initializes the PermissionRepository with the Permission model.

        :param Permission: The Permission model class.
        :type Permission: class
        """
        super().__init__(Permission)
