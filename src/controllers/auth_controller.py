"""
    This module contains the AuthController class, which is responsible for handling the authentication process.
"""

import urwid

# from src.controllers.main_controller import MainController
from src.services.auth_service import AuthService
from src.services.role_service import RoleService
from src.views.auth_view import AuthView
from src.views.main_view import MainView


class AuthController:
    """
    AuthController handles the authentication process for signing up and signing in users.
    """

    def __init__(self, config):
        """
        Initializes the AuthController with the provided configuration.
        """
        self.session = config["session"]
        self.current_user = config["current_user"]
        self.loop = config["loop"]
        self.authentication_success = config["success_func"]
        self.authentication_failed = config["failed_func"]

    def signup(self):
        """Handles the signup process for a new user."""
        if not AuthService(self.current_user).check_permission_signup(self.session):
            print("Permission denied.")
            return

        roles = RoleService().get_all(self.session)
        email, password, selected_role = AuthView().signup(roles)
        AuthService(self.current_user).signup_process(email, password, selected_role, self.session)
        print("Has permission.")

    def signin(self):
        """
        Handles the sign-in process for the user.

        This method sets up the login page layout using the AuthView class and connects the
        "click" signal of the login button to the handle_signin_button_pressed method. It
        then updates the screen and sets the current widget to the login page layout.

        """
        layout_dict = AuthView().login_page_layout(">Authentication")
        urwid.connect_signal(
            layout_dict["button"], "click", lambda button: self.handle_signin_button_pressed(layout_dict["email"], layout_dict["password"])
        )
        self.loop.draw_screen()
        self.loop.widget = layout_dict["layout"]

    def handle_signin_button_pressed(self, email, password):
        """
        Handles the sign-in button press event by processing the provided email and password.
        :param email: The email address entered by the user.
        :type email: str
        :param password: The password entered by the user.
        :type password: str
        """
        email = email.get_edit_text()
        password = password.get_edit_text()
        self.current_user = AuthService(self.current_user).signin_process(email, password, self.session)

        if self.current_user:
            self.authentication_success()
        else:
            self.authentication_failed()

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
            MainView().display_message("Signin successful.")
        else:
            MainView().display_message("Signin failed.")
