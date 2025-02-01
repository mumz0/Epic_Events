# pylint: disable=W0246
"""This file defines the ClientController class for handling client-related operations."""

import urwid

from logger_file import logger
from src.controllers.base_controller import BaseController
from src.repositories.client_repository import ClientRepository
from src.services.base_service import BaseService
from src.services.client_service import ClientService
from src.views.paginated_view import PaginatedView


class ClientController(BaseController):
    """
    This controller is responsible for managing client-related actions such as retrieving and displaying all users.
    It interacts with the database session, views, and client services to perform these operations.
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

    def all_clients(self):
        """
        Fetch and display all clients in a paginated view.
        converts them to dictionary format using the ClientService, and displays them
        using a paginated view. It sets up signal connections for search functionality
        and button clicks, and updates the view history and screen layout.
        """
        client_objects = BaseService(self.current_user, ClientRepository()).get_all(self.session)
        client_list_dict = ClientService().list_to_dict(client_objects)
        logger.info("All users: %s", client_list_dict)
        paginated_view = PaginatedView(client_list_dict, "> Home > Clients")
        paginated_view.loop = self.base_view.loop
        layout, buttons = paginated_view.display_page(0)

        # TODO: Put signals in view
        urwid.connect_signal(paginated_view.search_edit, "change", paginated_view.handle_search_change)
        for button in buttons:
            urwid.connect_signal(
                button,
                "click",
                lambda button=button: self.object_details_layout(f"Home > Users > {button.get_label()}", button.get_label(), client_objects),
            )

        logger.info("items: %s", paginated_view.items)
        self.history.append(layout)
        self.base_view.update_screen(layout)
