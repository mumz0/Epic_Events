"""This file defines the UserService class for handling operations related to User entities."""

import sentry_sdk

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.base_service import BaseService
from src.services.role_service import RoleService


class UserService(BaseService):
    """
    UserService handles operations related to User entities.

    :param BaseService: Inherits from BaseService to utilize common service functionalities.
    :type BaseService: class
    """

    def __init__(self):
        """
        Initializes the UserService with the User model and repository.

        :param User: The User model class.
        :type User: class
        """
        repository = UserRepository()
        super().__init__(User, repository)

    def get_user(self, email: str, session) -> bool:
        """
        Authenticate user against the database.

        :param email: The user's email.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: True if authentication is successful, False otherwise.
        :rtype: bool
        """
        user = self.repository.find_by_email(email, session)
        return user

    def create_user(self, data, session):
        """
        Creates and persists an instance of the model with the given data.

        :param data: The data to initialize the model instance.
        :type data: dict
        :param session: The database session.
        :type session: Session
        :return: The persisted instance of the model.
        :rtype: object
        """
        try:
            instance = self.model(**data)
            return self.repository.add(instance, session)
        except Exception as e:
            error_message = f"Error creating user: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def prepare_data_and_update(self, data, obj, session):
        """
        Create the data to update the user.

        :param data: The data to update the user.
        :type data: dict
        :param obj: The user object to update.
        :type obj: User
        :param session: The database session.
        :type session: Session
        :return: The updated user object.
        :rtype: User
        """
        try:
            role_service = RoleService()
            role = role_service.get_by_name(data["Role"], session)
            if not role:
                error_message = f"Role '{data['Role']}' not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)

            data = {"email_address": data["Email address"], "role_id": role.name}
            return self.repository.update_obj(obj.id, data, session)
        except Exception as e:
            error_message = f"Error preparing data and updating user: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def list_to_dict(self, user_list):
        """
        Converts a list of User objects to a dictionary.

        :param user_list: A list of User objects.
        :type user_list: list
        :return: A dictionary of User objects.
        :rtype: dict
        """
        user_dict = {}
        for client in user_list:
            user_dict[client.id] = client.to_dict()
        return user_dict

    def get_by_email(self, email, session):
        """Retrieve a user by email address."""
        user = self.repository.find_by_email(email, session)
        return user
