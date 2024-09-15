"""This file serves as the entry point for the application, initializing and running the MainController."""

from dotenv import load_dotenv

from src.controllers.main_controller import MainController

load_dotenv()


if __name__ == "__main__":

    MainController().run_application()
