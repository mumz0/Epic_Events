"""This file defines the EventRepository class for handling operations related to Event entities."""

import sentry_sdk

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
        Filter events by sales email address.

        :param email: The sales email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of events.
        :rtype: list
        """
        try:
            events = session.query(Event).filter(Event.support_user_id == email).all()
            return events
        except Exception as e:
            error_message = f"Error filtering events by sales email address: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e

    def filter_by_client_email_address(self, email: str, session) -> list:
        """
        Filter events by client email address.

        :param email: The client email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of events.
        :rtype: list
        """
        try:
            events = session.query(Event).filter(Event.client_id == email).all()
            return events
        except Exception as e:
            error_message = f"Error filtering events by client email address: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e

    def filter_by_support_user_on_event(self, session, is_support: bool) -> list:
        """
        Filter events by support user on event.

        :param bool: The boolean value to filter by.
        :type bool: bool
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of events.
        :rtype: list
        """
        try:
            if is_support:
                events = session.query(Event).filter(Event.support_user_id.isnot(None)).all()
            else:
                events = session.query(Event).filter(Event.support_user_id.is_(None)).all()
            return events
        except Exception as e:
            error_message = f"Error filtering events by support user: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e
