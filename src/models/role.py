"""
Ce module définit la classe Role qui représente un rôle dans la base de données.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class Role(Base):
    """
    Cette classe représente un rôle dans la base de données.

    :param id: L'identifiant unique du rôle.
    :type id: int
    :param name: Le nom du rôle.
    :type name: str
    :param users: La liste des utilisateurs associés à ce rôle.
    :type users: list
    :param permissions: La liste des permissions associées à ce rôle.
    :type permissions: list
    """

    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="role_permission", backref="roles")
