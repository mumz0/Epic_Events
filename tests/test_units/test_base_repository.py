import unittest
from unittest.mock import MagicMock, patch

from src.repositories.base_repository import BaseRepository

class DummyModel:
    def __init__(self, id=None, name=None, **kwargs):
        self.id = id
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

class TestBaseRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.repo = BaseRepository(DummyModel)

    def test_add_success(self):
        inst = DummyModel(id=1)
        result = self.repo.add(inst, self.session)
        self.session.add.assert_called_once_with(inst)
        self.session.commit.assert_called_once()
        self.assertIs(result, inst)

    def test_add_all_success(self):
        insts = [DummyModel(id=1), DummyModel(id=2)]
        result = self.repo.add_all(insts, self.session)
        self.session.add_all.assert_called_once_with(insts)
        self.session.commit.assert_called_once()
        self.assertEqual(result, insts)

    def test_get_success(self):
        inst = DummyModel(id=5)
        query = MagicMock()
        query.get.return_value = inst
        self.session.query.return_value = query
        result = self.repo.get(5, self.session)
        self.session.query.assert_called_once_with(DummyModel)
        self.assertIs(result, inst)

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_get_not_found_raises(self, mock_msg):
        query = MagicMock()
        query.get.return_value = None
        self.session.query.return_value = query
        with self.assertRaises(ValueError) as cm:
            self.repo.get(99, self.session)
        mock_msg.assert_called_once_with("Instance with ID 99 not found.")
        self.assertIn("Instance with ID 99 not found.", str(cm.exception))

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_get_exception_raises(self, mock_exc):
        query = MagicMock()
        query.get.side_effect = RuntimeError("db fail")
        self.session.query.return_value = query
        with self.assertRaises(ValueError) as cm:
            self.repo.get(1, self.session)
        mock_exc.assert_called_once()
        self.assertIn("Error retrieving instance by ID", str(cm.exception))

    def test_get_id_success(self):
        inst = DummyModel(name="foo")
        filt = MagicMock()
        filt.first.return_value = inst
        self.session.query.return_value.filter_by.return_value = filt
        result = self.repo.get_id("foo", self.session)
        self.session.query.assert_called_once_with(DummyModel)
        self.assertIs(result, inst)

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_get_id_not_found_raises(self, mock_msg):
        filt = MagicMock()
        filt.first.return_value = None
        self.session.query.return_value.filter_by.return_value = filt
        with self.assertRaises(ValueError):
            self.repo.get_id("bar", self.session)
        mock_msg.assert_called_once_with("Instance with name bar not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_get_id_exception_raises(self, mock_exc):
        filt = MagicMock()
        filt.first.side_effect = Exception("oops")
        self.session.query.return_value.filter_by.return_value = filt
        with self.assertRaises(ValueError):
            self.repo.get_id("x", self.session)
        mock_exc.assert_called_once()

    def test_get_all_success(self):
        items = [DummyModel(id=1), DummyModel(id=2)]
        query = MagicMock()
        query.all.return_value = items
        self.session.query.return_value = query
        result = self.repo.get_all(self.session)
        self.session.query.assert_called_once_with(DummyModel)
        self.assertEqual(result, items)

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_get_all_exception_raises(self, mock_exc):
        query = MagicMock()
        query.all.side_effect = RuntimeError("fail")
        self.session.query.return_value = query
        with self.assertRaises(ValueError):
            self.repo.get_all(self.session)
        mock_exc.assert_called_once()

    def test_update_obj_success(self):
        inst = DummyModel(id=10, foo="old")
        query = MagicMock()
        query.get.return_value = inst
        self.session.query.return_value = query
        data = {"foo": "new", "noattr": 123}
        result = self.repo.update_obj(10, data, self.session)
        self.assertIs(result, inst)
        self.assertEqual(inst.foo, "new")
        self.session.commit.assert_called_once()

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_update_obj_not_found(self, mock_msg):
        query = MagicMock(get=MagicMock(return_value=None))
        self.session.query.return_value = query
        with self.assertRaises(ValueError):
            self.repo.update_obj(7, {"a": 1}, self.session)
        mock_msg.assert_called_once_with("Instance with ID 7 not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_update_obj_exception(self, mock_exc):
        query = MagicMock()
        query.get.side_effect = Exception("err")
        self.session.query.return_value = query
        with self.assertRaises(ValueError):
            self.repo.update_obj(1, {"a": 1}, self.session)
        mock_exc.assert_called_once()

    def test_update_attr_success(self):
        inst = DummyModel(id=3)
        filt = MagicMock()
        filt.first.return_value = inst
        self.session.query.return_value.filter_by.return_value = filt
        result = self.repo.update_attr(3, "name", "newname", self.session)
        self.assertIs(result, inst)
        self.assertEqual(inst.name, "newname")
        self.session.commit.assert_called_once()

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_update_attr_not_found(self, mock_msg):
        filt = MagicMock()
        filt.first.return_value = None
        self.session.query.return_value.filter_by.return_value = filt
        with self.assertRaises(ValueError):
            self.repo.update_attr(5, "x", "v", self.session)
        mock_msg.assert_called_once_with("Instance with ID 5 not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_update_attr_exception(self, mock_exc):
        filt = MagicMock()
        filt.first.side_effect = RuntimeError("fail")
        self.session.query.return_value.filter_by.return_value = filt
        with self.assertRaises(ValueError):
            self.repo.update_attr(2, "x", "v", self.session)
        mock_exc.assert_called_once()

    def test_delete_success(self):
        inst = DummyModel(id=4)
        filt = MagicMock()
        filt.first.return_value = inst
        self.session.query.return_value.filter_by.return_value = filt
        result = self.repo.delete(4, self.session)
        self.assertIs(result, inst)
        self.session.delete.assert_called_once_with(inst)
        self.session.commit.assert_called_once()

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_delete_not_found(self, mock_msg):
        filt = MagicMock(first=MagicMock(return_value=None))
        self.session.query.return_value.filter_by.return_value = filt
        with self.assertRaises(ValueError):
            self.repo.delete(8, self.session)
        mock_msg.assert_called_once_with("Instance with ID 8 not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_delete_exception(self, mock_exc):
        filt = MagicMock()
        filt.first.side_effect = Exception("oops")
        self.session.query.return_value.filter_by.return_value = filt
        with self.assertRaises(ValueError):
            self.repo.delete(9, self.session)
        mock_exc.assert_called_once()
