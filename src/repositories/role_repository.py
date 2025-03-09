"""This file defines the RoleRepository class for handling operations related to Role entities."""

import sentry_sdk

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

    def get_all(self, session):
        """
        Retrieves all roles except the 'admin' role from the database.

        :param session: The database session.
        :type session: Session
        :return: A list of roles excluding the 'admin' role.
        :rtype: list
        """
        try:
            roles = session.query(Role).filter(Role.name != "admin").all()
            return roles
        except Exception as e:
            error_message = f"Error retrieving all roles except 'admin': {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e

    def get_by_name(self, name, session):
        """
        Retrieves a Role from the database by its name.

        :param name: The name of the role.
        :type name: str
        :param session: The database session.
        :type session: Session
        :return: A Role object if found, otherwise None.
        :rtype: Role | None
        """
        try:
            role = session.query(Role).filter_by(name=name).first()
            if not role:
                error_message = f"Role with name {name} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)
            return role
        except Exception as e:
            error_message = f"Error retrieving role by name: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e
