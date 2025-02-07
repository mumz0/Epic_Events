# pylint: disable=W0246
"""This file defines the UserController class for handling user-related operations."""

import urwid

from logger_file import logger
from src.controllers.base_controller import BaseController
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
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

        self.create_paginated_buttons_signal(paginated_view, buttons, user_objects)

        logger.info("items: %s", paginated_view.items)
        self.history.append(layout)
        self.base_view.update_screen(layout)

    def create_paginated_buttons_signal(self, paginated_view, buttons, user_objects):
        """
        Creates and connects signals to handle user interactions with paginated buttons.

        :param paginated_view: The paginated view object responsible for handling page interactions.
        :type paginated_view: PaginatedView
        :param buttons: A dictionary containing the buttons to which signals will be attached,
            with keys such as "buttons_items", "previous_button", "next_button", and "create_button".
        :type buttons: dict
        :param user_objects: A collection of user-related objects to be displayed or handled when a button is clicked.
        :type user_objects: list
        """

        urwid.connect_signal(paginated_view.search_edit, "change", paginated_view.handle_search_change)
        for button in buttons["buttons_items"]:
            urwid.connect_signal(
                button,
                "click",
                lambda button=button: self.object_details_layout(f"Home > Users > {button.get_label()}", button.get_label(), user_objects),
            )
        urwid.connect_signal(buttons["previous_button"], "click", lambda button=button: paginated_view.previous_page())
        urwid.connect_signal(buttons["next_button"], "click", lambda button=button: paginated_view.next_page())
        # if buttons["create_button"] is not None:
        urwid.connect_signal(buttons["create_button"], "click", lambda button=button: self.user_creation())

    def user_creation(self):
        """
        Create a new user by presenting a form to collect email, password, and role information.

        This function displays a form with fields for email, password, and user role. Once the form is submitted,
        it triggers a handler to process the user creation event and logs the action.
        :param self: Reference to the current instance of the class.
        :type self: object
        """
        # Define the labels for the form
        button_labels = ["Create User"]
        edit_labels = ["Email: ", "Password: ", "Role (management, sales, support)"]

        # Create the form layout
        layout_dict = self.base_view.create_form_layout("Home > Users > Create", button_labels, edit_labels)

        # Connect the signal for the create user button
        urwid.connect_signal(
            layout_dict["buttons"][0],
            "click",
            lambda button: self.handle_user_creation_button_event(layout_dict),
        )
        self.history.append(layout_dict["layout"])
        self.base_view.update_screen(layout_dict["layout"])
        logger.info("Create User view")
        logger.info(self.base_view.loop)

    def handle_user_creation_button_event(self, layout_dict):
        """
        Handle the user creation button event by processing the user's email, password, and role,
        then optionally invoking a redirection function.

        :param layout_dict: A dictionary containing UI elements for fetching user input fields
            (e.g., email, password, role_name).
        :type layout_dict: dict
        :param redirect_func: A callable function to redirect after successful user creation, or None.
        :type redirect_func: callable, optional
        """
        logger.info("Submit button clicked")
        logger.info(
            "email: %s, password: %s, role_name: %s",
            layout_dict["edits"][0].get_edit_text(),
            layout_dict["edits"][1].get_edit_text(),
            layout_dict["edits"][2].get_edit_text(),
        )

        AuthService(self.current_user).signup_process(
            layout_dict["edits"][0].get_edit_text(), layout_dict["edits"][1].get_edit_text(), layout_dict["edits"][2].get_edit_text(), self.session
        )
        # TODO: Add redirect fonction after user creation
