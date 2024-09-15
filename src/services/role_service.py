"""This file defines the RoleService class for handling operations related to Role entities."""

from src.models.role import Role
from src.repositories.role_repository import RoleRepository
from src.services.base_service import BaseService


class RoleService(BaseService):
    """
    RoleService handles operations related to Role entities.

    :param BaseService: Inherits from BaseService to utilize common service functionalities.
    :type BaseService: class
    """

    def __init__(self):
        """
        Initializes the RoleService with the Role model and repository.

        :param Role: The Role model class.
        :type Role: class
        """
        repository = RoleRepository()
        super().__init__(Role, repository)
