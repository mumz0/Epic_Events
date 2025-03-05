# pylint: disable=W0612
"""
PaginatedView is a class that provides a paginated view of a list of items using the urwid library.
"""

import urwid

from src.views.base_view import BaseView


class PaginatedView(BaseView):
    """
    A class to represent a paginated view for displaying items.
    """

    def __init__(self, items, title, items_per_page=10):
        """
        Initialize the PaginatedView.

        :param items: A dictionary of items to be displayed in the paginated view.
        :type items: dict
        :param title: The title of the paginated view.
        :type title: str
        :param items_per_page: The number of items to display per page, defaults to 10.
        :type items_per_page: int, optional
        """
        super().__init__()
        self.items = list(items.values())
        self.original_items = self.items.copy()
        self.items_per_page = items_per_page
        self.page = 0
        self.total_pages = (len(self.items) + items_per_page - 1) // items_per_page
        self.title = title
        self.buttons_label_dict = None

    def get_page(self, page):
        """
        Retrieves a subset of items for the specified page.

        :param page: The page number (zero-based) to retrieve.
        :type page: int
        :return: A list of items corresponding to the specified page.
        :rtype: list
        """
        start = page * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def display_page(self, page, buttons_label_dict=None):
        """
        Displays a paginated view within a user interface.
        :param page: The current page index to display.
        :type page: int
        :returns: A tuple where the first element is the framed layout to render, and the second is a list of button widgets.
        :rtype: Tuple[urwid.Frame, List[urwid.Widget]]
        """
        if buttons_label_dict:
            self.buttons_label_dict = buttons_label_dict  # Store buttons_label_dict

        items = self.get_page(page)
        title_widget = urwid.LineBox(urwid.Padding(urwid.Text(self.title, align="left"), left=2, right=4))
        body = [urwid.Text(self.ascii_art, align="center"), title_widget, urwid.Divider()]

        body.append(urwid.Text(f"Page {page + 1}/{self.total_pages}"))
        buttons_items = [self.create_button(buttons_label) for buttons_label in self.buttons_label_dict["users_label"]]
        body.extend(buttons_items)

        buttons = []
        for button_label in self.buttons_label_dict["buttons"]:
            button = self.create_button(button_label)
            buttons.append(button)
            body.append(button)

        # TODO: Add permission condition
        buttons = {"buttons_items": buttons_items, "other_buttons": buttons}
        list_box = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        framed_layout = urwid.Frame(urwid.Padding(list_box, left=2, right=2))
        return framed_layout, buttons

    def previous_page(self):
        """
        Move to the previous page if possible and update the view.

        :param button: The button used to trigger moving to the previous page.
        :type button: object
        """
        if self.page > 0:
            self.page -= 1
        self.update_view()

    def next_page(self):
        """
        Move to the next page if it exists, then update the view.

        :param button: The UI button that triggers the page navigation.
        :type button: object
        """
        if self.page < self.total_pages - 1:
            self.page += 1
        self.update_view()

    def update_view(self):
        """
        Updates the displayed view.

        This method retrieves the current page's widget and associated buttons from
        :func:`display_page`, then refreshes the screen to reflect any changes.

        """
        self.loop.widget, buttons = self.display_page(self.page, self.buttons_label_dict)
        self.loop.draw_screen()
