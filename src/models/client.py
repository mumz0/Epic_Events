"""
Ce module définit la classe Client qui représente un client dans la base de données.
"""

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class Client(Base):
    """
    Cette classe représente un client dans la base de données.

    :param id: L'identifiant unique du client.
    :type id: int
    :param name: Le nom du client.
    :type name: str
    :param email: L'adresse email du client.
    :type email: str
    :param phone: Le numéro de téléphone du client.
    :type phone: str
    :param compagny: Le nom de la compagnie du client.
    :type compagny: str
    :param creation_date: La date de création du client.
    :type creation_date: DateTime
    :param last_update: La date de la dernière mise à jour du client.
    :type last_update: DateTime
    :param sales_contact_id: L'identifiant de l'utilisateur responsable des ventes pour ce client.
    :type sales_contact_id: int
    """

    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email_address = Column(String)
    phone = Column(String)
    compagny = Column(String)
    creation_date = Column(DateTime, default=datetime.datetime.now())
    last_update = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    sales_contact_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    sales_contact = relationship("User", backref="clients")

    # TODO: modify to include sales_contact_id name or email address
    def to_dict(self):
        """
        Converts the User object to a dictionary.

        :return: A dictionary representation of the User object.
        :rtype: dict
        """
        return {
            "Name": self.name,
            "Email address": self.email_address,
            "Phone": self.phone,
            "Compagny": self.compagny,
            "Creation date": self.creation_date,
            "Last update": self.last_update,
            "Sales contact": self.sales_contact_id,
        }

    def get_identifier(self):
        """
        Retrieve the identifier for the user.

        :return: The email address of the user.
        :rtype: str
        """
        return self.email_address
