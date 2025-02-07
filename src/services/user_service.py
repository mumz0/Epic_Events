"""This file defines the UserService class for handling operations related to User entities."""

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.base_service import BaseService


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
        :param password: The user's password.
        :type password: str
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
        instance = self.model(**data)
        return self.repository.add(instance, session)

    def list_to_dict(self, user_list):
        """
        Converts a list of User objects to a dictionary.

        :param user_list: A list of User objects.
        :type user_list: list
        :return: A dictionary of User objects.
        :rtype: dict
        """
        user_dict = {}
        for user in user_list:
            user_dict["Email address"] = user.email_address
        return user_dict
