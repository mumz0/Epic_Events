"""This file defines the ClientService class for handling operations related to Client entities."""

import urwid

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

    def create_object_details_frame(self, title, selected_object):
        """
        Create a frame displaying details for a given object.
        This method first creates a card for the selected object (if provided),
        then composes a header. Both the card and header elements are added to a frame,
        which is returned as the resulting widget.
        :param title: A string representing the title to be displayed in the header.
        :param selected_object: The object for which to create a card. If None,
            no card will be generated.
        :return: A frame widget containing the header and the object's details.
        """
        card = urwid.Text("")  # Initialisation par défaut
        if selected_object:
            card = self.create_card(selected_object)

        header_body = self.create_header_body(title)
        body = header_body + [card]
        frame = self.create_frame(body)
        return frame

    def list_to_dict(self, client_list):
        """
        Converts a list of Client objects to a dictionary.

        :param user_list: A list of Client objects.
        :type user_list: list
        :return: A dictionary of Client objects.
        :rtype: dict
        """
        client_dict = {}
        for client in client_list:
            client_dict["Email address"] = client.email
        return client_dict
