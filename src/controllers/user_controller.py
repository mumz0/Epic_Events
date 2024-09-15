"""This file defines the UserController class for handling user-related operations."""

from src.models.role import Role
from src.services.user_service import UserService


class UserController:
    """
    UserController handles user-related operations.
    """

    def create_admin_user(self, session_obj):
        """
        Creates an admin user with a predefined password and admin role.

        :param session_obj: The database session object.
        :type session_obj: Session
        """
        admin_role = session_obj.query(Role).filter(Role.name == "admin").first()
        admin_user_data = {"email_address": "", "password": "adminpassword", "role": admin_role}
        UserService().create(admin_user_data, session_obj)
