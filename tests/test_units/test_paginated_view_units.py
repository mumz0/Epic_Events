import unittest
from unittest.mock import MagicMock, patch
import urwid

from src.views.paginated_view import PaginatedView

class TestPaginatedView(unittest.TestCase):
    def setUp(self):
        # create view with 3 items, 2 per page
        items = {"a": 1, "b": 2, "c": 3}
        self.view = PaginatedView(items, title="MyTitle", items_per_page=2)
        # stub ascii art and loop
        self.view.ascii_art = "ART"
        self.view.loop = MagicMock()

    def test_get_page_returns_correct_slice(self):
        # page 0 → first two items
        self.assertEqual(self.view.get_page(0), [1, 2])
        # page 1 → last item
        self.assertEqual(self.view.get_page(1), [3])
        # out-of-range page → empty list
        self.assertEqual(self.view.get_page(2), [])

    def test_display_page_structure_and_buttons(self):
        labels = {"users_label": ["U1", "U2"], "buttons": ["Next", "Prev"]}
        framed, btns = self.view.display_page(0, buttons_label_dict=labels)

        # layout is a Frame
        self.assertIsInstance(framed, urwid.Frame)
        # returned buttons dict has expected keys
        self.assertIn("buttons_items", btns)
        self.assertIn("other_buttons", btns)
        self.assertEqual(len(btns["buttons_items"]), 2)
        self.assertEqual(len(btns["other_buttons"]), 2)

        list_widget = framed.body
        list_box = getattr(list_widget, "original_widget", list_widget)
        walker = list_box.body
        texts = [w.text for w in walker if isinstance(w, urwid.Text)]
        self.assertIn("Page 1/2", texts)

    @patch.object(PaginatedView, "display_page")
    def test_update_view_sets_widget_and_draws(self, mock_display):
        # simulate display_page returning known layout
        mock_display.return_value = ("LAYOUT", ["btn"])
        self.view.page = 1
        self.view.buttons_label_dict = {"dummy": []}

        self.view.update_view()

        mock_display.assert_called_once_with(1, self.view.buttons_label_dict)
        self.assertEqual(self.view.loop.widget, "LAYOUT")
        self.view.loop.draw_screen.assert_called_once()

    @patch.object(PaginatedView, "update_view")
    def test_next_and_previous_page_navigation(self, mock_update_view):
        # next_page from 0 → 1
        self.view.page = 0
        self.view.next_page()
        self.assertEqual(self.view.page, 1)
        mock_update_view.assert_called()

        mock_update_view.reset_mock()
        # next_page at last page stays
        self.view.page = self.view.total_pages - 1
        self.view.next_page()
        self.assertEqual(self.view.page, self.view.total_pages - 1)
        mock_update_view.assert_called()

        mock_update_view.reset_mock()
        # previous_page from >0 → decrement
        self.view.page = 1
        self.view.previous_page()
        self.assertEqual(self.view.page, 0)
        mock_update_view.assert_called()

        mock_update_view.reset_mock()
        # previous_page at 0 stays
        self.view.page = 0
        self.view.previous_page()
        self.assertEqual(self.view.page, 0)
        mock_update_view.assert_called()

if __name__ == "__main__":
    unittest.main()