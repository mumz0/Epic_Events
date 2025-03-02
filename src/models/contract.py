"""
Ce module définit la classe Contract qui représente un contrat dans la base de données.
"""

import datetime
import uuid

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

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("client.email_address"), nullable=False)
    sales_contact_id = Column(String, ForeignKey("user.email_address"), nullable=False)
    price = Column(Integer)
    Outstanding_balance = Column(Integer)
    creation_date = Column(DateTime, default=datetime.datetime.now())
    status_id = Column(String, ForeignKey("contract_status.name"), nullable=False, default="Pending")

    status = relationship("ContractStatus", backref="contracts")
    client = relationship("Client", backref="contracts")

    def to_dict(self):
        """
        Converts the User object to a dictionary.

        :return: A dictionary representation of the User object.
        :rtype: dict
        """
        return {
            "ID": self.id,
            "Client Name": self.client.name,
            "Client Email address": self.client.email_address,
            "Client Phone": self.client.phone,
            "Client Compagny": self.client.compagny,
            "Price": self.price,
            "Outstanding balance": self.Outstanding_balance,
            "Creation date": self.creation_date,
            "Status": self.status_id,
            "Sales contact": self.sales_contact_id,
        }

    def get_identifier(self):
        """
        Retrieve the identifier for the user.

        :return: The email address of the user.
        :rtype: str
        """
        return self.client_id
