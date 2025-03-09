"""
    This file is the entry point of the application. It initializes the database and the main controller, then runs the application.
"""

import logging
import os

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk import start_transaction
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.serverless import serverless_function

from database_config.settings import database_manager
from src.controllers.main_controller import MainController
from src.views.base_view import BaseView

load_dotenv()

# Configuration Sentry
sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.INFO)
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[sentry_logging],
    send_default_pii=True,
    traces_sample_rate=1.0,
    _experiments={
        "continuous_profiling_auto_start": True,
    },
)


@serverless_function
def main():
    """
    Initializes the database and the main controller, then runs the application.
    """
    # Start a transaction
    with start_transaction(op="task", name="main_function"):
        # Initialiser la base de données et le contrôleur principal
        logging.info("Initializing and populating the database")
        database_manager.initialize_and_populate_database()
        base_view = BaseView()
        logging.info("Running the main application")
        MainController(database_manager.session, base_view, None, []).run_application()


if __name__ == "__main__":
    main()
