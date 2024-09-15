"""
Ce module définit la classe RolePermission qui représente l'association entre les rôles et les permissions dans la base de données.
"""

from sqlalchemy import Column, ForeignKey, Integer

from src.models.base import Base


class RolePermission(Base):
    """
    Cette classe représente l'association entre les rôles et les permissions dans la base de données.

    :param id: L'identifiant unique de l'association rôle-permission.
    :type id: int
    :param role: L'identifiant du rôle associé.
    :type role: int
    :param permission: L'identifiant de la permission associée.
    :type permission: int
    """

    __tablename__ = "role_permission"

    id = Column(Integer, primary_key=True)
    role = Column("role_id", Integer, ForeignKey("role.id"))
    permission = Column("permission_id", Integer, ForeignKey("permission.id"))
