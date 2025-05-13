import unittest
from unittest.mock import patch, MagicMock

from src.controllers.role_controller import RoleController
from src.models.role import RoleEnum


class DummyPerm:
    def __init__(self, action):
        self.action = action


class TestRoleController(unittest.TestCase):
    def setUp(self):
        self.ctrl = RoleController()
        self.session = MagicMock()
        # build a list of dummy permission objects
        actions = [
            "user_create", "user_read", "user_update", "user_delete",
            "client_create", "client_read", "client_update", "client_delete",
            "contract_create", "contract_read", "contract_update", "contract_delete",
            "event_create", "event_read", "event_update", "event_delete",
        ]
        self.permission_objs = [DummyPerm(a) for a in actions]

    @patch("src.controllers.role_controller.RoleService")
    def test_create_admin_role(self, mock_rs_cls):
        # arrange
        mock_svc = MagicMock()
        mock_rs_cls.return_value = mock_svc
        expected_data = {
            "name": RoleEnum.ADMIN.value,
            "permissions": self.permission_objs
        }
        # act
        result = self.ctrl.create_admin_role(self.permission_objs, self.session)
        # assert
        mock_svc.create.assert_called_once_with(expected_data, self.session)
        self.assertIs(result, mock_svc.create.return_value)

    @patch("src.controllers.role_controller.RoleService")
    def test_create_management_role(self, mock_rs_cls):
        mock_svc = MagicMock()
        mock_rs_cls.return_value = mock_svc
        # include only actions allowed for management
        permission_objs = [
            DummyPerm("user_create"),
            DummyPerm("contract_delete"),
            DummyPerm("client_read"),
            DummyPerm("event_update"),
            DummyPerm("something_else"),
        ]
        # act
        self.ctrl.create_management_role(permission_objs, self.session)
        # assert: create called once with filtered permissions
        expected_perms = ["user_create", "client_read", "event_update"]
        called_data = mock_svc.create.call_args[0][0]
        self.assertEqual(called_data["name"], RoleEnum.MANAGEMENT.value)
        got_actions = [p.action for p in called_data["permissions"]]
        self.assertCountEqual(got_actions, expected_perms)

    @patch("src.controllers.role_controller.RoleService")
    def test_create_sales_role(self, mock_rs_cls):
        mock_svc = MagicMock()
        mock_rs_cls.return_value = mock_svc
        permission_objs = [
            DummyPerm("user_read"),
            DummyPerm("client_create"),
            DummyPerm("contract_update"),
            DummyPerm("event_read"),
            DummyPerm("unrelated"),
        ]
        self.ctrl.create_sales_role(permission_objs, self.session)
        expected_perms = ["user_read", "client_create", "contract_update", "event_read"]
        called_data = mock_svc.create.call_args[0][0]
        self.assertEqual(called_data["name"], RoleEnum.SALES.value)
        got_actions = [p.action for p in called_data["permissions"]]
        self.assertCountEqual(got_actions, expected_perms)

    @patch("src.controllers.role_controller.RoleService")
    def test_create_support_role(self, mock_rs_cls):
        mock_svc = MagicMock()
        mock_rs_cls.return_value = mock_svc
        permission_objs = [
            DummyPerm("user_read"),
            DummyPerm("event_read"),
            DummyPerm("event_update"),
            DummyPerm("contract_read"),
            DummyPerm("client_read"),
            DummyPerm("other"),
        ]
        self.ctrl.create_support_role(permission_objs, self.session)
        expected_perms = ["user_read", "event_read", "event_update", "contract_read", "client_read"]
        called_data = mock_svc.create.call_args[0][0]
        self.assertEqual(called_data["name"], RoleEnum.SUPPORT.value)
        got_actions = [p.action for p in called_data["permissions"]]
        self.assertCountEqual(got_actions, expected_perms)

    @patch.object(RoleController, "create_admin_role")
    @patch.object(RoleController, "create_management_role")
    @patch.object(RoleController, "create_sales_role")
    @patch.object(RoleController, "create_support_role")
    def test_create_roles_calls_all(self,
            mock_support, mock_sales, mock_mgmt, mock_admin):
        # act
        self.ctrl.create_roles(self.permission_objs, self.session)
        # assert each helper called once with same args
        mock_admin.assert_called_once_with(self.permission_objs, self.session)
        mock_mgmt.assert_called_once_with(self.permission_objs, self.session)
        mock_sales.assert_called_once_with(self.permission_objs, self.session)
        mock_support.assert_called_once_with(self.permission_objs, self.session)
