# pylint: disable=W0246
"""This file defines the ContractController class for handling user-related operations."""

import urwid

from logger_file import logger
from services.contract_service import ContractService
from src.controllers.base_controller import BaseController
from src.repositories.user_repository import UserRepository
from src.services.base_service import BaseService
from src.views.paginated_view import PaginatedView


class ContractController(BaseController):
    """
    This controller is responsible for managing contract-related actions such as retrieving and displaying all users.
    It interacts with the database session, views, and contract services to perform these operations.
    """

    def __init__(self, session, base_view, current_user, history):
        """
        Initialize the UserController.

        :param session: The current database session.
        :type session: sqlalchemy.orm.session.Session
        :param base_view: The base view for the controller.
        :type base_view: BaseView
        :param current_user: The currently logged-in user.
        :type current_user: User
        :param history: The history of user actions.
        :type history: History
        """
        super().__init__(session, base_view, current_user, history)

    def all_contracts(self):
        """
        Retrieve and display all users.
        This method retrieves all contract objects from the database, converts them to a dictionary format,
        and displays them in a paginated view. It also sets up the necessary signals for contract interaction.
        """
        user_objects = BaseService(self.current_user, UserRepository()).get_all(self.session)
        user_list_dict = ContractService().list_to_dict(user_objects)
        logger.info("All users: %s", user_list_dict)
        paginated_view = PaginatedView(user_list_dict, "> Home > Users")
        paginated_view.loop = self.base_view.loop
        layout, buttons = paginated_view.display_page(0)

        # TODO: Put signals in view
        urwid.connect_signal(paginated_view.search_edit, "change", paginated_view.handle_search_change)
        for button in buttons:
            urwid.connect_signal(
                button,
                "click",
                lambda button=button: self.object_details_layout(f"Home > Contracts > {button.get_label()}", button.get_label(), user_objects),
            )

        logger.info("items: %s", paginated_view.items)
        self.history.append(layout)
        self.base_view.update_screen(layout)
