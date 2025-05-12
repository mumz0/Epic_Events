from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_config.settings import DatabaseManager, Engine
from src.models.base import Base
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.role import Role

# Import models so they are registered in Base.metadata
from src.models.user import User

# ... import any other models you have ...


engine_obj = Engine()
engine_obj.engine = create_engine("sqlite:///:memory:")
engine_obj.session_factory = sessionmaker(bind=engine_obj.engine)
session = engine_obj.session_factory()

_already_initialized = False


def initialize_database_filled():
    global _already_initialized
    if _already_initialized:
        return

    Base.metadata.create_all(engine_obj.engine)
    database_manager = DatabaseManager(engine_obj)
    database_manager.initialize_and_populate_database()

    _already_initialized = True
