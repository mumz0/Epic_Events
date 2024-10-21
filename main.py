"""
    This file is the entry point of the application. It initializes the database and the main controller, then runs the application.
"""

from dotenv import load_dotenv
from logging_config import setup_logging

from database_config.settings import database_manager
from src.controllers.main_controller import MainController

load_dotenv()


def main():
    """
    Initializes the database and the main controller, then runs the application.
    """
    setup_logging()
    database_manager.initialize_and_populate_database()
    main_controller = MainController(database_manager.session)
    main_controller.run_application()


if __name__ == "__main__":
    main()
