"""
Ce module définit la classe ContractStatus qui représente le statut d'un contrat dans la base de données.
"""

from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates

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
    name = Column(String, nullable=False)

    @validates("name")
    def validate_name(self, _key, name):
        """
        Validates the name of the role.

        :param name: The name of the role.
        :type name: str
        :return: The name of the role.
        :rtype: str
        """
        if name not in {ContractStatusEnum.value for contract_status in ContractStatusEnum}:
            raise ValueError("Invalid contract status name.")
        return name
