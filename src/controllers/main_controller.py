"""This file defines the MainController class for initializing and running the application."""

import sys

import urwid

from src.controllers.auth_controller import AuthController
from src.controllers.user_controller import UserController
from src.views.main_view import MainView


class MainController:
    """
    MainController handles the initialization and running of the application.
    """

    def __init__(self, session):
        """
        Initializes the MainController with the session object.
        """
        self.session = session
        self.current_user = None
        self.loop = None
        self.response = None

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
        main_view = MainView()
        buttons, layout = main_view.starting_page_layout(">Welcome", ["Connect", "Quit"])

        urwid.connect_signal(buttons[0].base_widget, "click", lambda button: self.handle_button_pressed(self.handle_login_click))
        urwid.connect_signal(buttons[1].base_widget, "click", lambda button: self.handle_button_pressed(self.handle_exit_click))

        self.loop = urwid.MainLoop(layout)
        self.loop.run()

    def handle_button_pressed(self, func):
        """
        Handles the event when a button is pressed by executing the provided function.
        :param func: The function to be executed when the button is pressed.
        :type func: Callable
        """
        func()

    def handle_login_click(self):
        """
        Handles the login button click event.
        This method initializes the authentication process by creating a configuration
        dictionary with session, current user, event loop, success callback, and failure
        callback. It then creates an instance of AuthController with the configuration
        and calls the signin method to perform the login operation.
        Configuration:
        - session: The current session object.
        - current_user: The current user object.
        - loop: The event loop.
        - success_func: The function to call upon successful login.
        - failed_func: The function to call upon failed login, which displays a "Signin failed" message.
        """
        config = {
            "session": self.session,
            "current_user": self.current_user,
            "loop": self.loop,
            "success_func": self.menu,
            "failed_func": lambda: MainView().display_message("Signin failed."),
        }
        auth_controller = AuthController(config)
        auth_controller.signin()

    def menu(self):
        """
        Displays the main menu and sets up the button click handlers.
        This method creates the main menu layout using the `MainView` class and
        connects button click signals to their respective handlers. The first
        button is connected to the `user_menu_layout` method of the `UserController`
        class, and the second button is connected to the `handle_exit_click` method.
        The method then updates the screen and sets the main loop widget to the
        created layout.
        """
        buttons, layout = MainView().menu_view_layout(">Menu")
        urwid.connect_signal(
            buttons[0].base_widget,
            "click",
            lambda button: self.handle_button_pressed(UserController(self.session, self.current_user, self.loop).user_menu_layout),
        )
        urwid.connect_signal(buttons[1].base_widget, "click", lambda button: self.handle_button_pressed(self.handle_exit_click))
        urwid.connect_signal(buttons[1].base_widget, "click", lambda button: self.handle_button_pressed(self.handle_exit_click))
        self.loop.draw_screen()
        self.loop.widget = layout

    def handle_exit_click(self):
        """
        Handles the event when the exit button is clicked.
        This method will terminate the application.
        """
        sys.exit()
