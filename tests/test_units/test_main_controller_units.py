import unittest
from unittest.mock import patch, MagicMock, ANY

import urwid

from src.controllers.main_controller import MainController
from src.controllers.auth_controller import AuthController

class TestMainController(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.base_view = MagicMock()
        self.base_view.loop = MagicMock()
        self.current_user = MagicMock()
        self.history = []
        self.ctrl = MainController(self.session, self.base_view, self.current_user, self.history)

    def test_run_application_calls_connect(self):
        with patch.object(self.ctrl, 'connect') as mock_connect:
            self.ctrl.run_application()
            mock_connect.assert_called_once()

    @patch('src.controllers.main_controller.urwid.connect_signal')
    @patch('src.controllers.main_controller.AuthController')
    def test_connect_sets_up_menu_and_signals(self, mock_auth_cls, mock_connect_signal):
        # Arrange: AuthController returns a dummy instance
        auth_inst = MagicMock()
        mock_auth_cls.return_value = auth_inst
        # Arrange: create_menu_layout returns two buttons and a layout
        btn0, btn1 = MagicMock(base_widget='w0'), MagicMock(base_widget='w1')
        layout = MagicMock()
        self.base_view.create_menu_layout.return_value = ([btn0, btn1], layout)

        # Act
        self.ctrl.connect()

        # Assert AuthController was instantiated correctly
        mock_auth_cls.assert_called_once_with(
            self.session, self.base_view, self.current_user, self.history
        )
        # Assert menu layout creation
        self.base_view.create_menu_layout.assert_called_once_with(
            ">Welcome", ["Connect", "Quit"]
        )
        # Assert signals connected for both buttons
        calls = mock_connect_signal.call_args_list
        self.assertEqual(calls[0][0][0], btn0.base_widget)
        self.assertEqual(calls[0][0][1], "click")
        self.assertTrue(callable(calls[0][0][2]))
        self.assertEqual(calls[1][0][0], btn1.base_widget)
        self.assertEqual(calls[1][0][1], "click")
        # Assert loop initialization and run
        self.base_view.init_main_loop.assert_called_once_with(layout, ANY)
        self.base_view.loop.run.assert_called_once()
