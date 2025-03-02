"""This file defines the ContractRepository class for handling operations related to Contract entities."""

from src.models.contract import Contract
from src.repositories.base_repository import BaseRepository


class ContractRepository(BaseRepository):
    """
    ContractRepository handles operations related to Contract entities.

    :param BaseRepository: Inherits from BaseRepository to utilize common repository functionalities.
    :type BaseRepository: class
    """

    def __init__(self):
        """
        Initializes the ContractRepository with the Contract model.

        :param Contract: The Contract model class.
        :type Contract: class
        """
        super().__init__(Contract)

    def filter_by_sales_email_address(self, email: str, session) -> list:
        """
        Filter contracts by sales email address.

        :param email: The sales email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of contracts.
        :rtype: list
        """
        contracts = session.query(Contract).filter(Contract.sales_contact_id == email).all()
        return contracts

    def filter_by_client_email_address(self, email: str, session) -> list:
        """
        Filter contracts by client email address.

        :param email: The client email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of contracts.
        :rtype: list
        """
        contracts = session.query(Contract).filter(Contract.client_id == email).all()
        return contracts
