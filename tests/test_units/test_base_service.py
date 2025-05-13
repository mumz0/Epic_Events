import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.services.base_service import BaseService
from src.repositories.role_repository import RoleRepository
from src.repositories.permission_repository import PermissionRepository


class DummyModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestBaseService(unittest.TestCase):
    def setUp(self):
        # prepare a dummy repository with MagicMock methods
        self.repo = MagicMock()
        self.session = MagicMock()
        self.service = BaseService(model=DummyModel, repository=self.repo)

    def test_create_instance(self):
        data = {"a": 1, "b": 2}
        inst = self.service.create_instance(data)
        self.assertIsInstance(inst, DummyModel)
        self.assertEqual(inst.a, 1)
        self.assertEqual(inst.b, 2)

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_create_success(self, mock_capture_exc):
        expected = DummyModel(x=10)
        self.repo.add.return_value = expected
        result = self.service.create({"x": 10}, self.session)
        self.repo.add.assert_called_once()
        self.assertIs(result, expected)
        mock_capture_exc.assert_not_called()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_create_exception(self, mock_capture_exc):
        self.repo.add.side_effect = RuntimeError("fail")
        with self.assertRaises(ValueError) as cm:
            self.service.create({"x": 1}, self.session)
        self.assertEqual(str(cm.exception), "Error creating instance")
        mock_capture_exc.assert_called_once()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_create_all_success(self, mock_capture_exc):
        data_list = [{"a": 1}, {"a": 2}]
        expected = [DummyModel(a=1), DummyModel(a=2)]
        self.repo.add_all.return_value = expected
        result = self.service.create_all(data_list, self.session)
        self.repo.add_all.assert_called_once()
        self.assertEqual(result, expected)
        mock_capture_exc.assert_not_called()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_create_all_exception(self, mock_capture_exc):
        self.repo.add_all.side_effect = Exception("boom")
        with self.assertRaises(ValueError) as cm:
            self.service.create_all([{"x": 1}], self.session)
        self.assertEqual(str(cm.exception), "Error creating instances")
        mock_capture_exc.assert_called_once()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_get_success(self, mock_capture_exc):
        expected = DummyModel(id=5)
        self.repo.get.return_value = expected
        result = self.service.get(5, self.session)
        self.repo.get.assert_called_once_with(5, self.session)
        self.assertIs(result, expected)

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_get_exception(self, mock_capture_exc):
        self.repo.get.side_effect = Exception("err")
        result = self.service.get(1, self.session)
        self.assertIsNone(result)
        mock_capture_exc.assert_called_once()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_get_id_success(self, mock_capture_exc):
        expected = DummyModel(name="foo")
        self.repo.get_id.return_value = expected
        result = self.service.get_id("foo", self.session)
        self.repo.get_id.assert_called_once_with("foo", self.session)
        self.assertIs(result, expected)

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_get_id_exception(self, mock_capture_exc):
        self.repo.get_id.side_effect = Exception("err")
        result = self.service.get_id("bar", self.session)
        self.assertIsNone(result)
        mock_capture_exc.assert_called_once()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_get_all_success(self, mock_capture_exc):
        self.repo.get_all.return_value = [1, 2, 3]
        result = self.service.get_all(self.session)
        self.repo.get_all.assert_called_once_with(self.session)
        self.assertEqual(result, [1, 2, 3])
        mock_capture_exc.assert_not_called()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_get_all_forbidden(self, mock_capture_exc):
        # inject a RoleRepository to trigger PermissionError
        svc = BaseService(model=DummyModel, repository=RoleRepository())
        result = svc.get_all(self.session)
        self.assertEqual(result, [])
        mock_capture_exc.assert_called()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_update_success(self, mock_capture_exc):
        expected = DummyModel(u=1)
        self.repo.update_obj.return_value = expected
        result = self.service.update(1, {"u": 1}, self.session)
        self.repo.update_obj.assert_called_once()
        self.assertIs(result, expected)

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_update_exception(self, mock_capture_exc):
        self.repo.update_obj.side_effect = Exception("fail")
        result = self.service.update(1, {}, self.session)
        self.assertIsNone(result)
        mock_capture_exc.assert_called_once()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_delete_success(self, mock_capture_exc):
        expected = DummyModel(d=2)
        self.repo.delete.return_value = expected
        result = self.service.delete(2, self.session)
        self.repo.delete.assert_called_once()
        self.assertIs(result, expected)

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_delete_exception(self, mock_capture_exc):
        self.repo.delete.side_effect = Exception("fail")
        result = self.service.delete(2, self.session)
        self.assertIsNone(result)
        mock_capture_exc.assert_called_once()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_remove_attributes_from_object(self, mock_capture_exc):
        obj = {"a": 1, "b": 2, "c": 3}
        out = self.service.remove_attributes_from_object(obj.copy(), ["b", "c", "x"])
        self.assertEqual(out, {"a": 1})
        mock_capture_exc.assert_not_called()

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_remove_attributes_exception(self, mock_capture_exc):
        # simulate pop failure
        bad = MagicMock()
        bad.pop.side_effect = Exception("oops")
        out = self.service.remove_attributes_from_object(bad, ["a"])
        self.assertEqual(out, {})
        mock_capture_exc.assert_called_once()

    def test_datetime_to_string_success(self):
        dt = datetime(2020, 5, 17)
        self.assertEqual(BaseService.datetime_to_string(dt), "2020/05/17")

    @patch("src.services.base_service.sentry_sdk.capture_exception")
    def test_datetime_to_string_exception(self, mock_capture_exc):
        # passing bad object
        self.assertEqual(BaseService.datetime_to_string(None), "")
        mock_capture_exc.assert_called_once()
