"""
Ce module définit la classe Role qui représente un rôle dans la base de données.
"""

from enum import Enum as PyEnum

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, validates

from src.models.base import Base


class RoleEnum(PyEnum):
    """
    This enumeration defines possible roles a user can have.
    """

    ADMIN = "admin"
    SALES = "sales"
    SUPPORT = "support"
    MANAGEMENT = "management"


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

    # id = Column(Integer, unique=True)
    name = Column(String, primary_key=True, unique=True, nullable=False)
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="role_permission", backref="roles")

    @validates("name")
    def validate_name(self, _key, name):
        """
        Validates the name of the role.

        :param name: The name of the role.
        :type name: str
        :return: The name of the role.
        :rtype: str
        """
        if name not in {role.value for role in RoleEnum}:
            raise ValueError("Invalid role name.")
        return name
