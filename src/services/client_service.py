"""This file defines the ClientService class for handling operations related to Client entities."""

import sentry_sdk

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

        :param client_list: A list of Client objects.
        :type client_list: list
        :return: A dictionary of Client objects.
        :rtype: dict
        """
        try:
            client_dict = {}
            for client in client_list:
                client_dict[client.id] = client.to_dict()
            return client_dict
        except Exception as e:
            error_message = "Error converting client list to dictionary"
            sentry_sdk.capture_exception(e)
            return {}

    def prepare_data_and_update(self, data, obj, session):
        """
        Create the data to update the client.

        :param data: The data to update the client.
        :type data: dict
        :param obj: The client object to update.
        :type obj: Client
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: The updated client data.
        :rtype: dict
        """
        try:
            user = UserService().get_user(data["Sales contact"], session)
            if not user:
                raise ValueError("Contact Sales not found.")

            data = {
                "phone": data["Phone"],
                "compagny": data["Compagny"],
                "name": data["Name"],
                "email_address": data["Email address"],
                "sales_contact_id": user.email_address,
            }
            return self.repository.update_obj(obj.id, data, session)
        except ValueError as e:
            sentry_sdk.capture_message(e)
            raise e
        except Exception as e:
            sentry_sdk.capture_message("Error preparing data and updating client")
            sentry_sdk.capture_exception(e)
            return {}
