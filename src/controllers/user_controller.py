# pylint: disable=W0246
"""This file defines the UserController class for handling user-related operations."""

import urwid

from logger_file import logger
from src.controllers.base_controller import BaseController
from src.models.user import User
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
        logger.info("UserController init: %s", self.current_user)
        logger.info("Current user: %s", self.current_user)

    def all_users(self):
        """
        Retrieve and display all users.
        This method retrieves all user objects from the database, converts them to a dictionary format,
        and displays them in a paginated view. It also sets up the necessary signals for user interaction.
        """

        user_objects = UserRepository().get_all(self.session)
        user_list_dict = UserService().list_to_dict(user_objects)
        logger.info("All users: %s", user_list_dict)
        paginated_view = PaginatedView(user_list_dict, "> Home > Users")
        paginated_view.loop = self.base_view.loop
        users_label = self.get_button_data_for_items(user_objects)
        logger.info("users_label: %s", users_label)
        buttons_label = {
            "users_label": users_label,
            "buttons": ["Previous", "Next", "Create"],
        }
        layout, buttons = paginated_view.display_page(0, buttons_label)

        self.create_paginated_buttons_signal(paginated_view, buttons, user_objects)

        logger.info("items: %s", paginated_view.items)
        self.history.append(layout)
        self.base_view.update_screen(layout)
        logger.info("History:  Menu (%s)", len(self.history))

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
        for button in buttons["buttons_items"]:
            object_details_data = {
                "title": f"Home > Users > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": user_objects,
                "service": self,
                "buttons_label": ["Modify", "Delete"],
            }
            urwid.connect_signal(
                button,
                "click",
                lambda button=button, object_details_data=object_details_data: self.object_details_layout(
                    f"Home > Client > {button.get_label()}", button.get_label(), user_objects, self, object_details_data
                ),
            )
        urwid.connect_signal(buttons["other_buttons"][0], "click", lambda button=button: paginated_view.previous_page())
        urwid.connect_signal(buttons["other_buttons"][1], "click", lambda button=button: paginated_view.next_page())
        # if buttons["create_button"] is not None:
        urwid.connect_signal(buttons["other_buttons"][2], "click", lambda button=button: self.user_creation())

    def create_details_view_buttons_signal(self, buttons, user_object):
        """
        Connect signals to details view buttons for modifying or deleting a user.

        :param buttons: A dictionary of buttons with keys like 'modify_button' and 'delete_button'.
        :type buttons: dict
        :param user_object: The user object related to the details view.
        :type user_object: User
        """
        logger.info("Creating details view buttons signal")
        logger.info("Current user: %s", self.current_user)
        user_template_dict = user_object.to_dict()
        urwid.connect_signal(
            buttons[0],
            "click",
            lambda button: self.pre_filled_form_page(
                f"Home > Users > {user_object.email_address} > Modify", user_template_dict, user_object, UserService()
            ),
        )
        urwid.connect_signal(buttons[1], "click", lambda button: self.show_delete_confirmation(user_object, BaseService(User)))

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

        response = AuthService(self.current_user).signup_process(
            layout_dict["edits"][0].get_edit_text(), layout_dict["edits"][1].get_edit_text(), layout_dict["edits"][2].get_edit_text(), self.session
        )
        # TODO: Add redirect fonction after user creation
        if response:
            self.history.pop()
            self.base_view.update_screen(self.history[-1])
        else:
            logger.info("User creation failed")
