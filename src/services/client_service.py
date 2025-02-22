"""This file defines the ClientService class for handling operations related to Client entities."""

from logger_file import logger
from src.models.client import Client
from src.repositories.client_repository import ClientRepository
from src.services.base_service import BaseService
from src.services.user_service import UserService


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
            client_dict[client.id] = client.to_dict()
        logger.info("Client dict: %s", client_dict)
        return client_dict

    def prepare_data_and_update(self, data, obj, session):
        """
        Create the data to update the user.

        :param data: The data to update the user.
        :type data: dict
        :return: The data to update the user.
        :rtype: dict
        """
        for attr, value in data.items():
            logger.info(f"{attr}: {value}")
        user = UserService().get_user(data["Sales contact"], session)
        if not user:
            raise ValueError(f"Contact Sales '{data['Sales contact']}' not found.")

        data = {
            "phone": data["Phone"],
            "compagny": data["Compagny"],
            "name": data["Name"],
            "email": data["Email address"],
            "sales_contact_id": user.email_address,
        }
        return self.repository.update_obj(obj.id, data, session)

    def remove_attributes_from_object(self, object_template, attributes_to_remove):
        """
        Removes specified attributes from the object template.

        :param object_template: The template object from which attributes will be removed.
        :type object_template: dict
        :param attributes_to_remove: A list of attribute names to be removed.
        :type attributes_to_remove: list
        :return: The modified object template.
        :rtype: dict
        """
        for attr in attributes_to_remove:
            object_template.pop(attr, None)
        return object_template
