"""
This module sets up the logging configuration for the application.
"""

import logging


def setup_logging():
    """
    Configures the logging settings for the application.

    This function sets up the logging configuration to log messages with the INFO level or higher.
    The log messages are formatted to include the timestamp, logger name, log level, and the message.
    The logs are written to a file named 'app.log'.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
        ],
    )
    return logging.getLogger()


logger = setup_logging()
