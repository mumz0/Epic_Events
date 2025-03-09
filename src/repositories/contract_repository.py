"""This file defines the ContractRepository class for handling operations related to Contract entities."""

import sentry_sdk

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
        try:
            contracts = session.query(Contract).filter(Contract.sales_contact_id == email).all()
            return contracts
        except Exception as e:
            error_message = f"Error filtering contracts by sales email address: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

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
        try:
            contracts = session.query(Contract).filter(Contract.client_id == email).all()
            return contracts
        except Exception as e:
            error_message = f"Error filtering contracts by client email address: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def filtered_by_contract_signed_or_pending(self, session, issigned: str) -> list:
        """
        Filter contracts by signed or not.

        :param session: The SQLAlchemy session.
        :type session: Session
        :param issigned: The signed status.
        :type issigned: str
        :return: A list of contracts.
        :rtype: list
        """
        try:
            contracts = session.query(Contract).filter(Contract.status_id == issigned).all()
            return contracts
        except Exception as e:
            error_message = f"Error filtering contracts by signed status: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def filtered_by_contract_payed_or_not(self, session, is_payed: bool) -> list:
        """
        Filter contracts by payed or not.

        :param session: The SQLAlchemy session.
        :type session: Session
        :param is_payed: Boolean indicating if the contract is payed or not.
        :type is_payed: bool
        :return: A list of contracts.
        :rtype: list
        """
        try:
            if is_payed is True:
                contracts = session.query(Contract).filter(Contract.Outstanding_balance == Contract.price).all()
            elif is_payed is False:
                contracts = session.query(Contract).filter(Contract.Outstanding_balance != Contract.price).all()
            else:
                error_message = "The value must be a boolean."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)
            return contracts
        except Exception as e:
            error_message = f"Error filtering contracts by payed status: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)
