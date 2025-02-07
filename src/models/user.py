"""
Ce module définit la classe User qui représente un utilisateur dans la base de données.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class User(Base):
    """
    Cette classe représente un utilisateur dans la base de données.

    :param id: L'identifiant unique de l'utilisateur.
    :type id: int
    :param email_address: L'adresse email de l'utilisateur.
    :type email_address: str
    :param password: Le mot de passe de l'utilisateur.
    :type password: str
    :param role_id: L'identifiant du rôle associé à l'utilisateur.
    :type role_id: int
    :param role: Le rôle associé à l'utilisateur.
    :type role: Role
    """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email_address = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    role_id = Column(String, ForeignKey("role.name"))
    role = relationship("Role", back_populates="users")

    def create_user_obj(self, email_address, password, role_id):
        """
        Create a new User object.

        :param email_address: The email address of the user.
        :type email_address: str
        :param password: The password of the user.
        :type password: str
        :param role: The role of the user.
        :type role: Role
        :return: A new User object.
        :rtype: User
        """
        return User(email_address=email_address, password=password, role=role_id)

    def to_dict(self):
        """
        Converts the User object to a dictionary.

        :return: A dictionary representation of the User object.
        :rtype: dict
        """
        return {"Email address": self.email_address, "Role": self.role.name}

    def get_identifier(self):
        """
        Retrieve the identifier for the user.

        :return: The email address of the user.
        :rtype: str
        """
        return self.email_address
