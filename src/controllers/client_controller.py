# pylint: disable=W0246
"""This file defines the ClientController class for handling client-related operations."""

import sentry_sdk
import urwid

from src.controllers.base_controller import BaseController
from src.controllers.contract_controller import ContractController
from src.controllers.event_controller import EventController
from src.models.client import Client
from src.repositories.client_repository import ClientRepository
from src.services.base_service import BaseService
from src.services.client_service import ClientService
from src.services.user_service import UserService
from src.views.paginated_view import PaginatedView


class ClientController(BaseController):
    """
    This controller is responsible for managing client-related actions such as retrieving and displaying all users.
    It interacts with the database session, views, and client services to perform these operations.
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

    def all_clients(self):
        """
        Fetch and display all clients in a paginated view.
        converts them to dictionary format using the ClientService, and displays them
        using a paginated view. It sets up signal connections for search functionality
        and button clicks, and updates the view history and screen layout.
        """
        client_objects = BaseService(self.current_user, ClientRepository()).get_all(self.session)
        client_list_dict = ClientService().list_to_dict(client_objects)
        paginated_view = PaginatedView(client_list_dict, "> Home > Clients")
        paginated_view.loop = self.base_view.loop
        clients_label = BaseController.get_button_data_for_items(self, client_objects)
        buttons_label = {
            "users_label": clients_label,
            "buttons": ["Previous", "Next"],
        }
        if self.current_user.role.name in ["admin", "sales"]:
            buttons_label["buttons"].append("Create")
        layout, buttons = paginated_view.display_page(0, buttons_label)

        self.create_paginated_buttons_signal(paginated_view, buttons, client_objects)

        self.history.append(layout)
        self.base_view.update_screen(layout)

    def create_paginated_buttons_signal(self, paginated_view, buttons, client_objects):
        """
        Connect signals for the paginated view and handle button clicks.

        :param paginated_view: The paginated view instance
        :type paginated_view: PaginatedView
        :param buttons: Dictionary containing pagination and item buttons
        :type buttons: dict
        :param client_objects: List of client objects for detail view
        :type client_objects: list
        """
        for button in buttons["buttons_items"]:
            selected_client = self.select_item_in_lst(client_objects, button.get_label())
            object_details_data = {
                "title": f"> Home > Users > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": selected_client,
                "service": self,
                "buttons_label": [],
            }
            if selected_client.sales_contact_id == self.current_user.email_address and self.current_user.role.name != "admin":
                object_details_data["buttons_label"] = ["Modify", "Contracts", "Events"]
            elif (
                self.current_user.role.name == "management"
                or self.current_user.role.name == "sales"
                and selected_client.sales_contact_id != self.current_user.email_address
                or self.current_user.role.name == "support"
            ):
                object_details_data["buttons_label"] = ["Contracts", "Events"]
            elif self.current_user.role.name == "admin":
                object_details_data["buttons_label"] = [
                    "Modify",
                    "Delete",
                    "Contracts",
                    "Events",
                ]

            urwid.connect_signal(
                button,
                "click",
                lambda button=button, selected_client=selected_client, object_details_data=object_details_data: self.object_details_layout(
                    f"> Home > Client > {button.get_label()}", selected_client, self, object_details_data
                ),
            )

        button_actions = [
            ("Previous", paginated_view.previous_page()),
            ("Next", paginated_view.next_page()),
            ("Create", self.client_creation()),
        ]

        self.connect_button_signals(buttons, button_actions)

    def client_creation(self):
        """
        Creates a client creation form view and binds signals.
        """
        # Define the labels for the form
        button_labels = ["Create Client"]
        edit_labels = ["Name: ", "Email: ", "Phone: ", "Compagny: "]

        # Create the form layout
        layout_dict = self.base_view.create_form_layout("> Home > Clients > Create", button_labels, edit_labels)

        # Connect the signal for the create user button
        urwid.connect_signal(
            layout_dict["buttons"][0],
            "click",
            lambda button: self.handle_client_creation_button_event(layout_dict),
        )
        self.base_view.update_screen(layout_dict["layout"])

    def handle_client_creation_button_event(self, layout_dict):
        """
        Handle the user creation button event by processing the user's email, password, and role,
        then optionally invoking a redirection function.

        :param layout_dict: A dictionary containing UI elements for fetching user input fields
            (e.g., email, password, role_name).
        :type layout_dict: dict
        :param redirect_func: A callable function to redirect after successful user creation, or None.
        :type redirect_func: callable, optional
        """

        client_data = {
            "name": layout_dict["edits"][0].get_edit_text(),
            "email_address": layout_dict["edits"][1].get_edit_text(),
            "phone": layout_dict["edits"][2].get_edit_text(),
            "compagny": layout_dict["edits"][3].get_edit_text(),
            "sales_contact_id": self.current_user.email_address,
        }
        user_exist = UserService().get_by_email(self.current_user.email_address, self.session)
        if user_exist:
            BaseService(Client).create(client_data, self.session)
            self.history.pop()

            self.base_view.update_screen(self.history[0])
        else:
            self.base_view.display_message("Sales contact does not exist. Please try again.")

    def create_details_view_buttons_signal(self, buttons, client_object):
        """
        Create signals for modify and delete buttons in the details view.

        :param buttons: Dictionary with references to 'modify_button' and 'delete_button'
        :type buttons: dict
        :param client_object: The client instance for which details are displayed
        :type client_object: Client
        """
        client_template_dict = client_object.to_dict()
        new_client_template_dict = BaseService(Client).remove_attributes_from_object(client_template_dict, ["Creation date", "Last update"])
        sentry_sdk.capture_message(f"client_email: {client_object.email_address}")
        button_actions = [
            (
                "Modify",
                lambda: self.pre_filled_form_page(
                    f"> Home > Clients > {client_object.email_address} > Modify",
                    new_client_template_dict,
                    client_object,
                    ClientService(),
                ),
            ),
            ("Delete", lambda: self.show_delete_confirmation(client_object, BaseService(Client))),
            (
                "Contracts",
                lambda: ContractController(self.session, self.base_view, self.current_user, self.history).paginated_contracts_displayed(
                    f"> Home > Client > {client_object.email_address} > Contracts", "client", client_object.email_address
                ),
            ),
            (
                "Events",
                lambda: EventController(self.session, self.base_view, self.current_user, self.history).paginated_events_displayed(
                    f"> Home > Client > {client_object.email_address} > Events", "client", client_object.email_address
                ),
            ),
        ]

        self.connect_button_signals(buttons, button_actions)
