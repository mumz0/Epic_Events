import unittest
from unittest.mock import MagicMock, patch

from src.controllers.auth_controller import AuthController
from src.controllers.base_controller import BaseController
from src.controllers.main_controller import MainController


class TestMainController(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_base_view = MagicMock()
        self.mock_current_user = MagicMock()
        self.mock_history = []
        self.controller = MainController(self.mock_session, self.mock_base_view, self.mock_current_user, self.mock_history)

    @patch("src.controllers.main_controller.AuthController")
    @patch("src.controllers.main_controller.urwid.connect_signal")
    @patch.object(BaseController, "__init__", return_value=None)
    def test_connect_creates_menu_and_signals(self, mock_base_init, mock_connect_signal, mock_auth_ctrl):
        # Return two items so buttons and layout can be unpacked
        self.mock_base_view.create_menu_layout.return_value = ([MagicMock(), MagicMock()], MagicMock())

        self.controller.connect()

        mock_auth_ctrl.assert_called_once_with(self.mock_session, self.mock_base_view, self.mock_current_user, self.mock_history)
        self.mock_base_view.create_menu_layout.assert_called_once_with(">Welcome", ["Connect", "Quit"])
        mock_connect_signal.assert_any_call(self.mock_base_view.create_menu_layout.return_value[0][0].base_widget, "click", unittest.mock.ANY)
        mock_connect_signal.assert_any_call(self.mock_base_view.create_menu_layout.return_value[0][1].base_widget, "click", unittest.mock.ANY)
