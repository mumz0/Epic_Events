# pylint: disable=W0246
"""This file defines the UserController class for handling user-related operations."""

import logging
import sentry_sdk
import urwid

from src.controllers.base_controller import BaseController
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.base_service import BaseService
from src.services.user_service import UserService
from src.views.paginated_view import PaginatedView
from utils.decorators import require_valid_token


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

    @require_valid_token
    def all_users(self):
        """
        Retrieve and display all users.
        This method retrieves all user objects from the database, converts them to a dictionary format,
        and displays them in a paginated view. It also sets up the necessary signals for user interaction.
        """
        sentry_sdk.capture_message(f"all users: {str(self.current_user.id)}")
        
        user_objects = UserRepository().get_all(self.session)
        user_list_dict = UserService().list_to_dict(user_objects)
        paginated_view = PaginatedView(user_list_dict, "> Home > Users")
        paginated_view.loop = self.base_view.loop
        users_label = self.get_button_data_for_items(user_objects)
        buttons_label = {
            "users_label": users_label,
            "buttons": ["Previous", "Next"],
        }
        for permission in self.current_user.role.permissions:
            if permission.action == "user_create":
                buttons_label["buttons"].append("Create")

        layout, buttons = paginated_view.display_page(0, buttons_label)

        self.create_paginated_buttons_signal(paginated_view, buttons, user_objects)

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
        for button in buttons["buttons_items"]:
            selected_user = self.select_item_in_lst(user_objects, button.get_label())
            object_details_data = {
                "title": f"Home > Users > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": selected_user,
                "service": self,
                "buttons_label": [],
            }
            for permission in self.current_user.role.permissions:
                if permission.action == "user_update":
                    object_details_data["buttons_label"].append("Modify")
                if permission.action == "user_delete":
                    object_details_data["buttons_label"].append("Delete")

            urwid.connect_signal(
                button,
                "click",
                lambda button=button, selected_user=selected_user, object_details_data=object_details_data: self.object_details_layout(
                    f"Home > Client > {button.get_label()}", selected_user, self, object_details_data
                ),
            )

        button_actions = [
            ("Previous", paginated_view.previous_page()),
            ("Next", paginated_view.next_page()),
            ("Create", lambda: self.user_creation()),
        ]

        self.connect_button_signals(buttons, button_actions)

    def create_details_view_buttons_signal(self, buttons, user_object):
        """
        Connect signals to details view buttons for modifying or deleting a user.

        :param buttons: A dictionary of buttons with keys like 'modify_button' and 'delete_button'.
        :type buttons: dict
        :param user_object: The user object related to the details view.
        :type user_object: User
        """
        user_template_dict = user_object.to_dict()
        new_user_template_dict = BaseService(User).remove_attributes_from_object(user_template_dict, ["ID"])

        button_actions = [
            (
                "Modify",
                lambda: self.pre_filled_form_page(
                    f"Home > Users > {user_object.email_address} > Modify",
                    new_user_template_dict,
                    user_object,
                    UserService(),
                ),
            ),
            ("Delete", lambda: self.show_delete_confirmation(user_object, BaseService(User))),
        ]

        self.connect_button_signals(buttons, button_actions)

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
        response = AuthService(self.current_user).signup_process(
            layout_dict["edits"][0].get_edit_text(), layout_dict["edits"][1].get_edit_text(), layout_dict["edits"][2].get_edit_text(), self.session
        )

        if response:
            self.history.pop()
            self.base_view.update_screen(self.history[-1])
        else:
            popup, buttons = self.base_view.create_message_popup("User already exists. Please try again.")
            urwid.connect_signal(buttons[0], "click", lambda button: self.remove_popup())
            self.base_view.update_screen(popup)
