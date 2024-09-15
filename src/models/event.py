"""
Ce module définit la classe Event qui représente un événement dans la base de données.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from src.models.base import Base


class Event(Base):
    """
    Cette classe représente un événement dans la base de données.

    :param id: L'identifiant unique de l'événement.
    :type id: int
    :param name: Le nom de l'événement.
    :type name: str
    :param start_date: La date de début de l'événement.
    :type start_date: DateTime
    :param end_date: La date de fin de l'événement.
    :type end_date: DateTime
    :param location: Le lieu de l'événement.
    :type location: str
    :param attendees: Le nombre de participants à l'événement.
    :type attendees: int
    :param notes: Les notes associées à l'événement.
    :type notes: str
    :param client_id: L'identifiant du client associé à l'événement.
    :type client_id: int
    :param contract_id: L'identifiant du contrat associé à l'événement.
    :type contract_id: int
    :param support_user_id: L'identifiant de l'utilisateur de support associé à l'événement.
    :type support_user_id: int
    """

    __tablename__ = "event"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)

    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contract.id"), nullable=False)
    support_user_id = Column(Integer, ForeignKey("user.id"))
