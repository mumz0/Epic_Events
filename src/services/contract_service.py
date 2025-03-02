"""This file defines the ContractService class for handling operations related to Contract entities."""

from logger_file import logger
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

    def get_contract(self, email: str, session) -> bool:
        """
        Authenticate user against the database.

        :param email: The user's email.
        :type email: str
        :param password: The user's password.
        :type password: str
        :param session: The SQLAlchemy session.
        :type session: Session
        :return: True if authentication is successful, False otherwise.
        :rtype: bool
        """
        user = self.repository.find_by_email(email, session)
        return user

    def list_to_dict(self, contract_list):
        """
        Converts a list of User objects to a dictionary.

        :param user_list: A list of User objects.
        :type user_list: list
        :return: A dictionary of User objects.
        :rtype: dict
        """
        user_dict = {}
        for contract in contract_list:
            user_dict["ID"] = contract.id
        return user_dict

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
        return self.repository.filter_by_sales_email_address(email, session)

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
        return self.repository.filter_by_client_email_address(email, session)

    def prepare_data_and_update(self, data, obj, session):
        """
        Create the data to update the user.

        :param data: The data to update the user.
        :type data: dict
        :return: The data to update the user.
        :rtype: dict
        """
        for attr, value in data.items():
            logger.info(f"{attr}: {value}")
        user = UserService().get_user(data["Sales contact"], session)
        if not user:
            raise ValueError(f"Contact Sales '{data['Sales contact']}' not found.")

        data = {
            "price": data["Price"],
            "Outstanding_balance": data["Outstanding balance"],
            "status_id": data["Status"],
            "sales_contact_id": user.email_address,
        }
        return self.repository.update_obj(obj.id, data, session)
