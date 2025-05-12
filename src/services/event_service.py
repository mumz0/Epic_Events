"""This file defines the EventService class for handling operations related to Event entities."""

import string
import uuid
from datetime import datetime

import sentry_sdk

from src.models.event import Event
from src.repositories.event_repository import EventRepository
from src.services.base_service import BaseService


class EventService(BaseService):
    """
    EventService handles operations related to Event entities.

    :param BaseService: Inherits from BaseService to utilize common service functionalities.
    :type BaseService: class
    """

    def __init__(self):
        """
        Initializes the EventService with the Event model.

        :param Event: The Event model class.
        :type Event: class
        """
        repository = EventRepository()
        super().__init__(Event, repository)

    def list_to_dict(self, event_list):
        """
        Converts a list of event objects to a dictionary.

        :param event_list: A list of Event objects.
        :type event_list: list
        :return: A dictionary of Event objects.
        :rtype: dict
        """
        try:
            event_dict = {}
            for event in event_list:
                event_dict["ID"] = event.id
            return event_dict
        except Exception as e:
            sentry_sdk.capture_message("Error converting event list to dictionary")
            sentry_sdk.capture_exception(e)
            return {}

    def filter_by_support_email_adress(self, email: str, session) -> list:
        """
        Filter events by support email address.

        :param email: The support email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of events.
        :rtype: list
        """
        try:
            return self.repository.filter_by_support_email_address(email, session)
        except Exception as e:
            sentry_sdk.capture_message("Error filtering events by support email address")
            sentry_sdk.capture_exception(e)
            return []

    def filter_by_email_adress(self, email: str, session) -> list:
        """
        Filter events by email address.

        :param email: The email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of events.
        :rtype: list
        """
        try:
            return self.repository.filter_by_client_email_address(email, session)
        except Exception as e:
            sentry_sdk.capture_message("Error filtering events by email address")
            sentry_sdk.capture_exception(e)
            return []

    def string_date_to_datetime(self, date_string):
        """
        Convert a date string to a datetime object.

        :param date_string: Date string in the format 'YYYY/MM/DD'.
        :type date_string: str
        :return: Corresponding datetime object.
        :rtype: datetime.datetime
        """
        try:
            date_object = datetime.strptime(date_string, "%Y/%m/%d")
            return date_object
        except Exception as e:
            sentry_sdk.capture_message("Error converting date string to datetime")
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def generate_uid(session, length=8):
        """
        Generate a unique identifier (UID) for an event.

        This method generates a UID with a specified length, prefixed with "EVENT".
        The UID is ensured to be unique within the given session by checking against
        existing event IDs in the database.

        :param session: The database session used to query existing event IDs.
        :type session: sqlalchemy.orm.session.Session
        :param length: The length of the UID to be generated (excluding the prefix), defaults to 8.
        :type length: int, optional
        :return: A unique event identifier with the specified length and "EVENT" prefix.
        :rtype: str
        """
        try:
            while True:
                uid = uuid.uuid4().hex.upper()
                uid = "".join(filter(lambda x: x in string.ascii_uppercase + string.digits, uid))
                uid_with_prefix = f"EVENT{uid[:length]}"
                if not session.query(Event).filter(Event.id == uid_with_prefix).first():
                    return uid_with_prefix
        except Exception as e:
            sentry_sdk.capture_message("Error generating UID")
            sentry_sdk.capture_exception(e)
            return None

    def filter_by_support_user_on_event(self, session, is_support: bool) -> list:
        """
        Filter events by support user on event.

        :param session: The SQLAlchemy session.
        :type session: Session
        :param is_support: The support user on event.
        :type is_support: bool
        :return: A list of events.
        :rtype: list
        """
        try:
            return self.repository.filter_by_support_user_on_event(session, is_support)
        except Exception as e:
            sentry_sdk.capture_message("Error filtering events by support user")
            sentry_sdk.capture_exception(e)
            return []

    def prepare_data_and_update(self, data, obj, session):
        """
        Prepare event data and update the event object in the database.

        :param data: The event data.
        :type data: dict
        :param obj: The event object to update.
        :type obj: Event
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: The updated event data.
        :rtype: dict
        """
        try:
            if "Start Date" in data:
                data["start_date"] = datetime.strptime(data["Start Date"], "%Y/%m/%d")
            if "End Date" in data:
                data["end_date"] = datetime.strptime(data["End Date"], "%Y/%m/%d")
            return self.repository.update_obj(data, obj, session)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return {}
