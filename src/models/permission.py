"""
Ce module définit la classe Permission qui représente une permission dans la base de données.
"""

from sqlalchemy import Column, String

from src.models.base import Base


class Permission(Base):
    """
    Cette classe représente une permission dans la base de données.

    :param id: L'identifiant unique de la permission.
    :type id: int
    :param action: L'action autorisée par la permission (par exemple, 'create', 'read', 'update', 'delete').
    :type action: str
    :param entity: L'entité sur laquelle l'action est autorisée (par exemple, 'client', 'contract', 'evenement').
    :type entity: str
    """

    __tablename__ = "permission"

    # id = Column(Integer, primary_key=True)
    action = Column(String, primary_key=True, nullable=False)
