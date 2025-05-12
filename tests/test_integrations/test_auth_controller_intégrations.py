from src.controllers.auth_controller import AuthController
from src.models.role import Role, RoleEnum
from src.models.user import User
from src.services.auth_service import AuthService
from src.views.base_view import BaseView
from tests.test_integrations.run_tests import BaseTestDB


class TestAuthControllerIntegration(BaseTestDB):

    def setUp(self):
        super().setUp()
        self.base_view = BaseView()
        self.history = []
        self.current_user = None

        self.auth_controller = AuthController(self.session, self.base_view, self.current_user, self.history)

    def test_create_admin_user_success(self):
        admin_role = Role(name=RoleEnum.ADMIN.value)
        self.session.add(admin_role)
        self.session.commit()

        email = "admin@example.com"
        password = "securepassword"
        self.base_view.admin_signup_view = lambda: (email, password)

        AuthService(None).signup_process(email, password, RoleEnum.ADMIN.value, self.session)
        admin_user = self.session.query(User).filter_by(email_address=email).first()

        self.assertIsNotNone(admin_user)
        self.assertIsNotNone(admin_user.role)
        self.assertEqual(admin_user.role.name, RoleEnum.ADMIN.value)

    def test_create_admin_user_role_not_found(self):
        self.session.query(Role).filter_by(name=RoleEnum.ADMIN.value).delete()
        self.session.flush()

        email = "admin1@example.com"
        password = "securepassword"
        self.base_view.admin_signup_view = lambda: (email, password)
        admin_role = self.session.query(Role).filter_by(name=RoleEnum.ADMIN.value).first()

        self.assertFalse(AuthService(None).signup_process(email, password, admin_role, self.session))
        self.session.rollback

    def test_create_admin_user_duplicate_email(self):
        email = "admin@example.com"
        password = "securepassword"
        admin_role = self.session.query(Role).filter_by(name=RoleEnum.ADMIN.value).first()
        existing_admin = User(email_address=email, password=password, role=admin_role)
        self.session.add(existing_admin)
        self.session.flush()

        self.base_view.admin_signup_view = lambda: (email, "newpassword")

        self.assertTrue(AuthService(None).signup_process(email, password, admin_role, self.session))
        self.session.rollback()

    def tearDown(self):
        """
        Cleans up the database by removing all data created during the tests.
        """
        self.session.query(User).delete()
        self.session.commit()
        super().tearDown()
