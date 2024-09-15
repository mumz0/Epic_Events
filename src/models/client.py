"""
Ce module définit la classe Client qui représente un client dans la base de données.
"""

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
    email = Column(String)
    phone = Column(String)
    compagny = Column(String)
    creation_date = Column(DateTime)
    last_update = Column(DateTime)
    sales_contact_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    sales_contact = relationship("User", backref="clients")
