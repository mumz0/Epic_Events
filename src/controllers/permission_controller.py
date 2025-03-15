"""This file defines the PermissionController class for handling permission-related operations."""

import os

from src.services.permission_service import PermissionService


class PermissionController:
    """
    PermissionController handles permission-related operations.
    """

    def create_permissions(self):
        """
        Create permissions in the database.
        """
        permission_data_lst = []
        for permission in os.getenv("PERMISSIONS").split(","):
            permission_data = {"action": permission}
            permission_obj = PermissionService().create_instance(permission_data)
            permission_data_lst.append(permission_obj)
        return permission_data_lst
