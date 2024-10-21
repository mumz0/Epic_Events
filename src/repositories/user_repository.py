"""This file defines the UserRepository class for handling operations related to User entities."""

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
        Find a user by email and password.

        :param email: The user's email.
        :type email: str
        :param password: The user's password.
        :type password: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: The user if found, None otherwise.
        :rtype: User or None
        """
        return session.query(User).filter(User.email_address == email).first()

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
        user = session.query(User).get(user_id)
        user.token = token
        session.commit()
