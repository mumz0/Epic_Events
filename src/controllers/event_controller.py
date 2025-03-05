# pylint: disable=W0246
"""This file defines the ContractController class for handling user-related operations."""

import urwid

from logger_file import logger
from src.controllers.base_controller import BaseController
from src.models.event import Event
from src.repositories.event_reposiroty import EventRepository
from src.services.base_service import BaseService
from src.services.contract_service import ContractService
from src.services.event_service import EventService
from src.views.paginated_view import PaginatedView


class EventController(BaseController):
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

    def paginated_events_displayed(self, title: str, filter_type: str, email_address=None):
        """
        Retrieve and display all users.
        This method retrieves all contract objects from the database, converts them to a dictionary format,
        and displays them in a paginated view. It also sets up the necessary signals for contract interaction.
        """
        event_objects = self.define_data_to_display(filter_type, email_address)
        event_list_dict = EventService().list_to_dict(event_objects)
        logger.info("All events: %s", event_list_dict)
        paginated_view = PaginatedView(event_list_dict, title)
        paginated_view.loop = self.base_view.loop
        events_label = self.get_button_data_for_items(event_objects)
        logger.info("users_label: %s", events_label)
        buttons_label = self.define_page_buttons_nedded(events_label, filter_type)
        layout, buttons = paginated_view.display_page(0, buttons_label)
        self.define_page_buttons_signal_needded(paginated_view, buttons, event_objects, filter_type, email_address)

        logger.info("items: %s", paginated_view.items)
        self.history.append(layout)
        self.base_view.update_screen(layout)
        logger.info("History:  Menu (%s)", len(self.history))

    def define_data_to_display(self, filter_type, email_address=None):
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
            event_objects = BaseService(self.current_user, EventRepository()).get_all(self.session)
        elif filter_type == "client":
            event_objects = EventService().filter_by_email_adress(email_address, self.session)
        elif filter_type == "current_user":
            event_objects = EventService().filter_by_sales_email_adress(self.current_user.email_address, self.session)
        else:
            event_objects = None
        return event_objects

    def define_page_buttons_signal_needded(self, paginated_view, buttons, event_objects, filter_type, client_email_address):
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
            self.create_all_contracts_paginated_buttons_signal(paginated_view, buttons, event_objects)
        if filter_type == "client":
            self.create_client_contracts_paginated_buttons_signal(paginated_view, buttons, event_objects, client_email_address)
        if filter_type == "current_user":
            self.create_current_user_paginated_buttons_signal(paginated_view, buttons, event_objects)

    def create_client_contracts_paginated_buttons_signal(self, paginated_view, buttons, event_objects, client_email_address):
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
            object_details_data = {
                "title": f"> Home > Clients > {client_email_address} > Events > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": event_objects,
                "service": self,
                "buttons_label": ["Modify", "Delete"],
            }
            urwid.connect_signal(
                button,
                "click",
                lambda button=button, object_details_data=object_details_data: self.object_details_layout(
                    f"> Home > Client > {client_email_address} > Events > {button.get_label()}",
                    button.get_label(),
                    event_objects,
                    self,
                    object_details_data,
                ),
            )
        urwid.connect_signal(buttons["other_buttons"][0], "click", lambda button: paginated_view.previous_page())
        urwid.connect_signal(buttons["other_buttons"][1], "click", lambda button: paginated_view.next_page())
        urwid.connect_signal(buttons["other_buttons"][2], "click", lambda button: self.create_client_contracts(client_email_address))

    def create_current_user_paginated_buttons_signal(self, paginated_view, buttons, event_objects):
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
            object_details_data = {
                "title": f"> Home > Events > My events > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": event_objects,
                "service": self,
                "buttons_label": ["Modify", "Delete", "Client"],
            }
            urwid.connect_signal(
                button,
                "click",
                lambda button=button, object_details_data=object_details_data: self.object_details_layout(
                    f"> Home > Client > {button.get_label()}", button.get_label(), event_objects, self, object_details_data
                ),
            )
        urwid.connect_signal(buttons["other_buttons"][0], "click", lambda button: paginated_view.previous_page())
        urwid.connect_signal(buttons["other_buttons"][1], "click", lambda button: paginated_view.next_page())

    def create_all_contracts_paginated_buttons_signal(self, paginated_view, buttons, event_objects):
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
            object_details_data = {
                "title": f"Home > Events > {button.get_label()}",
                "item_identifier": button.get_label(),
                "obj_lst": event_objects,
                "service": self,
                "buttons_label": ["Modify", "Delete"],
            }
            urwid.connect_signal(
                button,
                "click",
                lambda button=button, object_details_data=object_details_data: self.object_details_layout(
                    f"> Home > Client > {button.get_label()}", button.get_label(), event_objects, self, object_details_data
                ),
            )
        urwid.connect_signal(buttons["other_buttons"][0], "click", lambda button: paginated_view.previous_page())
        urwid.connect_signal(buttons["other_buttons"][1], "click", lambda button: paginated_view.next_page())
        urwid.connect_signal(
            buttons["other_buttons"][2], "click", lambda button: self.paginated_events_displayed("> Home > Events > My events", "current_user")
        )

    def define_page_buttons_nedded(self, event_label, filter_type):
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
        if filter_type == "all":
            return {"users_label": event_label, "buttons": ["Previous", "Next", "My events"]}

        if filter_type == "client":
            return {"users_label": event_label, "buttons": ["Previous", "Next", "Create"]}

        if filter_type == "current_user":
            return {"users_label": event_label, "buttons": ["Previous", "Next"]}

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
        button_labels = ["Create event"]
        edit_labels = [
            "Name",
            "Start_date (YYYY/MM/DD)",
            "End date (YYYY/MM/DD)",
            "Location",
            "Attendees",
            "Notes",
            "Contract ID",
            "Support contact",
        ]

        # Create the form layout
        layout_dict = self.base_view.create_form_layout("> Home > Events > Create", button_labels, edit_labels)

        # Connect the signal for the create user button
        urwid.connect_signal(
            layout_dict["buttons"][0],
            "click",
            lambda button: self.handle_client_creation_button_event(layout_dict, client_email_address),
        )
        self.base_view.update_screen(layout_dict["layout"])
        logger.info("Create event view")
        logger.info(self.base_view.loop)
        logger.info("History:  before event creation (%s)", len(self.history))

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
        logger.info("Submit button clicked")
        datetime_start_date = EventService().string_date_to_datetime(layout_dict["edits"][1].get_edit_text())
        datetime_end_date = EventService().string_date_to_datetime(layout_dict["edits"][2].get_edit_text())
        event_data = {
            "id": EventService().generate_uid(self.session),
            "name": layout_dict["edits"][0].get_edit_text(),
            "start_date": datetime_start_date,
            "end_date": datetime_end_date,
            "location": layout_dict["edits"][3].get_edit_text(),
            "attendees": layout_dict["edits"][4].get_edit_text(),
            "notes": layout_dict["edits"][5].get_edit_text(),
            "contract_id": layout_dict["edits"][6].get_edit_text(),
            "client_id": client_email_address,
            "support_user_id": layout_dict["edits"][7].get_edit_text(),
        }

        if BaseService(Event).create(event_data, self.session):
            logger.info("Event successfully created")
            self.history.pop()

            self.base_view.update_screen(self.history[0])
            logger.info("History:  after event creation (%s)", len(self.history))
        else:
            logger.info("Event creation failed")

    def create_details_view_buttons_signal(self, buttons, event_object):
        """
        Create signals for the details view buttons.

        This method connects signals to the provided buttons for modifying and deleting a contract object.
        It logs the current user and the client template dictionary after removing specific attributes.

        :param buttons: List of buttons to which signals will be connected.
        :type buttons: list
        :param contract_object: The contract object for which the details view buttons are created.
        :type contract_object: Contract
        """

        logger.info("Creating details view buttons signal")
        logger.info("Current user: %s", self.current_user)
        event_template_dict = event_object.to_dict()
        new_event_template_dict = BaseService(Event).remove_attributes_from_object(event_template_dict, "ID")
        logger.info("Event template dict: %s", new_event_template_dict)
        urwid.connect_signal(
            buttons[0],
            "click",
            lambda button: self.pre_filled_form_page(
                f"> Home > Client > {event_object.id} > Modify",
                new_event_template_dict,
                event_object,
                ContractService(),
            ),
        )
        urwid.connect_signal(
            buttons[1],
            "click",
            lambda button: self.show_delete_confirmation(event_object, BaseService(Event)),
        )
