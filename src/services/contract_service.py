"""This file defines the ContractService class for handling operations related to Contract entities."""

from src.models.contract import Contract
from src.repositories.contract_repository import ContractRepository
from src.services.base_service import BaseService


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

    def list_to_dict(self, user_list):
        """
        Converts a list of User objects to a dictionary.

        :param user_list: A list of User objects.
        :type user_list: list
        :return: A dictionary of User objects.
        :rtype: dict
        """
        user_dict = {}
        for user in user_list:
            user_dict["Email address"] = user.email_address
        return user_dict
