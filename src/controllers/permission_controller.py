"""This file defines the PermissionController class for handling permission-related operations."""

import os

from src.services.permission_service import PermissionService


class PermissionController:
    """
    PermissionController handles permission-related operations.
    """

    def create_permissions(self):
        """
        Creates permissions based on environment variables.

        :return: A list of created permission objects.
        :rtype: list
        """
        admin_permission_str = os.getenv("ADMIN_PERMISSIONS_ACTION_LST")
        admin_entity_str = os.getenv("ADMIN_PERMISSIONS_ENTITY_LST")

        admin_permission_str_lst = admin_permission_str.split(",")
        admin_entity_str_lst = admin_entity_str.split(",")

        permission_data_lst = []
        for item in admin_permission_str_lst:
            for entity in admin_entity_str_lst:
                permission_data = {"action": item, "entity": entity}
                permission_obj = PermissionService().create_instance(permission_data)
                permission_data_lst.append(permission_obj)
        return permission_data_lst
