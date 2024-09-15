"""
Ce module définit la classe ContractStatus qui représente le statut d'un contrat dans la base de données.
"""

from sqlalchemy import Column, Integer, String

from src.models.base import Base


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
