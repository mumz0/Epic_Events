"""
    This module contains the AuthController class, which is responsible for handling the authentication process.
"""

import urwid

from logger_file import logger
from src.controllers.base_controller import BaseController
from src.controllers.user_controller import UserController
from src.services.auth_service import AuthService


class AuthController(BaseController):
    """
    AuthController handles the authentication process for signing up and signing in users.
    """

    def __init__(self, session, base_view, current_user, history):
        super().__init__(session, base_view, current_user, history)
        logger.info("AuthController: %s", self.session)
        self.current_user = None

    # def signup(self):
    #     """Handles the signup process for a new user."""
    #     if not AuthService(self.current_user).check_permission_signup(self.session):
    #         print("Permission denied.")
    #         return

    #     roles = RoleService().get_all(self.session)
    #     email, password, selected_role = AuthView().signup(roles)
    #     AuthService(self.current_user).signup_process(email, password, selected_role, self.session)
    #     print("Has permission.")

    def signin(self):
        """
        Handles the sign-in process for the user.

        This method sets up the login page layout using the AuthView class and connects the
        "click" signal of the login button to the handle_signin_button_pressed method. It
        then updates the screen and sets the current widget to the login page layout.
        """
        logger.info("run_main_loop")
        logger.info(self.base_view.loop)

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
                layout_dict,
                self.menu(
                    "> Home",
                    [
                        ("Users", UserController(self.session, self.base_view, self.current_user, self.history).all_users),
                        ("Clients", None),
                        ("Contracts", None),
                        ("Events", None),
                    ],
                ),
            ),
        )

        # Update the screen with the new layout
        self.base_view.update_screen(layout_dict["layout"])
        logger.info("signin")
        logger.info(self.base_view.loop)

    def handle_auth_form_button_event(self, layout_dict, redirect_func):
        """
        Handles the sign-in button press event by processing the provided email and password.
        :param email: The email address entered by the user.
        :type email: str
        :param password: The password entered by the user.
        :type password: str
        """
        logger.info("Submit button clicked")
        self.current_user = AuthService(self.current_user).signin_process(
            layout_dict["edits"][0].get_edit_text(), layout_dict["edits"][1].get_edit_text(), self.session
        )
        redirect_func()

    def authentication_process(self):
        """
        Handles the authentication process for the user.
        This method attempts to sign in the user by calling the `signin` method.
        If the sign-in is successful, it sets the `current_user` attribute to the
        signed-in user and displays a success message. If the sign-in fails, it
        displays a failure message.

        """
        self.signin()
        if self.current_user:
            self.base_view.display_message("Signin successful.")
        else:
            self.base_view.display_message("Signin failed.")
