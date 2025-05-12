import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.repositories.base_repository import BaseRepository
from src.repositories.permission_repository import PermissionRepository
from src.repositories.role_repository import RoleRepository
from src.services.base_service import BaseService


class TestBaseService(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_repository = MagicMock(spec=BaseRepository)
        self.service = BaseService(model=self.mock_model, repository=self.mock_repository)
        self.mock_session = MagicMock()

    def test_create_instance(self):
        data = {"key": "value"}
        instance = self.service.create_instance(data)
        self.mock_model.assert_called_once_with(**data)
        self.assertEqual(instance, self.mock_model.return_value)

    def test_create(self):
        data = {"key": "value"}
        instance = MagicMock()
        self.mock_model.return_value = instance
        self.mock_repository.add.return_value = instance

        result = self.service.create(data, self.mock_session)

        self.mock_model.assert_called_once_with(**data)
        self.mock_repository.add.assert_called_once_with(instance, self.mock_session)
        self.assertEqual(result, instance)

    @patch("sentry_sdk.capture_exception")
    def test_create_exception(self, mock_capture_exception):
        self.mock_model.side_effect = Exception("Test exception")
        data = {"key": "value"}

        with self.assertRaises(ValueError) as context:
            self.service.create(data, self.mock_session)

        mock_capture_exception.assert_called_once()
        self.assertEqual(str(context.exception), "Error creating instance")

    def test_create_all(self):
        data_list = [{"key": "value1"}, {"key": "value2"}]
        instances = [MagicMock(), MagicMock()]
        self.mock_model.side_effect = instances
        self.mock_repository.add_all.return_value = instances

        result = self.service.create_all(data_list, self.mock_session)

        self.assertEqual(self.mock_model.call_count, len(data_list))
        self.mock_repository.add_all.assert_called_once_with(instances, self.mock_session)
        self.assertEqual(result, instances)

    def test_get(self):
        instance_id = 1
        instance = MagicMock()
        self.mock_repository.get.return_value = instance

        result = self.service.get(instance_id, self.mock_session)

        self.mock_repository.get.assert_called_once_with(instance_id, self.mock_session)
        self.assertEqual(result, instance)

    def test_get_id(self):
        instance_name = "test_name"
        instance = MagicMock()
        self.mock_repository.get_id.return_value = instance

        result = self.service.get_id(instance_name, self.mock_session)

        self.mock_repository.get_id.assert_called_once_with(instance_name, self.mock_session)
        self.assertEqual(result, instance)

    def test_update(self):
        instance_id = 1
        data = {"key": "value"}
        updated_instance = MagicMock()
        self.mock_repository.update_obj.return_value = updated_instance

        result = self.service.update(instance_id, data, self.mock_session)

        self.mock_repository.update_obj.assert_called_once_with(instance_id, data, self.mock_session)
        self.assertEqual(result, updated_instance)

    def test_delete(self):
        instance_id = 1
        deleted_instance = MagicMock()
        self.mock_repository.delete.return_value = deleted_instance

        result = self.service.delete(instance_id, self.mock_session)

        self.mock_repository.delete.assert_called_once_with(instance_id, self.mock_session)
        self.assertEqual(result, deleted_instance)

    def test_remove_attributes_from_object(self):
        object_template = {"key1": "value1", "key2": "value2"}
        attributes_to_remove = ["key1"]

        result = self.service.remove_attributes_from_object(object_template, attributes_to_remove)

        self.assertNotIn("key1", result)
        self.assertIn("key2", result)

    def test_datetime_to_string(self):
        date_obj = datetime(2023, 1, 1)
        result = BaseService.datetime_to_string(date_obj)
        self.assertEqual(result, "2023/01/01")

    @patch("sentry_sdk.capture_exception")
    def test_datetime_to_string_exception(self, mock_capture_exception):
        result = BaseService.datetime_to_string(None)
        mock_capture_exception.assert_called_once()
        self.assertEqual(result, "")

    def test_get_all_with_role_repository(self):
        self.service.repository = MagicMock(spec=RoleRepository)
        self.service.get_all = MagicMock(side_effect=PermissionError("Access to this method is not allowed."))

        with self.assertRaises(PermissionError) as context:
            self.service.get_all(self.mock_session)

        self.assertEqual(str(context.exception), "Access to this method is not allowed.")

    def test_get_all_with_permission_repository(self):
        self.service.repository = MagicMock(spec=PermissionRepository)
        self.service.get_all = MagicMock(side_effect=PermissionError("Access to this method is not allowed."))

        with self.assertRaises(PermissionError) as context:
            self.service.get_all(self.mock_session)

        self.assertEqual(str(context.exception), "Access to this method is not allowed.")

    @patch("sentry_sdk.capture_exception")
    def test_get_all_exception(self, mock_capture_exception):
        self.mock_repository.get_all.side_effect = Exception("Test exception")
        self.service.repository = self.mock_repository

        result = self.service.get_all(self.mock_session)

        mock_capture_exception.assert_called_once()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
