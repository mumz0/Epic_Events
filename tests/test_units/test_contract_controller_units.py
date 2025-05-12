import unittest
from unittest.mock import MagicMock, patch

from src.controllers.contract_controller import ContractController
from src.services.contract_service import ContractService
from src.views.paginated_view import PaginatedView


class TestContractController(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_base_view = MagicMock()
        self.mock_current_user = MagicMock()
        self.mock_current_user.role.permissions = []
        self.mock_history = []
        self.controller = ContractController(self.mock_session, self.mock_base_view, self.mock_current_user, self.mock_history)

    @patch.object(ContractService, "list_to_dict", return_value={"C1": {"id": "C1"}})
    @patch("src.controllers.contract_controller.PaginatedView")
    def test_paginated_contracts_displayed_all(self, mock_paginated, mock_list_dict):
        mock_paginated.return_value.display_page.return_value = (MagicMock(), {"buttons_items": []})
        self.controller.paginated_contracts_displayed("> Home > Contracts", "all")

        # Vérifier que la méthode list_to_dict est appelée
        mock_list_dict.assert_called_once()
        # Vérifier que l'écran est mis à jour
        self.assertTrue(self.mock_base_view.update_screen.called)
        # Vérifier que l'historique est mis à jour
        self.assertEqual(len(self.mock_history), 1)

    @patch.object(ContractService, "list_to_dict", return_value={"C2": {"id": "C2"}})
    @patch("src.controllers.contract_controller.PaginatedView")
    def test_paginated_contracts_displayed_client(self, mock_paginated, mock_list_dict):
        mock_paginated.return_value.display_page.return_value = (MagicMock(), {"buttons_items": []})
        self.controller.paginated_contracts_displayed("> Home > Contracts > Client", "client", "client@example.com")

        mock_list_dict.assert_called_once()
        self.assertTrue(self.mock_base_view.update_screen.called)
        self.assertEqual(len(self.mock_history), 1)

    def test_define_data_to_display_not_implemented(self):
        # Exemple minimaliste pour illustrer un test unitaire sur define_data_to_display
        with patch.object(self.controller, "define_data_to_display", return_value=[]):
            result = self.controller.define_data_to_display("all")
            self.assertEqual(result, [])

    @patch("src.controllers.contract_controller.urwid.connect_signal")
    def test_define_page_buttons_signal_needded_calls_correct_signal(self, mock_connect_signal):
        paginated_view = MagicMock(spec=PaginatedView)
        buttons = {"buttons_items": [MagicMock()]}
        contract_objects = [MagicMock(id="C1")]

        self.controller.define_page_buttons_signal_needded(paginated_view, buttons, contract_objects, "all", None)
        self.assertTrue(mock_connect_signal.called)

    @patch("src.controllers.contract_controller.urwid.connect_signal")
    def test_create_client_contracts_paginated_buttons_signal(self, mock_connect_signal):
        paginated_view = MagicMock(spec=PaginatedView)
        buttons = {"buttons_items": [MagicMock()]}
        contract_objects = [MagicMock(id="C1")]

        self.controller.create_client_contracts_paginated_buttons_signal(paginated_view, buttons, contract_objects, "client@example.com")
        self.assertTrue(mock_connect_signal.called)

    @patch("src.controllers.contract_controller.urwid.connect_signal")
    def test_create_all_contracts_paginated_buttons_signal(self, mock_connect_signal):
        paginated_view = MagicMock(spec=PaginatedView)
        buttons = {"buttons_items": [MagicMock()]}
        contract_objects = [MagicMock(id="C2")]

        self.controller.create_all_contracts_paginated_buttons_signal(paginated_view, buttons, contract_objects)
        self.assertTrue(mock_connect_signal.called)
        self.assertTrue(self.mock_base_view.update_screen.called is False)

    @patch("src.controllers.contract_controller.urwid.connect_signal")
    def test_create_client_contracts(self, mock_connect_signal):
        # Vérifier simplement que la méthode create_form_layout est appelée
        self.controller.create_client_contracts("client@example.com")
        self.mock_base_view.create_form_layout.assert_called_once()
        self.assertTrue(mock_connect_signal.called)

    def test_create_details_view_buttons_signal(self):
        buttons = {"buttons_items": [MagicMock()]}
        self.controller.create_details_view_buttons_signal(buttons, MagicMock(id="C1"))
        # Vérifier qu'il n'y a pas d'erreurs
        self.assertTrue(True)
