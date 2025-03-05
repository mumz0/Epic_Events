"""
This module defines the BaseView class, which provides methods for creating and managing
a text-based user interface using the urwid library. The class includes methods for
initializing the main loop, updating the screen, creating buttons and layouts, clearing
the screen, and displaying messages.
"""

import os
import time
from typing import List

import click
import urwid

from ascii.ascii import Ascii


class BaseView:
    """
    BaseView class for initializing the view with ASCII art and event loop.
    """

    def __init__(self):

        self.ascii_art = Ascii().epic_events()
        self.loop = None

    def admin_signup_view(self):
        """
        Admin signup view that prompts the user for email and password, returning them as a tuple.

        :returns: A tuple containing the user's email and password.
        :rtype: tuple
        """
        email_edit = input("Email: ")
        password_edit = input("Password: ")
        return email_edit, password_edit

    def init_main_loop(self, layout, unhandled_input):
        """
        Initialize the main loop for the application.

        This method sets up the main loop using the provided layout and
        unhandled input handler.

        :param layout: The layout to be used for the main loop.
        :type layout: urwid.Widget
        :param unhandled_input: A function to handle unhandled input events.
        :type unhandled_input: callable
        """
        self.loop = urwid.MainLoop(layout, unhandled_input=unhandled_input)

    def update_screen(self, layout):
        """
        Update the screen with the given layout.

        This method updates the current screen layout by setting the loop's widget
        to the provided layout, clearing the screen, and then drawing the new screen.

        :param layout: The new layout to be displayed on the screen.
        :type layout: urwid.Widget
        """
        self.loop.widget = layout
        self.loop.screen.clear()
        self.loop.draw_screen()

    def create_button(self, label: str):
        """
        Create a button with the given label and optional on_press callback.

        :param label: The text label for the button.
        :type label: str
        :param on_press: Optional callback function to be called when the button is pressed.
        :type on_press: function, optional
        :return: The created button.
        :rtype: urwid.Button
        """
        button = urwid.Button(label)
        return button

    def clear_screen(self):
        """Clears the terminal screen based on the OS."""
        os.system("cls" if os.name == "nt" else "clear")

    def create_header_body(self, title: str) -> List[urwid.Widget]:
        """
        Creates the header section, which includes a title widget and an ASCII art logo.
        :param title: The title to be displayed in the menu.
        :type title: str
        :return: A list of widgets representing the header body.
        :rtype: list
        """
        logo = urwid.Text(self.ascii_art, align="center")
        title_widget = urwid.LineBox(urwid.Padding(urwid.Text(title, align="left"), left=2, right=4))
        header_body = [logo, title_widget, urwid.Divider()]
        return header_body

    def create_menu_body(self, header_body: List[urwid.Widget], button_labels: List[str]) -> List[urwid.Widget]:
        """
        Creates the body of the layout, including the header and the buttons.
        :param header_body: The list of header widgets to include in the body.
        :param button_labels: A list of labels for the buttons.
        :return: A list of body widgets, including the header and buttons.
        :rtype: list
        """
        buttons = self.create_buttons(button_labels)
        # Combine header_body and buttons into the final body
        body = header_body + buttons
        return body, buttons

    def create_buttons(self, button_labels: List[str]) -> List[urwid.Widget]:
        """
        Creates a list of buttons based on the provided labels.
        :param button_labels: A list of labels for the buttons.
        :type button_labels: list
        :return: A list of button widgets.
        :rtype: list
        """
        return [urwid.AttrMap(self.create_button(label), None, focus_map="reversed") for label in button_labels]

    def create_frame(self, body: List[urwid.Widget]) -> urwid.Widget:
        """
        Wraps the body in a frame layout with padding.
        :param body: The body widget list to be framed.
        :type body: list
        :return: The framed menu layout.
        :rtype: urwid.Widget
        """
        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        return urwid.Frame(urwid.Padding(list_box, left=2, right=2))

    def create_menu_layout(self, title: str, button_labels: List[str]):
        """
        Creates the layout for the menu view, including the header, body, and buttons.
        :param title: The title to be displayed in the menu.
        :type title: str
        :param button_labels: A list of labels for the buttons.
        :type button_labels: list
        :return: A tuple containing the list of buttons and the framed menu layout.
        :rtype: tuple(list, urwid.Widget)
        """
        self.clear_screen()

        header_body = self.create_header_body(title)
        body, buttons = self.create_menu_body(header_body, button_labels)
        layout = self.create_frame(body)

        return buttons, layout

    def create_form_layout(self, title: str, button_labels: List[str], edit_labels: List[str]):
        """
        Creates a form page with a given title, button labels, and edit labels.
        :param title: The title of the form page.
        :type title: str
        :param button_labels: A list of labels for the buttons.
        :type button_labels: list
        :param edit_labels: A list of labels for the edit fields.
        :type edit_labels: list
        :return: A dictionary containing the edit inputs, buttons, and the layout of the form page.
        :rtype: dict
        """
        title_widget = urwid.LineBox(urwid.Padding(urwid.Text(title, align="left"), left=2, right=4))
        edits = [urwid.Edit(f"{label}: ") for label in edit_labels]
        buttons = [urwid.Button(label) for label in button_labels]

        body = (
            [
                urwid.Text(self.ascii_art, align="center"),
                title_widget,
                urwid.Divider(),
            ]
            + edits
            + [urwid.AttrMap(button, None, focus_map="reversed") for button in buttons]
        )

        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        framed_menu = urwid.Frame(urwid.Padding(list_box, left=2, right=2))

        layout_dict = {"edits": edits, "buttons": buttons, "layout": framed_menu}
        return layout_dict

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

    def create_card(self, obj):
        """
        Creates a card with urwid displaying the information of user_list.
        :param user_list: List of user information to display.
        :type user_list: list
        """
        card_info = []
        card_data_dict = obj.to_dict()
        for key, value in card_data_dict.items():
            user_info = f"{key}: {str(value)}"
            card_info.append(user_info)

        card_text = "\n".join(card_info)
        card = urwid.LineBox(urwid.Padding(urwid.Text(card_text), left=2, right=2))
        pile = urwid.Pile([card])
        card = urwid.Filler(pile, valign="top")
        return card

    def create_object_details_frame(self, title, selected_object, buttons_labels):
        """
        Create a frame displaying details for a given object.
        This method first creates a card for the selected object (if provided),
        then composes a header. Both the card and header elements are added to a frame,
        which is returned as the resulting widget.
        :param title: A string representing the title to be displayed in the header.
        :param selected_object: The object for which to create a card. If None,
            no card will be generated.
        :return: A frame widget containing the header and the object's details.
        """
        card = urwid.Text("")
        if selected_object:
            card = self.create_card(selected_object)

        header_body = self.create_header_body(title)
        body = header_body + [card]
        buttons = []
        for button_label in buttons_labels["buttons_label"]:
            button = self.create_button(button_label)
            buttons.append(button)
            body.append(button)
        frame = self.create_frame(body)
        # buttons = {"modify_button": buttons[0], "delete_button": buttons[1]}
        return frame, buttons

    def create_pre_filled_form_page(self, object_template, title):
        """
        Create a pre-filled form page with the given object template and title.

        :param object_template: The template object to pre-fill the form fields.
        :type object_template: dict
        :param title: The title of the form page.
        :type title: str
        :return: A tuple containing the layout and the button.
        :rtype: tuple
        """
        header_body = self.create_header_body(title)

        edit_widgets = []
        for key, value in object_template.items():
            edit_widgets.append(urwid.Edit(f"{key}: ", str(value)))

        save_button = urwid.Button("Save")
        body = header_body + edit_widgets + [urwid.Divider(), save_button]
        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        frame = urwid.Frame(body=list_box)
        layout_dict = {"edits": edit_widgets, "buttons": save_button, "layout": frame}
        return layout_dict

    def create_delete_confirmation_popup_layout(self):
        """
        Create a confirmation popup layout to confirm item deletion.
        """
        yes_button = urwid.Button("Yes")
        no_button = urwid.Button("No")
        buttons = [yes_button, no_button]
        pile = urwid.Pile(
            [
                urwid.Text("Do you really want to delete this item?"),
                urwid.Columns([yes_button, no_button]),
            ]
        )

        popup = urwid.Overlay(
            urwid.LineBox(pile),
            self.loop.widget,
            align="center",
            width=("relative", 50),
            valign="middle",
            height=("relative", 20),
        )
        return popup, buttons
