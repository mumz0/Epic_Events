"""This file defines the Engine class for managing the database connection and session factory."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.base import Base


class Engine:
    """
    Engine handles the database connection and session factory.
    """

    def __init__(self):
        """
        Initializes the Engine with the database path and creates the engine.

        :param DATABASE_PATH: The path to the SQLite database file.
        :type DATABASE_PATH: str
        :param Session: The session factory.
        :type Session: sessionmaker
        :param engine: The SQLAlchemy engine.
        :type engine: Engine
        """
        self.database_path = os.path.join("_persistent", "database.db")
        self.session = None
        self.engine = create_engine("sqlite:///" + self.database_path)

    def load_database_and_session_factory(self):
        """
        Loads the database schema and initializes the session factory.
        """
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.session = sessionmaker(bind=self.engine)

    def get_db(self):
        """
        Provides a database session and ensures it is closed after use.

        :yield: The database session.
        :rtype: Session
        """
        db = self.session()
        db.current_user_id = None
        try:
            yield db
        finally:
            db.close()


engine_obj = Engine()
