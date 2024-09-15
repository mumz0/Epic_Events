"""This file defines the PermissionService class for handling operations related to Permission entities."""

from src.models.permission import Permission
from src.repositories.permission_repository import PermissionRepository
from src.services.base_service import BaseService


class PermissionService(BaseService):
    """
    PermissionService handles operations related to Permission entities.

    :param BaseService: Inherits from BaseService to utilize common service functionalities.
    :type BaseService: class
    """

    def __init__(self):
        """
        Initializes the PermissionService with the Permission model.

        :param Permission: The Permission model class.
        :type Permission: class
        """
        repository = PermissionRepository()
        super().__init__(Permission, repository)
