"""This file defines the UserRepository class for handling operations related to User entities."""

import sentry_sdk

from src.models.user import User
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """
    UserRepository handles operations related to User entities.

    :param BaseRepository: Inherits from BaseRepository to utilize common repository functionalities.
    :type BaseRepository: class
    """

    def __init__(self):
        """
        Initializes the UserRepository with the User model.

        :param User: The User model class.
        :type User: class
        """
        super().__init__(User)

    def find_by_email(self, email: str, session):
        """
        Find a user by email.

        :param email: The user's email.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: The user if found, None otherwise.
        :rtype: User or None
        """
        try:
            user = session.query(User).filter(User.email_address == email).first()
            if not user:
                error_message = f"User with email {email} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)
            return user
        except Exception as e:
            error_message = f"Error finding user by email: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e

    def update_token(self, user_id: int, token: str, session):
        """
        Update the token for a user.

        :param user_id: The ID of the user.
        :type user_id: int
        :param token: The new token.
        :type token: str
        :param session: The SQLAlchemy session.
        :type session: Session
        """
        try:
            user = session.query(User).get(user_id)
            if not user:
                error_message = f"User with ID {user_id} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)
            user.token = token
            session.commit()
        except Exception as e:
            error_message = f"Error updating token for user ID {user_id}: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e

    def get_all(self, session):
        """
        Retrieves all instances from the model except admin user.

        :param session: The database session.
        :type session: Session
        :return: A list of all instances of the model.
        :rtype: list
        """
        try:
            users = session.query(self.model).filter(self.model.role_id != 1).all()
            return users
        except Exception as e:
            error_message = f"Error retrieving all users except admin: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from e
