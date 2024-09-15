"""This file defines the ClientService class for handling operations related to Client entities."""

from src.models.client import Client
from src.repositories.client_repository import ClientRepository
from src.services.base_service import BaseService


class ClientService(BaseService):
    """
    ClientService handles operations related to Client entities.

    :param BaseService: Inherits from BaseService to utilize common service functionalities.
    :type BaseService: class
    """

    def __init__(self):
        """
        Initializes the ClientService with the Client model.

        :param Client: The Client model class.
        :type Client: class
        """
        repository = ClientRepository()
        super().__init__(Client, repository)
