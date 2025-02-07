"""
Ce module définit la classe ContractStatus qui représente le statut d'un contrat dans la base de données.
"""

from enum import Enum as PyEnum

from sqlalchemy import Column, Enum, Integer

from src.models.base import Base


class ContractStatusEnum(PyEnum):
    """
    This enumeration defines possible statuses a contract can have.
    """

    PENDING = "Pending"
    SIGNED = "Signed"


class ContractStatus(Base):
    """
    Cette classe représente le statut d'un contrat dans la base de données.

    :param id: L'identifiant unique du statut de contrat.
    :type id: int
    :param name: Le nom du statut de contrat (par exemple, 'pending', 'signed').
    :type name: str
    """

    __tablename__ = "contract_status"

    id = Column(Integer, primary_key=True)

    # pending, signed
    name = Column(Enum(ContractStatusEnum), nullable=False)
