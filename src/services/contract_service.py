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
