"""This file defines the RoleController class for handling role-related operations."""

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
        admin_role_data = {"name": "admin", "permissions": permission_obj_lst}
        return RoleService().create(admin_role_data, session_obj)

    def create_management_role(self, permission_obj_lst, session_obj):
        """
        Creates the management role with specific permissions.

        :param permission_obj_lst: List of permission objects.
        :type permission_obj_lst: list
        :param session_obj: The database session object.
        :type session_obj: Session
        """
        management_permission_lst = []
        for permission in permission_obj_lst:
            is_read_action = permission.action == "read"
            is_user_entity = permission.entity == "user"
            is_create_contract = permission.action == "create" and permission.entity == "contract"
            is_modify_contract = permission.action == "modify" and permission.entity == "contract"

            if is_read_action or is_user_entity or is_create_contract or is_modify_contract:
                management_permission_lst.append(permission)

        management_role_data = {"name": "management", "permissions": management_permission_lst}
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
        sales_permission_lst = []
        for permission in permission_obj_lst:
            is_read_action = permission.action == "read"
            is_create_client = permission.action == "create" and permission.entity == "client"
            is_modify_client = permission.action == "modify" and permission.entity == "client"
            is_create_event = permission.action == "create" and permission.entity == "event"
            is_modify_contract = permission.action == "modify" and permission.entity == "contract"

            if is_read_action or is_create_client or is_modify_client or is_create_event or is_modify_contract:
                sales_permission_lst.append(permission)

        sales_role_data = {"name": "sales", "permissions": sales_permission_lst}
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
        support_permissions_lst = []
        for permission in permission_obj_lst:
            if (permission.action == "read") or (permission.action == "modify" and permission.entity == "event"):
                support_permissions_lst.append(permission)

        support_role_data = {"name": "support", "permissions": support_permissions_lst}
        RoleService().create(support_role_data, session_obj)
