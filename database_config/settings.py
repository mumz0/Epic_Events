"""This file defines the Engine class for managing the database connection and session factory."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.controllers.auth_controller import AuthController
from src.controllers.permission_controller import PermissionController
from src.controllers.role_controller import RoleController
from src.models.base import Base
from src.services.role_service import RoleService


class Engine:
    """Handles the database connection and session factory."""

    def __init__(self):
        """Initializes the Engine with the database path and creates the engine."""
        self.database_path = os.path.join("_persistent", "database.db")
        self.engine = create_engine(f"sqlite:///{self.database_path}")
        self.session_factory = sessionmaker(bind=self.engine)

    def load_database(self):
        """Loads the database schema."""
        Base.metadata.create_all(self.engine, checkfirst=True)

    def get_db(self):
        """Provides a database session and ensures it is closed after use."""
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()


class DatabaseManager:
    """Manages database initialization and population."""

    def __init__(self, engine):
        self.engine = engine
        self.session = None

    def initialize_and_populate_database(self):
        """Initializes the database and fills it with data if it is empty."""
        self.initialize_database()
        if self.is_database_empty():
            print("Database contains no data.")
            self.fill_db_with_data()
        else:
            print("Database already contains data.")

    def is_database_empty(self):
        """Checks if the database is empty by verifying if the Roles table contains any data."""
        roles = RoleService().get_all(self.session)
        return not bool(roles)

    def initialize_database(self):
        """Initializes the database and sets up the session object."""
        self.engine.load_database()
        session_generator = self.engine.get_db()
        self.session = next(session_generator)
        print("Database session initialized:", self.session)

    def fill_db_with_data(self):
        """Fills the database with initial data by creating permissions, roles, and an admin user."""
        permission_obj_lst = PermissionController().create_permissions()
        RoleController().create_roles(permission_obj_lst, self.session)
        AuthController.create_admin_user(self.session)


# Initialize the Engine object
engine_obj = Engine()

# Initialize the DatabaseManager with the Engine instance
database_manager = DatabaseManager(engine_obj)
