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
    email_address = Column(String)
    password = Column(String)
    role_id = Column(Integer, ForeignKey("role.id"))
    role = relationship("Role", back_populates="users")
