"""This file defines the MainController class for initializing and running the application."""

import os

from database_config.settings import engine_obj
from src.controllers.permission_controller import PermissionController
from src.controllers.role_controller import RoleController
from src.controllers.user_controller import UserController


class MainController:
    """
    MainController handles the initialization and running of the application.
    """

    def __init__(self):
        """
        Initializes the MainController with a session object.
        """
        self.session_obj = None

    def run_application(self):
        """
        Runs the application by initializing the database and filling it with data if the database path is not set.
        """
        if not os.getenv("DB_PATH"):
            self.initialize_database()
            self.fill_db_with_data()

    def initialize_database(self):
        """
        Initializes the database and sets up the session object.
        """
        engine_obj.load_database_and_session_factory()
        session_generator = engine_obj.get_db()
        self.session_obj = next(session_generator)

    def fill_db_with_data(self):
        """
        Fills the database with initial data by creating permissions, roles, and an admin user.
        """
        permission_obj_lst = PermissionController().create_permissions()
        RoleController().create_roles(permission_obj_lst, self.session_obj)
        UserController().create_admin_user(self.session_obj)
