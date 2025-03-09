# pylint: disable=useless-parent-delegation
"""This file defines the MainController class for initializing and running the application."""

import urwid
from sentry_sdk.integrations.serverless import serverless_function

from src.controllers.auth_controller import AuthController
from src.controllers.base_controller import BaseController


class MainController(BaseController):
    """
    MainController handles the initialization and running of the application.
    """

    def __init__(self, session, base_view, current_user, history):
        super().__init__(session, base_view, current_user, history)

    def run_application(self):
        """
        Initializes and runs the main application loop.
        This method sets up the main view, creates the layout with buttons, and connects
        the button click signals to their respective handlers. It then starts the urwid
        main loop to run the application.
        The main view displays a welcome message and two buttons: "Connect" and "Quit".
        - "Connect" button triggers the handle_login_click handler.
        - "Quit" button triggers the handle_exit_click handler.
        """

        self.connect()

    @serverless_function
    def connect(self):
        """
        Establishes the connection by setting up the authentication controller and the main menu layout.
        This method initializes the authentication controller with the current session, base view, current user, and history.
        It then creates the main menu layout with "Connect" and "Quit" buttons. Signals are connected to these buttons to
        handle their respective click events. The main loop is initialized and started.
        """
        auth_controller = AuthController(self.session, self.base_view, self.current_user, self.history)
        buttons, layout = self.base_view.create_menu_layout(">Welcome", ["Connect", "Quit"])

        urwid.connect_signal(buttons[0].base_widget, "click", lambda button: self.handle_button_pressed(auth_controller.signin))
        urwid.connect_signal(buttons[1].base_widget, "click", lambda button: self.handle_button_pressed(self.handle_exit_click))

        self.base_view.init_main_loop(layout, lambda button: self.handle_back_keypress("esc"))

        self.base_view.loop.run()
