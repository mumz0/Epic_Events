"""
BaseController is an abstract base class that provides common functionality for controllers in the application.
"""

import sys

import urwid

from logger_file import logger


class BaseController:
    """
    BaseController is responsible for managing the interaction between the session,
    the base view, the current user, and the history of actions.
    """

    def __init__(self, session, base_view, current_user, history):

        self.session = session
        self.base_view = base_view
        self.current_user = current_user
        self.history = history

    # def show_expired_token_popup(self):
    #     """
    #     Displays a popup indicating that the user's session has expired and prompts them to reconnect.

    #     This method creates a popup with a messageand an "OK" button. When the button is pressed,
    #     it triggers the `handle_login` method to handle the reconnection process. The popup is then
    #     displayed on the base view's screen.
    #     """
    #     body = urwid.Text("Votre session a expiré. Veuillez vous reconnecter.")
    #     button = urwid.Button("OK", on_press=self.handle_login)
    #     popup = urwid.Filler(urwid.Pile([body, button]))
    #     self.base_view.loop.widget = popup
    #     self.base_view.update_screen()

    # def is_token_avaible(self):
    #     """
    #     Checks if the current user's token is available and valid.
    #     This method uses the AuthService to verify the token of the current user.
    #     If the token is not valid, it triggers a popup to notify the user about the expired token.
    #     :return: Always returns True.
    #     :rtype: bool
    #     """
    #     auth_service = AuthService(self.current_user)
    #     if not auth_service.verify_token():
    #         self.show_expired_token_popup()
    #     return True

    def handle_exit_click(self):
        """
        Handles the event when the exit button is clicked.
        This method will terminate the application.
        """
        sys.exit()

    # TODO: CREATE LAYOUT IN VIEW NOT HERE
    def show_exit_confirmation(self):
        """
        Displays a pop-up asking for exit confirmation.
        """
        yes_button = urwid.Button("Yes")
        no_button = urwid.Button("No")

        urwid.connect_signal(yes_button, "click", lambda button: self.handle_exit_click())
        urwid.connect_signal(no_button, "click", lambda button: self.remove_popup())

        pile = urwid.Pile([urwid.Text("Do you really want to exit?"), urwid.Columns([yes_button, no_button])])

        popup = urwid.Overlay(
            urwid.LineBox(pile),
            self.base_view.loop.widget,
            align="center",
            width=("relative", 50),
            valign="middle",
            height=("relative", 20),
        )

        # Ajouter le pop-up à l'historique
        self.history.append(self.base_view.loop.widget)

        self.base_view.loop.widget = popup
        self.base_view.update_screen(self.base_view.loop.widget)

    def remove_popup(self):
        """
        Removes the pop-up and returns to the previous screen.
        """
        if self.history:
            self.base_view.loop.widget = self.history.pop()
            self.base_view.update_screen(self.history[-1])

    def handle_button_pressed(self, func):
        """
        Handles the event when a button is pressed by executing the provided function.
        :param func: The function to be executed when the button is pressed.
        :type func: Callable
        """
        # logger.debug("Button pressed: Executing function %s", func.__name__)
        func()

    def handle_back_keypress(self, key):
        """
        Handles the back key press event, typically triggered by the 'esc' key.
        If the current widget is the first in the history, it shows the exit confirmation.
        Otherwise, it navigates back to the previous widget in the history.
        :param key: The key that was pressed.
        :type key: str
        """
        logger.info("ESC pressed: %s", self.history)
        if self.base_view.loop.widget == self.history[0]:
            self.show_exit_confirmation()
            return
        logger.debug(f"Key pressed: {key}")
        if key == "esc" and self.history:
            self.base_view.loop.widget = self.history.pop()
            logger.info("Returning to previous page: %s", self.base_view.loop.widget)
            if self.history:
                self.base_view.update_screen(self.history[-1])
            else:
                self.base_view.update_screen(self.base_view.loop.widget)

    def menu(self, title, menu_items):
        """
        Displays a menu with the given title and menu items.
        :param title: The title of the menu.
        :type title: str
        :param menu_items: A list of tuples where each tuple contains a label and a function to be called when the menu item is selected.
        :type menu_items: list of (str, callable)
        """
        logger.info(f"Displaying {title} menu")
        labels = [item[0] for item in menu_items]
        buttons, layout = self.base_view.create_menu_layout(title, labels)

        for button, (label, func) in zip(buttons, menu_items):
            logger.debug(f"Menu item: {label}")
            urwid.connect_signal(button.base_widget, "click", lambda button, handler=func: self.handle_button_pressed(handler))

        if "Home" in str(title):
            logger.info("Adding to history")
            self.history.append(layout)
            self.base_view.update_screen(self.history[-1])
        logger.info("Home" in title)
        logger.info("Not adding to history")
        self.base_view.update_screen(layout)

    def object_details_layout(self, title, item_label, objects_lst):
        """
        Creates and displays the layout for object details.
        :param title: The title of the object details frame.
        :type title: str
        :param item_label: The label of the item to find in the objects list.
        :type item_label: str
        :param objects_lst: The list of objects to search for the item.
        :type objects_lst: list
        """
        logger.info("Found label: %s", item_label)
        selected_object = None
        for obj in objects_lst:
            if obj.get_identifier() == item_label:
                logger.info("Found object: %s", obj.id)
                selected_object = obj
                break
        frame = self.base_view.create_object_details_frame(title, selected_object)
        self.history.append(frame)
        self.base_view.update_screen(frame)
