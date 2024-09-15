"""This file defines the ClientRepository class for handling operations related to Client entities."""

from src.models.client import Client
from src.repositories.base_repository import BaseRepository


class ClientRepository(BaseRepository):
    """
    ClientRepository handles operations related to Client entities.

    :param BaseRepository: Inherits from BaseRepository to utilize common repository functionalities.
    :type BaseRepository: class
    """

    def __init__(self):
        """
        Initializes the ClientRepository with the Client model.

        :param Client: The Client model class.
        :type Client: class
        """
        super().__init__(Client)
