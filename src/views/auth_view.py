"""
This module contains the AuthView class which is responsible for displaying the authentication views.
"""

import os

import click
import urwid

from ascii.ascii import Ascii


class AuthView:
    """
    AuthView displays the authentication views.
    """

    def __init__(self):
        self.ascii_art = Ascii().epic_events()
        self.loop = None

    def signup(self, roles):
        """
        Displays the signup menu, prompts the user for email, password, and role selection.

        :param roles: A list of role objects available for selection.
        :type roles: list
        :return: A tuple containing the email, password, and selected role if a valid role is selected, otherwise None.
        :rtype: tuple or None
        """
        os.system("cls" if os.name == "nt" else "clear")
        email = click.prompt("Enter email", type=str)
        password = click.prompt("Enter password", hide_input=True, confirmation_prompt=True)

        click.echo("Select a role:")
        for i, role in enumerate(roles, start=1):
            click.echo(f"{i}. {role.name}")

        role_index = click.prompt("Enter role number", type=int) - 1

        if 0 <= role_index < len(roles):
            selected_role = roles[role_index]
            click.echo(f"Selected role: {selected_role.name}")
            return email, password, selected_role
        click.echo("Invalid role selected.")
        return None

    def signup_admin(self):
        """
        Displays the admin signup menu, prompts the user for email and password.

        :return: A tuple containing the email and password.
        :rtype: tuple
        """
        os.system("cls" if os.name == "nt" else "clear")
        email = click.prompt("Enter email", type=str)
        password = click.prompt("Enter password", hide_input=True, confirmation_prompt=True)
        return email, password

    def create_login_page(self, title):
        """
        Creates a login page with a given title.
        :param title: The title of the login page.
        :type title: str
        :return: A dictionary containing the email input, password input, submit button, and the layout of the login page.
        :rtype: dict
        """
        os.system("cls" if os.name == "nt" else "clear")

        title_widget = urwid.LineBox(urwid.Padding(urwid.Text(title, align="left"), left=2, right=4))
        email = urwid.Edit("Email: ")
        password = urwid.Edit("Password: ", mask="*")
        submit_button = urwid.Button("Submit")

        body = [
            urwid.Text(self.ascii_art, align="center"),
            title_widget,
            urwid.Divider(),
            email,
            password,
            urwid.AttrMap(submit_button, None, focus_map="reversed"),
        ]

        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        framed_menu = urwid.Frame(urwid.Padding(list_box, left=2, right=2))

        layout_dict = {"email": email, "password": password, "button": submit_button, "layout": framed_menu}
        return layout_dict

    def create_signup_page(self, title):
        """
        Creates a signup page with email and password input fields and a submit button.
        :param title: The title to be displayed on the signup page.
        :type title: str
        :return: A framed menu containing the signup page UI elements.
        :rtype: urwid.Frame
        """
        os.system("cls" if os.name == "nt" else "clear")

        title_widget = urwid.LineBox(urwid.Padding(urwid.Text(title, align="left"), left=2, right=4))
        email_edit = urwid.Edit("Email: ")
        password_edit = urwid.Edit("Password: ", mask="*")
        submit_button = urwid.Button("Submit")
        urwid.connect_signal(submit_button, "click")

        body = [
            urwid.Text(self.ascii_art, align="center"),
            title_widget,
            urwid.Divider(),
            email_edit,
            password_edit,
            urwid.AttrMap(submit_button, None, focus_map="reversed"),
        ]

        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        framed_menu = urwid.Frame(urwid.Padding(list_box, left=2, right=2))

        return framed_menu

    def login_page_layout(self, title):
        """
        Generates the layout for the login page.
        :param title: The title of the login page.
        :type title: str
        :return: A dictionary containing the layout of the login page.
        :rtype: dict
        """
        layout_dict = self.create_login_page(title)
        return layout_dict
