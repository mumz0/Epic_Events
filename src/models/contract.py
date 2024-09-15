"""
Ce module définit la classe Contract qui représente un contrat dans la base de données.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class Contract(Base):
    """
    Cette classe représente un contrat dans la base de données.

    :param id: L'identifiant unique du contrat.
    :type id: int
    :param informations: Les informations relatives au contrat.
    :type informations: str
    :param sales_contact_id: L'identifiant de l'utilisateur responsable des ventes pour ce contrat.
    :type sales_contact_id: int
    :param price: Le prix du contrat.
    :type price: int
    :param Outstanding_balance: Le solde restant du contrat.
    :type Outstanding_balance: int
    :param creation_date: La date de création du contrat.
    :type creation_date: DateTime
    :param status_id: L'identifiant du statut du contrat.
    :type status_id: int
    """

    __tablename__ = "contract"

    id = Column(Integer, primary_key=True)
    informations = Column(String)
    sales_contact_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    price = Column(Integer)
    Outstanding_balance = Column(Integer)
    creation_date = Column(DateTime)
    status_id = Column(Integer, ForeignKey("contract_status.id"), nullable=False, default=1)

    status = relationship("ContractStatus", backref="contracts")
