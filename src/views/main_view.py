"""
MainView class provides methods to create and display different UI layouts using urwid.
"""

import os
import time

import click
import urwid

from ascii.ascii import Ascii


class MainView:
    """
    MainView class provides methods to create and manage the layout of the main interface for the Epic Events application.
    """

    def __init__(self):
        self.ascii_art = Ascii().epic_events()

    def starting_page_layout(self, title, item_labels):
        """
        Creates the layout for the starting page of the application.
        :param title: The title to be displayed at the top of the page.
        :type title: str
        :param item_labels: A list containing labels for the buttons.
        :type item_labels: list of str
        :return: A tuple containing the list of buttons and the framed menu layout.
        :rtype: tuple (list of urwid.Button, urwid.Widget)
        """
        os.system("cls" if os.name == "nt" else "clear")

        connect_button = self.create_button(item_labels[0])
        quit_button = self.create_button(item_labels[1])
        buttons = [connect_button, quit_button]

        title_widget = urwid.LineBox(urwid.Padding(urwid.Text(title, align="left"), left=2, right=4))
        body = [urwid.Text(self.ascii_art, align="center"), title_widget, urwid.Divider()]

        # Wrap buttons in Pile widget instead of Columns
        button_widgets = [urwid.AttrMap(button, None, focus_map="reversed") for button in buttons]
        body.extend(button_widgets)

        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        framed_menu = urwid.Frame(urwid.Padding(list_box, left=2, right=2))
        lined_framed_menu = urwid.LineBox(framed_menu)

        return buttons, lined_framed_menu

    def menu_view_layout(self, title):
        """
        Creates the layout for the menu view.
        This method clears the terminal screen, creates a title widget, and
        constructs a body with ASCII art, the title widget, and a divider.
        It then creates buttons for 'User', 'Clients', and 'Events', adds
        them to the body, and constructs a list box and framed menu layout.
        :param title: The title to be displayed in the menu.
        :type title: str
        :return: A tuple containing the list of buttons and the framed menu layout.
        :rtype: tuple(list, urwid.Widget)
        """
        os.system("cls" if os.name == "nt" else "clear")
        title_widget = urwid.LineBox(urwid.Padding(urwid.Text(title, align="left"), left=2, right=4))
        body = [urwid.Text(self.ascii_art, align="center"), title_widget, urwid.Divider()]

        # Create buttons
        user_button = self.create_button("User")
        clients_button = self.create_button("Clients")
        events_button = self.create_button("Events")

        # Add buttons to the body
        buttons = [
            urwid.AttrMap(user_button, None, focus_map="reversed"),
            urwid.AttrMap(clients_button, None, focus_map="reversed"),
            urwid.AttrMap(events_button, None, focus_map="reversed"),
        ]
        body.extend(buttons)

        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        framed_menu = urwid.Frame(urwid.Padding(list_box, left=2, right=2))
        lined_framed_menu = urwid.LineBox(framed_menu)
        return buttons, lined_framed_menu

    def create_button(self, label):
        """
        Creates a button with the given label.
        :param label: The text to display on the button.
        :type label: str
        :return: A button widget with the specified label.
        :rtype: urwid.Button
        """
        button = urwid.Button(label)
        return button

    def display_message(self, message):
        """
        Displays a message to the user using urwid and click.
        The message is displayed for two seconds before continuing.
        """

        # Display message using urwid
        text_widget = urwid.Text(message)
        fill = urwid.Filler(text_widget, "top")
        loop = urwid.MainLoop(fill)

        # Display message using click
        click.echo(message)

        # Run the loop for 2 seconds
        loop.screen.start()
        time.sleep(2)
        loop.screen.stop()
