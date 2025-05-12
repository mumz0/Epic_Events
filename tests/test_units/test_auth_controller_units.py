import unittest
from unittest.mock import MagicMock, patch

from src.controllers.auth_controller import AuthController
from src.models.user import User
from src.views.base_view import BaseView


class TestAuthController(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.base_view = MagicMock(spec=BaseView)
        self.current_user = None
        self.history = []
        self.auth_controller = AuthController(self.session, self.base_view, self.current_user, self.history)

    @patch("urwid.connect_signal")
    def test_signin_creates_form_layout(self, mock_connect_signal):
        self.base_view.create_form_layout.return_value = {
            "layout": "mock_layout",
            "buttons": [MagicMock()],
            "edits": [MagicMock(), MagicMock()],
        }

        self.auth_controller.signin()

        self.base_view.create_form_layout.assert_called_once_with(">Authentication", ["Sign In"], ["Email", "Password"])
        self.base_view.update_screen.assert_called_once_with("mock_layout")
        mock_connect_signal.assert_called_once()

    @patch("urwid.connect_signal")
    def test_signin_connects_button_signal(self, mock_connect_signal):
        mock_button = MagicMock()
        self.base_view.create_form_layout.return_value = {
            "layout": "mock_layout",
            "buttons": [mock_button],
            "edits": [MagicMock(), MagicMock()],
        }

        self.auth_controller.signin()

        mock_connect_signal.assert_called_once_with(
            mock_button,
            "click",
            unittest.mock.ANY,
        )

    @patch("urwid.connect_signal")
    def test_signin_updates_screen(self, mock_connect_signal):
        self.base_view.create_form_layout.return_value = {
            "layout": "mock_layout",
            "buttons": [MagicMock()],
            "edits": [MagicMock(), MagicMock()],
        }

        self.auth_controller.signin()

        self.base_view.update_screen.assert_called_once_with("mock_layout")

    @patch("src.controllers.auth_controller.AuthService")
    def test_create_admin_user_success(self, mock_auth_service):
        # Préparer le role admin simulé
        from src.models.role import Role, RoleEnum

        admin_role = Role(name=RoleEnum.ADMIN.value)
        # Simuler la requête de la session pour récupérer le role admin
        self.session.query.return_value.filter_by.return_value.first.return_value = admin_role

        # Patch de la méthode admin_signup_view de BaseView utilisée dans create_admin_user
        with patch("src.controllers.auth_controller.BaseView.admin_signup_view", return_value=("admin@example.com", "password")):
            # Appeler la méthode create_admin_user
            self.auth_controller.create_admin_user()
            # Vérifier que signup_process a été appelé avec les bons paramètres
            mock_auth_service.return_value.signup_process.assert_called_once_with("admin@example.com", "password", admin_role.name, self.session)

    def test_create_admin_user_role_not_found(self):
        # Simuler l'absence de role admin
        self.session.query.return_value.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            self.auth_controller.create_admin_user()

        self.assertEqual(str(context.exception), "Admin role not found.")

    @patch("src.controllers.auth_controller.AuthService")
    def test_handle_auth_form_button_event_success(self, mock_auth_service):
        # Préparer un faux utilisateur retourné par signin_process
        fake_user = MagicMock(spec=User)
        mock_auth_service.return_value.signin_process.return_value = fake_user

        # Créer une fausse layout_dict avec edits
        fake_edit_email = MagicMock()
        fake_edit_email.get_edit_text.return_value = "user@example.com"
        fake_edit_pass = MagicMock()
        fake_edit_pass.get_edit_text.return_value = "secret"
        layout_dict = {"edits": [fake_edit_email, fake_edit_pass]}

        # Créer un faux redirect_func (bien que dans le code, il ne soit pas exécuté)
        redirect_func = MagicMock()

        self.auth_controller.handle_auth_form_button_event(layout_dict, redirect_func)

        # Vérifier que current_user a bien été mis à jour
        self.assertEqual(self.auth_controller.current_user, fake_user)
        # Dans ce cas, la fonction de redirection n’est pas appelée (elle est référencée et non exécutée)
        redirect_func.assert_not_called()
        # Aucune erreur de message n'est affichée
        self.base_view.display_message.assert_not_called()

    @patch("src.controllers.auth_controller.AuthService")
    def test_handle_auth_form_button_event_failure(self, mock_auth_service):
        # Simuler l'échec de la connexion en retournant None
        mock_auth_service.return_value.signin_process.return_value = None

        fake_edit_email = MagicMock()
        fake_edit_email.get_edit_text.return_value = "user@example.com"
        fake_edit_pass = MagicMock()
        fake_edit_pass.get_edit_text.return_value = "wrongpassword"
        layout_dict = {"edits": [fake_edit_email, fake_edit_pass]}
        redirect_func = MagicMock()

        self.auth_controller.handle_auth_form_button_event(layout_dict, redirect_func)

        # Vérifier que display_message est appelée en cas d'échec
        self.base_view.display_message.assert_called_once_with("Signin failed. Please try again.")
        # Et que la redirection n'est pas exécutée
        redirect_func.assert_not_called()

    def test_authentication_process_success(self):
        # Simuler un succès de connexion en définissant current_user à une valeur non nulle
        self.base_view.display_message = MagicMock()
        self.auth_controller.current_user = MagicMock(spec=User)
        # On s'assure que signin ne modifie pas current_user en le surchargant
        self.auth_controller.signin = MagicMock()
        self.auth_controller.authentication_process()
        self.base_view.display_message.assert_called_once_with("Signin successful.")

    def test_authentication_process_failure(self):
        # Simuler un échec de connexion (current_user reste None)
        self.base_view.display_message = MagicMock()
        self.auth_controller.current_user = None
        self.auth_controller.signin = MagicMock()
        self.auth_controller.authentication_process()
        self.base_view.display_message.assert_called_once_with("Signin failed.")
