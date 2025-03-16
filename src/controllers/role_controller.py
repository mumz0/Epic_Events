"""This file defines the RoleController class for handling role-related operations."""

from src.models.role import RoleEnum
from src.services.role_service import RoleService


class RoleController:
    """
    RoleController handles role-related operations.
    """

    def create_roles(self, permission_obj_lst, session_obj):
        """
        Creates predefined roles with associated permissions.

        :param permission_obj_lst: List of permission objects.
        :type permission_obj_lst: list
        :param session_obj: The database session object.
        :type session_obj: Session
        """
        self.create_admin_role(permission_obj_lst, session_obj)
        self.create_management_role(permission_obj_lst, session_obj)
        self.create_sales_role(permission_obj_lst, session_obj)
        self.create_support_role(permission_obj_lst, session_obj)

    def create_admin_role(self, permission_obj_lst, session_obj):
        """
        Creates the admin role with all permissions.

        :param permission_obj_lst: List of permission objects.
        :type permission_obj_lst: list
        :param session_obj: The database session object.
        :type session_obj: Session
        :return: The created admin role.
        :rtype: Role
        """
        admin_role_data = {"name": RoleEnum.ADMIN.value, "permissions": permission_obj_lst}
        return RoleService().create(admin_role_data, session_obj)

    def create_management_role(self, permission_obj_lst, session_obj):
        """
        Creates the management role with specific permissions.

        :param permission_obj_lst: List of permission objects.
        :type permission_obj_lst: list
        :param session_obj: The database session object.
        :type session_obj: Session
        """
        management_permission_lst = [
            "user_create",
            "user_read",
            "user_update",
            "user_delete",
            "contract_create",
            "contract_read",
            "contract_update",
            "event_read",
            "event_update",
            "client_read",
        ]
        management_permission_obj_lst = []
        for permission in permission_obj_lst:
            if permission.action in management_permission_lst:
                management_permission_obj_lst.append(permission)

        management_role_data = {"name": RoleEnum.MANAGEMENT.value, "permissions": management_permission_obj_lst}
        RoleService().create(management_role_data, session_obj)

    def create_sales_role(self, permission_obj_lst, session_obj):
        """
        Create a sales role with specific permissions.
        This method filters the given list of permission objects to include only those
        that are relevant to the sales role. The relevant permissions are:
        - Read any entity
        - Create a client
        - Modify a client
        - Create an event
        - Modify a contract
        The filtered permissions are then used to create a sales role, which is saved
        using the RoleService.
        :param permission_obj_lst: List of permission objects to be filtered.
        :type permission_obj_lst: list
        :param session_obj: The session object used to interact with the database.
        :type session_obj: Session
        """
        sales_permission_lst = [
            "user_read",
            "client_create",
            "client_update",
            "client_read",
            "contract_read",
            "contract_update",
            "event_create",
            "event_read",
        ]
        sales_permission_obj_lst = []
        for permission in permission_obj_lst:
            if permission.action in sales_permission_lst:
                sales_permission_obj_lst.append(permission)

        sales_role_data = {"name": RoleEnum.SALES.value, "permissions": sales_permission_obj_lst}
        RoleService().create(sales_role_data, session_obj)

    def create_support_role(self, permission_obj_lst, session_obj):
        """
        Create a support role with specific permissions.
        This method filters the given list of permissions to include only those
        that allow reading or modifying events. It then creates a support role
        with these permissions and uses the RoleService to save it.
        :param permission_obj_lst: List of permission objects to be filtered.
        :type permission_obj_lst: list
        :param session_obj: The session object used for database transactions.
        :type session_obj: Session
        """
        support_permissions_lst = [
            "user_read",
            "event_read",
            "event_update",
            "contract_read",
            "client_read",
        ]
        support_permission_obj_lst = []
        for permission in permission_obj_lst:
            if permission.action in support_permissions_lst:
                support_permission_obj_lst.append(permission)

        support_role_data = {"name": RoleEnum.SUPPORT.value, "permissions": support_permission_obj_lst}
        RoleService().create(support_role_data, session_obj)
