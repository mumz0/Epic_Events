"""
    This file is the entry point of the application. It initializes the database and the main controller, then runs the application.
"""

from dotenv import load_dotenv

from database_config.settings import database_manager
from src.controllers.main_controller import MainController
from src.views.base_view import BaseView

load_dotenv()


def main():
    """
    Initializes the database and the main controller, then runs the application.
    """
    database_manager.initialize_and_populate_database()
    base_view = BaseView()
    MainController(database_manager.session, base_view, None, []).run_application()


if __name__ == "__main__":
    main()
