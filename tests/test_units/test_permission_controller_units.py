import unittest
from unittest.mock import patch, MagicMock

from src.controllers.permission_controller import PermissionController

class TestPermissionController(unittest.TestCase):

    @patch("src.controllers.permission_controller.PermissionService")
    def test_create_permissions_success(self, mock_perm_svc_cls):
        # Arrange: PermissionService().create_instance returns a string per action
        mock_svc = MagicMock()
        mock_svc.create_instance.side_effect = lambda data: f"created:{data['action']}"
        mock_perm_svc_cls.return_value = mock_svc

        ctrl = PermissionController()

        # Act
        result = ctrl.create_permissions()

        # Assert: one call per expected action, in order
        expected_actions = [
            "user_create", "user_read", "user_update", "user_delete",
            "client_create", "client_read", "client_update", "client_delete",
            "contract_create", "contract_read", "contract_update", "contract_delete",
            "event_create", "event_read", "event_update", "event_delete",
        ]
        self.assertEqual(len(result), len(expected_actions))
        for idx, action in enumerate(expected_actions):
            mock_svc.create_instance.assert_any_call({"action": action})
            self.assertEqual(result[idx], f"created:{action}")

    @patch("src.controllers.permission_controller.PermissionService")
    def test_create_permissions_exception_propagates(self, mock_perm_svc_cls):
        # Arrange: raise on one of the actions
        mock_svc = MagicMock()
        def side_effect(data):
            if data["action"] == "client_read":
                raise RuntimeError("boom")
            return data["action"]
        mock_svc.create_instance.side_effect = side_effect
        mock_perm_svc_cls.return_value = mock_svc
        ctrl = PermissionController()

        # Act & Assert: exception bubbles out
        with self.assertRaises(RuntimeError):
            ctrl.create_permissions()

        # Ensure calls happened up to the failing action
        mock_svc.create_instance.assert_any_call({"action": "user_create"})
        mock_svc.create_instance.assert_any_call({"action": "user_read"})
        mock_svc.create_instance.assert_any_call({"action": "user_update"})
        mock_svc.create_instance.assert_any_call({"action": "user_delete"})
        mock_svc.create_instance.assert_any_call({"action": "client_create"})
        mock_svc.create_instance.assert_any_call({"action": "client_read"})

if __name__ == "__main__":
    unittest.main()