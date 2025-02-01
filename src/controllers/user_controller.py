# pylint: disable=W0246
"""This file defines the UserController class for handling user-related operations."""

import urwid

from logger_file import logger
from src.controllers.base_controller import BaseController
from src.repositories.user_repository import UserRepository
from src.services.base_service import BaseService
from src.services.user_service import UserService
from src.views.paginated_view import PaginatedView


class UserController(BaseController):
    """
    This controller is responsible for managing user-related actions such as retrieving and displaying all users.
    It interacts with the database session, views, and user services to perform these operations.
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

    # def create_admin_user(self, session_obj):
    #     """
    #     Creates an admin user with a predefined password and admin role.

    #     :param session_obj: The database session object.
    #     :type session_obj: Session
    #     """
    #     admin_role = session_obj.query(Role).filter_by(name="admin").first()
    #     email, password = AuthView().signup_admin()
    #     AuthService(None).signup_process(email, password, admin_role, session_obj)

    def all_users(self):
        """
        Retrieve and display all users.
        This method retrieves all user objects from the database, converts them to a dictionary format,
        and displays them in a paginated view. It also sets up the necessary signals for user interaction.
        """
        user_objects = BaseService(self.current_user, UserRepository()).get_all(self.session)
        user_list_dict = UserService().list_to_dict(user_objects)
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
                lambda button=button: self.object_details_layout(f"Home > Users > {button.get_label()}", button.get_label(), user_objects),
            )

        logger.info("items: %s", paginated_view.items)
        self.history.append(layout)
        self.base_view.update_screen(layout)
