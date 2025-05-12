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
        permission_instances = []
        permission_lst = [
            "user_create",
            "user_read",
            "user_update",
            "user_delete",
            "client_create",
            "client_read",
            "client_update",
            "client_delete",
            "contract_create",
            "contract_read",
            "contract_update",
            "contract_delete",
            "event_create",
            "event_read",
            "event_update",
            "event_delete",
        ]
        for permission in permission_lst:
            permission_data = {"action": permission}
            permission_obj = PermissionService().create_instance(permission_data)
            permission_instances.append(permission_obj)
        return permission_instances
