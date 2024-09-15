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
