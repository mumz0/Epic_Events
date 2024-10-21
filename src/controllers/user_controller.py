"""This file defines the UserController class for handling user-related operations."""

from src.models.role import Role
from src.services.auth_service import AuthService
from src.views.auth_view import AuthView


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
        admin_role = session_obj.query(Role).filter_by(name="admin").first()
        email, password = AuthView().signup_admin()
        AuthService(None).signup_process(email, password, admin_role, session_obj)
