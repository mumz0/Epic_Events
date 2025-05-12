"""This file defines the PermissionRepository class for handling operations related to Permission entities."""

import sentry_sdk

from src.models.permission import Permission
from src.models.role import Role
from src.models.role_permission import RolePermission
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

    def get_permissions_by_role(self, role_name, session):
        """
        Retrieves a list of permissions associated with the given role name.

        :param role_name: The name of the role.
        :type role_name: str
        :param session: The database session.
        :type session: sqlalchemy.orm.Session
        :return: A list of Permission objects associated with the role name.
        :rtype: list
        """
        try:
            permissions = (
                session.query(Permission)
                .join(RolePermission, Permission.action == RolePermission.permission)
                .join(Role, Role.name == RolePermission.role)
                .filter(Role.name == role_name)
                .all()
            )
            return permissions
        except Exception as e:
            error_message = f"Error retrieving permissions"
            sentry_sdk.capture_message(error_message)
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e
