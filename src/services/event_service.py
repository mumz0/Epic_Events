"""This file defines the EventService class for handling operations related to Event entities."""

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
