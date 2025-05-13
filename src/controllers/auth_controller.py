# pylint: disable=W0104
"""
    This module contains the AuthController class, which is responsible for handling the authentication process.
"""

import logging
import sentry_sdk
import urwid

from src.controllers.base_controller import BaseController
from src.controllers.client_controller import ClientController
from src.controllers.contract_controller import ContractController
from src.controllers.event_controller import EventController
from src.controllers.user_controller import UserController
from src.models.role import Role, RoleEnum
from src.services.auth_service import AuthService
from src.views.base_view import BaseView


class AuthController(BaseController):
    """
    AuthController handles the authentication process for signing up and signing in users.
    """

    def __init__(self, session, base_view, current_user, history):
        super().__init__(session, base_view, current_user, history)
        self.current_user = current_user

    def create_admin_user(self):
        """
        Creates an admin user with a predefined password and admin role.
        """
        query = self.session.query(Role).filter_by(name=RoleEnum.ADMIN.value)
        admin_role_obj = query.first()
        if not admin_role_obj:
            raise ValueError("Admin role not found.")
        email, password = BaseView().admin_signup_view()
        AuthService(None).signup_process(email, password, admin_role_obj.name, self.session)

    def signin(self):
        """
        Handles the sign-in process for the user.

        This method sets up the login page layout using the AuthView class and connects the
        "click" signal of the login button to the handle_signin_button_pressed method. It
        then updates the screen and sets the current widget to the login page layout.
        """

        # Define the labels for the form
        button_labels = ["Sign In"]
        edit_labels = ["Email", "Password"]

        # Create the form layout
        layout_dict = self.base_view.create_form_layout(">Authentication", button_labels, edit_labels)

        # Connect the signal for the sign-in button
        urwid.connect_signal(
            layout_dict["buttons"][0],
            "click",
            lambda button: self.handle_auth_form_button_event(
                layout_dict)
            ),


        # Update the screen with the new layout
        self.base_view.update_screen(layout_dict["layout"])

    def show_expired_token_popup(self):
        """
        Displays a popup indicating that the user's session has expired and prompts them to reconnect.

        This method creates a popup with a message and an "OK" button. When the button is pressed,
        it triggers the `signin` method to handle the reconnection process. The popup is then
        displayed on the base view's screen.
        """
        popup, button = self.base_view.create_expired_token_popup()
        urwid.connect_signal(button, "click", lambda btn: self.signin())

        self.base_view.loop.widget = popup
        self.base_view.update_screen(popup)
            
    def handle_auth_form_button_event(self, layout_dict):
        """
        Handles the sign-in button press event by processing the provided email and password.
        :param email: The email address entered by the user.
        :type email: str
        :param password: The password entered by the user.
        :type password: str
        """
        self.current_user = AuthService(self.current_user).signin_process(
            layout_dict["edits"][0].get_edit_text(), layout_dict["edits"][1].get_edit_text(), self.session
        )
        sentry_sdk.capture_message(f"handle_auth_form_button_event: {str(self.current_user.id)}")
        self.menu(
                    "> Home",
                    [
                        ("Users", lambda: UserController(self.session, self.base_view, self.current_user, self.history).all_users()),
                        ("Clients", lambda: ClientController(self.session, self.base_view, self.current_user, self.history).all_clients()),
                        (
                            "Contracts",
                            lambda: ContractController(self.session, self.base_view, self.current_user, self.history).paginated_contracts_displayed(
                                "> Home > Contracts", "all"
                            ),
                        ),
                        (
                            "Events",
                            lambda: EventController(self.session, self.base_view, self.current_user, self.history).paginated_events_displayed(
                                "> Home > Events", "all"
                            ),
                        ),
                        (
                            "Exit",
                            lambda: BaseController(self.session, self.base_view, self.current_user, self.history).show_exit_confirmation()
                        ),
                    ],
                ),
        
