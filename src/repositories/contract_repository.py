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
