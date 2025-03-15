# pylint: disable=W0246
"""This file defines the ContractController class for handling user-related operations."""

import sentry_sdk
import urwid
from sentry_sdk.integrations.serverless import serverless_function

from src.controllers.base_controller import BaseController
from src.models.contract import Contract
from src.repositories.contract_repository import ContractRepository
from src.services.base_service import BaseService
from src.services.contract_service import ContractService
from src.views.paginated_view import PaginatedView


class ContractController(BaseController):
    """
    This controller is responsible for managing contract-related actions such as retrieving and displaying all users.
    It interacts with the database session, views, and contract services to perform these operations.
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

    def paginated_contracts_displayed(self, title: str, filter_type: str, client_email_address=None):
        """
        Retrieve and display all users.
        This method retrieves all contract objects from the database, converts them to a dictionary format,
        and displays them in a paginated view. It also sets up the necessary signals for contract interaction.
        """
        contract_objects = self.define_data_to_display(filter_type, client_email_address)
        contract_list_dict = ContractService().list_to_dict(contract_objects)
        paginated_view = PaginatedView(contract_list_dict, title)
        paginated_view.loop = self.base_view.loop
        contracts_label = self.get_button_data_for_items(contract_objects)
        buttons_label = self.define_page_buttons_nedded(contracts_label, filter_type)
        layout, buttons = paginated_view.display_page(0, buttons_label)
        self.define_page_buttons_signal_needded(paginated_view, buttons, contract_objects, filter_type, client_email_address)

        self.history.append(layout)
        self.base_view.update_screen(layout)

    @serverless_function
    def define_data_to_display(self, filter_type, client_email_address):
        """
        Retrieves contract objects based on the given filter.

        :param filter: Filter to apply ('all', 'client', 'current_user', or None).
        :type filter: str
        :param client_email_address: Client email address for filtering, defaults to None.
        :type client_email_address: str, optional
        :return: A list of matching contract objects or None.
        :rtype: list or None
        """
        if filter_type == "all":
            contract_objects = BaseService(self.current_user, ContractRepository()).get_all(self.session)
        elif filter_type == "client":

            sentry_sdk.capture_message(f"client_email_address: {client_email_address}")
            contract_objects = ContractService().filter_by_email_adress(client_email_address, self.session)
            sentry_sdk.capture_message(f"contract_objects: {contract_objects}")
        elif filter_type == "current_user":
            contract_objects = ContractService().filter_by_sales_email_adress(self.current_user.email_address, self.session)
        elif filter_type == "not signed":
            contract_objects = ContractService().filtered_by_contract_signed_or_pending(self.session, "Pending")
        elif filter_type == "not payed":
            contract_objects = ContractService().filtered_by_contract_payed_or_not(self.session, False)
        else:
            contract_objects = None
        return contract_objects

    def define_page_buttons_signal_needded(self, paginated_view, buttons, contract_objects, filter_type, client_email_address):
        """
        Define the signals needed for page buttons based on the filter criteria.

        :param paginated_view: The view that displays paginated contract objects.
        :type paginated_view: PaginatedView
        :param buttons: The buttons to be updated with signals.
        :type buttons: list
        :param contract_objects: The contract objects to be displayed.
        :type contract_objects: list
        :param filter: The filter criteria to determine which contracts to display.
        :type filter: str
        :param client_email_address: The email address of the client (used when filter is "client").
        :type client_email_address: str
        """
        if filter_type == "all":
            self.create_all_contracts_paginated_buttons_signal(paginated_view, buttons, contract_objects)
        elif filter_type == "client":
            self.create_client_contracts_paginated_buttons_signal(paginated_view, buttons, contract_objects, client_email_address)
        elif filter_type in {"current_user", "signed", "not signed", "payed", "not payed"}:
            self.create_filtered_contracts_paginated_buttons_signal(paginated_view, buttons, contract_objects)

    def create_client_contracts_paginated_buttons_signal(self, paginated_view, buttons, contract_objects, client_email_address):
        """
        Create paginated buttons signal for client contracts.

        This method connects signals to the buttons in the paginated view for client contracts.
        It sets up the object details data and connects the click events to the appropriate handlers.

        :param paginated_view: The paginated view object that handles pagination.
        :type paginated_view: PaginatedView
        :param buttons: A dictionary containing button items and other buttons.
        :type buttons: dict
        :param contract_objects: A list of contract objects associated with the client.
        :type contract_objects: list
        :param client_email_address: The email address of the client.
        :type client_email_address: str
        """
        for button in buttons["buttons_items"]:
            selected_contract = self.select_item_in_lst(contract_objects, button.get_label())
            object_details_data = {
                "title": f"> Home > Clients > {client_email_address} > Contracts > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": selected_contract,
                "service": self,
                "buttons_label": [],
            }
            for permission in self.current_user.role.permissions:
                if permission.action == "event_update" and (
                    self.current_user.role.name != "support" or selected_contract.support_user_id == self.current_user.email_address
                ):
                    object_details_data["buttons_label"].append("Modify")
                if permission.action == "event_delete":
                    object_details_data["buttons_label"].append("Delete")

            urwid.connect_signal(
                button,
                "click",
                lambda button=button, selected_contract=selected_contract, object_details_data=object_details_data: self.object_details_layout(
                    f"> Home > Client > {client_email_address} > Contracts > {button.get_label()}",
                    selected_contract,
                    self,
                    object_details_data,
                ),
            )

        button_actions = [
            ("Previous", paginated_view.previous_page()),
            ("Next", paginated_view.next_page()),
            ("Create", lambda button: self.create_client_contracts(client_email_address)),
        ]

        self.connect_button_signals(buttons, button_actions)

    def create_filtered_contracts_paginated_buttons_signal(self, paginated_view, buttons, contract_objects):
        """
        Create signals for paginated buttons and connect them to their respective actions.

        This method sets up the signals for the buttons in a paginated view. It connects each button to a
        click event that triggers the display of object details. Additionally, it connects the pagination
        buttons to their respective actions for navigating between pages.

        :param paginated_view: The paginated view object that handles the pagination logic.
        :type paginated_view: PaginatedView
        :param buttons: A dictionary containing the button items and other pagination buttons.
        :type buttons: dict
        :param contract_objects: A list of contract objects to be displayed.
        :type contract_objects: list
        """
        for button in buttons["buttons_items"]:
            selected_contract = self.select_item_in_lst(contract_objects, button.get_label())
            object_details_data = {
                "title": f"> Home > Contracts > My contracts > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": selected_contract,
                "service": self,
                "buttons_label": [],
            }
            for permission in self.current_user.role.permissions:
                if permission.action == "event_update" and (
                    self.current_user.role.name != "support" or selected_contract.support_user_id == self.current_user.email_address
                ):
                    object_details_data["buttons_label"].append("Modify")
                if permission.action == "event_delete":
                    object_details_data["buttons_label"].append("Delete")

            urwid.connect_signal(
                button,
                "click",
                lambda button=button, selected_contract=selected_contract, object_details_data=object_details_data: self.object_details_layout(
                    f"> Home > Client > {button.get_label()}", selected_contract, self, object_details_data
                ),
            )

        button_actions = [
            ("Previous", paginated_view.previous_page()),
            ("Next", paginated_view.next_page()),
        ]

        self.connect_button_signals(buttons, button_actions)

    def create_all_contracts_paginated_buttons_signal(self, paginated_view, buttons, contract_objects):
        """
        Connects signals to buttons for paginated contract views.

        This method sets up the signals for the buttons in a paginated view of contracts.
        It connects each button to display the details of the corresponding contract object
        and also connects navigation buttons to handle pagination.

        :param paginated_view: The view object that handles pagination.
        :type paginated_view: PaginatedView
        :param buttons: A dictionary containing button items and other navigation buttons.
        :type buttons: dict
        :param contract_objects: A list of contract objects to be displayed.
        :type contract_objects: list
        """
        for button in buttons["buttons_items"]:
            selected_contract = self.select_item_in_lst(contract_objects, button.get_label())
            object_details_data = {
                "title": f"> Home > Contracts > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": selected_contract,
                "service": self,
                "buttons_label": [],
            }
            for permission in self.current_user.role.permissions:
                if permission.action == "event_update" and (
                    self.current_user.role.name != "support" or selected_contract.support_user_id == self.current_user.email_address
                ):
                    object_details_data["buttons_label"].append("Modify")
                if permission.action == "event_delete":
                    object_details_data["buttons_label"].append("Delete")

            urwid.connect_signal(
                button,
                "click",
                lambda button=button, selected_contract=selected_contract, object_details_data=object_details_data: self.object_details_layout(
                    f"> Home > Contracts > {button.get_label()}", selected_contract, self, object_details_data
                ),
            )

        button_actions = [
            ("Previous", paginated_view.previous_page()),
            ("Next", paginated_view.next_page()),
            ("My contracts", lambda: self.paginated_contracts_displayed("> Home > Contracts > My contracts", "current_user")),
            ("Not signed contracts", lambda: self.paginated_contracts_displayed("> Home > Contracts > Not signed contracts", "not signed")),
            ("Not payed contracts", lambda: self.paginated_contracts_displayed("> Home > Contracts > Not payed contracts", "not payed")),
        ]

        self.connect_button_signals(buttons, button_actions)

    def define_page_buttons_nedded(self, contracts_label, filter_type):
        """
        Define the page buttons needed based on the filter type.

        :param contracts_label: The label for the contracts.
        :type contracts_label: str
        :param filter: The filter type to determine which buttons to display.
                    Possible values are "all", "client", and "current_user".
        :type filter: str
        :return: A dictionary with the users label and the list of buttons, or None if the filter is not recognized.
        :rtype: dict or None
        """
        buttons = ["Previous", "Next"]
        _dict = {"users_label": contracts_label, "buttons": buttons}

        if filter_type == "all":
            if self.current_user.role.name in ["admin", "sales", "management"]:
                buttons.append("My contracts")
            if self.current_user.role.name in ["admin", "sales"]:
                buttons.extend(["Not signed contracts", "Not payed contracts"])
            return _dict

        if filter_type == "client":
            for permission in self.current_user.role.permissions:
                if permission.action == "contract_create":
                    buttons.append("Create")
            return _dict

        if filter_type in {"current_user", "not signed", "not payed"}:
            return _dict

        return None

    def create_client_contracts(self, client_email_address):
        """
        Create the client contracts view.

        This method sets up the form layout for creating client contracts, including
        input fields for price, outstanding balance, and status. It also connects the
        create contract button to the appropriate event handler.

        :param client_email_address: The email address of the client for whom the contract is being created.
        :type client_email_address: str
        """
        button_labels = ["Create Contract"]
        edit_labels = [
            "Price: ",
            "Outstanding balance: ",
            "Status (Signed, Pending): ",
        ]

        # Create the form layout
        layout_dict = self.base_view.create_form_layout(f"> Home > Contracts > {client_email_address} > Create", button_labels, edit_labels)

        # Connect the signal for the create user button
        urwid.connect_signal(
            layout_dict["buttons"][0],
            "click",
            lambda button: self.handle_client_creation_button_event(layout_dict, client_email_address),
        )
        self.base_view.update_screen(layout_dict["layout"])

    def handle_client_creation_button_event(self, layout_dict, client_email_address):
        """
        Handles the event when the client creation button is clicked.

        This method is responsible for creating a new contract using the provided
        client email address and layout dictionary. It logs the event, constructs
        the contract data, and attempts to create the contract using the BaseService.
        If the contract creation is successful, it updates the screen and logs the
        success. If it fails, it logs the failure.

        :param layout_dict: A dictionary containing layout information, including
                            editable fields for contract data.
        :type layout_dict: dict
        :param client_email_address: The email address of the client for whom the
                                     contract is being created.
        :type client_email_address: str
        """

        contract_data = {
            "id": ContractService().generate_uid(self.session),
            "client_id": client_email_address,
            "price": layout_dict["edits"][0].get_edit_text(),
            "Outstanding_balance": layout_dict["edits"][1].get_edit_text(),
            "sales_contact_id": self.current_user.email_address,
            "status_id": layout_dict["edits"][2].get_edit_text(),
        }
        if BaseService(Contract).create(contract_data, self.session):
            self.history.pop()

            self.base_view.update_screen(self.history[0])
        else:
            self.base_view.display_message("Contract creation failed. Please try again.")

    def create_details_view_buttons_signal(self, buttons, contract_object):
        """
        Create signals for the details view buttons.

        This method connects signals to the provided buttons for modifying and deleting a contract object.
        It logs the current user and the client template dictionary after removing specific attributes.

        :param buttons: List of buttons to which signals will be connected.
        :type buttons: list
        :param contract_object: The contract object for which the details view buttons are created.
        :type contract_object: Contract
        """

        client_template_dict = contract_object.to_dict()
        new_client_template_dict = BaseService(Contract).remove_attributes_from_object(
            client_template_dict, ["ID", "Client Name", "Client Email address", "Client Phone", "Client Compagny", "Creation date"]
        )

        button_actions = [
            (
                "Modify",
                lambda: self.pre_filled_form_page(
                    f"> Home > Client > {contract_object.id} > Modify",
                    new_client_template_dict,
                    contract_object,
                    ContractService(),
                ),
            ),
            ("Delete", lambda: self.show_delete_confirmation(contract_object, BaseService(Contract))),
        ]

        self.connect_button_signals(buttons, button_actions)
