"""This file defines the EventRepository class for handling operations related to Event entities."""

from src.models.event import Event
from src.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository):
    """
    EventRepository handles operations related to Event entities.

    :param BaseRepository: Inherits from BaseRepository to utilize common repository functionalities.
    :type BaseRepository: class
    """

    def __init__(self):
        """
        Initializes the EventRepository with the Event model.

        :param Event: The Event model class.
        :type Event: class
        """
        super().__init__(Event)

    def filter_by_sales_email_address(self, email: str, session) -> list:
        """
        Filter contracts by sales email address.

        :param email: The sales email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of contracts.
        :rtype: list
        """
        events = session.query(Event).filter(Event.support_user_id == email).all()
        return events

    def filter_by_client_email_address(self, email: str, session) -> list:
        """
        Filter contracts by client email address.

        :param email: The client email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of contracts.
        :rtype: list
        """
        events = session.query(Event).filter(Event.client_id == email).all()
        return events
