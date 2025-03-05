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
        repository: RoleRepository = RoleRepository()
        super().__init__(Role, repository)

    def get_all(self, session):
        """
        Retrieves all Role entities from the repository.

        :return: A list of all Role entities.
        :rtype: list
        """
        return self.repository.get_all(session)

    def get_by_name(self, name, session):
        """
        Retrieves a Role entity by its name.

        :param name: The name of the Role entity.
        :type name: str
        :return: The Role entity with the specified name.
        :rtype: Role
        """
        return self.repository.get_by_name(name, session)
