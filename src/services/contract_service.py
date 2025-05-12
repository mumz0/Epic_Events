"""This file defines the ContractService class for handling operations related to Contract entities."""

import string
import uuid

import sentry_sdk

from src.models.contract import Contract
from src.repositories.contract_repository import ContractRepository
from src.services.base_service import BaseService
from src.services.user_service import UserService


class ContractService(BaseService):
    """
    ContractService handles operations related to Contract entities.

    :param BaseService: Inherits from BaseService to utilize common service functionalities.
    :type BaseService: class
    """

    def __init__(self):
        """
        Initializes the ContractService with the Contract model.

        :param Contract: The Contract model class.
        :type Contract: class
        """
        repository = ContractRepository()
        super().__init__(Contract, repository)

    def list_to_dict(self, contract_list) -> dict:
        """
        Converts a list of Contract objects to a dictionary.

        :param contract_list: A list of Contract objects.
        :type contract_list: list
        :return: A dictionary of Contract objects.
        :rtype: dict
        """
        try:
            contract_dict = {}
            for contract in contract_list:
                contract_dict[contract.id] = contract.to_dict()
            return contract_dict
        except Exception as e:
            sentry_sdk.capture_message("Error converting contract list to dictionary")
            sentry_sdk.capture_exception(e)
            return {}

    def filter_by_sales_email_adress(self, email: str, session) -> list:
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
            return self.repository.filter_by_sales_email_address(email, session)
        except Exception as e:
            sentry_sdk.capture_message("Error filtering contracts by sales email address")
            sentry_sdk.capture_exception(e)
            return []

    def filter_by_email_adress(self, email: str, session) -> list:
        """
        Filter contracts by email address.

        :param email: The email address.
        :type email: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: A list of contracts.
        :rtype: list
        """
        try:
            return self.repository.filter_by_client_email_address(email, session)
        except Exception as e:
            sentry_sdk.capture_message("Error filtering contracts by email address")
            sentry_sdk.capture_exception(e)
            return []

    def prepare_data_and_update(self, data, obj, session) -> dict:
        """
        Create the data to update the contract.

        :param data: The data to update the contract.
        :type data: dict
        :param obj: The contract object to update.
        :type obj: Contract
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: The updated contract data.
        :rtype: dict
        """
        try:
            user = UserService().get_user(data["Sales contact"], session)
            if not user:
                error_message = "Sales contact not found"
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)

            data = {
                "price": data["Price"],
                "Outstanding_balance": data["Outstanding balance"],
                "status_id": data["Status"],
                "sales_contact_id": user.email_address,
            }
            return self.repository.update_obj(obj.id, data, session)
        except ValueError as e:
            raise e
        except Exception as e:
            sentry_sdk.capture_message("Error preparing data and updating contract")
            sentry_sdk.capture_exception(e)
            return {}

    def generate_uid(self, session, length=8) -> str:
        """
        Generate a unique identifier (UID) for a contract.

        This method generates a UID by creating a random UUID, converting it to an uppercase hexadecimal string,
        filtering out non-alphanumeric characters, and prefixing it with "CONTRACT". The generated UID is then
        checked against the database to ensure it is unique.

        :param session: The database session used to query the Contract table.
        :type session: sqlalchemy.orm.Session
        :param length: The length of the UID to be generated (excluding the "CONTRACT" prefix), defaults to 8.
        :type length: int, optional
        :return: A unique identifier for a contract.
        :rtype: str
        """
        try:
            while True:
                uid = uuid.uuid4().hex.upper()
                uid = "".join(filter(lambda x: x in string.ascii_uppercase + string.digits, uid))
                uid_with_prefix = f"CONTRACT{uid[:length]}"
                if not self.repository.find_existing_uid(session, uid_with_prefix):
                    return uid_with_prefix
        except Exception as e:
            sentry_sdk.capture_message("Error generating UID")
            sentry_sdk.capture_exception(e)
            return None

    def filtered_by_contract_signed_or_pending(self, session, is_signed: str) -> list:
        """
        Filter contracts by signed or not.

        :param session: The SQLAlchemy session.
        :type session: Session
        :param is_signed: Indicates if the contract is signed or not.
        :type is_signed: str
        :return: A list of contracts filtered by signed status.
        :rtype: list
        """
        try:
            return self.repository.filtered_by_contract_signed_or_pending(session, is_signed)
        except Exception as e:
            sentry_sdk.capture_message("Error filtering contracts by signed status")
            sentry_sdk.capture_exception(e)
            return []

    def filtered_by_contract_payed_or_not(self, session, is_payed: str) -> list:
        """
        Filter contracts by payed or not.

        :param session: The SQLAlchemy session.
        :type session: Session
        :param is_payed: Indicates if the contract is payed or not.
        :type is_payed: str
        :return: A list of contracts filtered by payed status.
        :rtype: list
        """
        try:
            return self.repository.filtered_by_contract_payed_or_not(session, is_payed)
        except Exception as e:
            sentry_sdk.capture_message("Error filtering contracts by payed status")
            sentry_sdk.capture_exception(e)
            return []

    def check_if_contract_is_signed(self, session, contract_id) -> bool:
        """
        Check if a contract is signed.

        :param session: The SQLAlchemy session.
        :type session: Session
        :param contract_id: The ID of the contract.
        :type contract_id: str
        :return: True if the contract is signed, False otherwise.
        :rtype: bool
        """
        try:
            contract = self.repository.get(contract_id, session)
            if contract is None:
                error_message = "Contract not found"
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)
            return contract.status_id == "Signed"
        except ValueError as e:
            raise e
        except Exception as e:
            sentry_sdk.capture_message("Error checking if contract is signed")
            sentry_sdk.capture_exception(e)
            return False
