"""This file defines the EventService class for handling operations related to Event entities."""

import string
import uuid
from datetime import datetime

from src.models.event import Event
from src.repositories.event_reposiroty import EventRepository
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

        :param user_list: A list of Event objects.
        :type user_list: list
        :return: A dictionary of Event objects.
        :rtype: dict
        """
        user_dict = {}
        for contract in event_list:
            user_dict["ID"] = contract.id
        return user_dict

    def filter_by_support_email_adress(self, email: str, session) -> list:
        """
        Filter contracts by sales email address.

        :param email: The sales email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of contracts.
        :rtype: list
        """
        return self.repository.filter_by_support_email_address(email, session)

    def filter_by_email_adress(self, email: str, session) -> list:
        """
        Filter contracts by email address.

        :param email: The email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of contracts.
        :rtype: list
        """
        return self.repository.filter_by_client_email_address(email, session)

    def string_date_to_datetime(self, date_string):
        """
        Convert a date string to a datetime object.

        :param date_string: Date string in the format 'YYYY/MM/DD'.
        :type date_string: str
        :return: Corresponding datetime object.
        :rtype: datetime.datetime
        """
        date_object = datetime.strptime(date_string, "%Y/%m/%d")
        return date_object

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
        while True:
            uid = uuid.uuid4().hex.upper()
            uid = "".join(filter(lambda x: x in string.ascii_uppercase + string.digits, uid))
            uid_with_prefix = f"EVENT{uid[:length]}"
            if not session.query(Event).filter(Event.id == uid_with_prefix).first():
                return uid_with_prefix

    def filter_by_support_user_on_event(self, session, is_support: bool) -> list:
        """
        Filter events by support user on event.

        :param session: The SQLAlchemy session.
        :type session: Session
        :param True: The support user on event.
        :type True: bool
        :return: A list of events.
        :rtype: list
        """
        return self.repository.filter_by_support_user_on_event(session, is_support)

    def prepare_data_and_update(self, data, obj, session) -> dict:
        """
        Create the data to update the user.

        :param data: The data to update the user.
        :type data: dict
        :return: The data to update the user.
        :rtype: dict
        """
        datetime_start_date = self.string_date_to_datetime(data["Start Date"])
        datetime_end_date = self.string_date_to_datetime(data["End Date"])
        data = {
            "name": data["Name"],
            "start_date": datetime_start_date,
            "end_date": datetime_end_date,
            "location": data["Location"],
            "attendees": data["Attendees"],
            "notes": data["Notes"],
            "support_user_id": data["Support User ID"],
        }
        return self.repository.update_obj(obj.id, data, session)
