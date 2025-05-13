import unittest
from unittest.mock import MagicMock, patch

from src.repositories.client_repository import ClientRepository
from src.models.client import Client


class DummyClientModel:
    def __init__(self, id=None, name=None, **kwargs):
        self.id = id
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)


class QueryFake:
     def __init__(self, result=None, exc=None):
         self._result = result
         self._exc = exc

     def get(self, _id):
         if self._exc:
             raise self._exc
         return self._result

     def filter_by(self, **kwargs):
         if self._exc:
             raise self._exc
         return self

     def first(self):
         if self._exc:
             raise self._exc
         return self._result

     def all(self):
         if self._exc:
             raise self._exc
         return self._result


class TestClientRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.repo = ClientRepository()

    def test_init_sets_model(self):
        self.assertIs(self.repo.model, Client)

    def test_get_all_delegates_to_session(self):
        items = [Client(id=1), Client(id=2)]
        self.session.query.return_value.all.return_value = items
        result = self.repo.get_all(self.session)
        self.session.query.assert_called_once_with(Client)
        self.assertEqual(result, items)

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_get_all_exception(self, mock_exc):
        self.session.query.return_value.all.side_effect = RuntimeError("fail")
        with self.assertRaises(ValueError):
            self.repo.get_all(self.session)
        mock_exc.assert_called_once()

    def test_get_success(self):
        inst = Client(id=10)
        self.session.query.return_value = QueryFake(result=inst)
        result = self.repo.get(10, self.session)
        self.assertIs(result, inst)

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_get_not_found(self, mock_msg):
        self.session.query.return_value = QueryFake(result=None)
        with self.assertRaises(ValueError) as cm:
            self.repo.get(5, self.session)
        mock_msg.assert_called_once_with("Instance with ID 5 not found.")
        self.assertIn("Instance with ID 5 not found.", str(cm.exception))

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_get_exception(self, mock_exc):
        self.session.query.return_value = QueryFake(exc=RuntimeError("err"))
        with self.assertRaises(ValueError):
            self.repo.get(1, self.session)
        mock_exc.assert_called_once()

    def test_get_id_success(self):
        inst = Client(id=20, name="C1")
        self.session.query.return_value = QueryFake(result=inst)
        result = self.repo.get_id("C1", self.session)
        self.assertIs(result, inst)

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_get_id_not_found(self, mock_msg):
        self.session.query.return_value = QueryFake(result=None)
        with self.assertRaises(ValueError):
            self.repo.get_id("X", self.session)
        mock_msg.assert_called_once_with("Instance with name X not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_get_id_exception(self, mock_exc):
        self.session.query.return_value = QueryFake(exc=Exception("oops"))
        with self.assertRaises(ValueError):
            self.repo.get_id("Y", self.session)
        mock_exc.assert_called_once()

    def test_update_obj_success(self):
        inst = Client(id=3)
        q = QueryFake(result=inst)
        self.session.query.return_value = q
        data = {"name": "NewName", "foo": "ignored"}
        result = self.repo.update_obj(3, data, self.session)
        self.assertIs(result, inst)
        self.assertEqual(inst.name, "NewName")
        self.session.commit.assert_called_once()

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_update_obj_not_found(self, mock_msg):
        self.session.query.return_value = QueryFake(result=None)
        with self.assertRaises(ValueError):
            self.repo.update_obj(7, {"name": "X"}, self.session)
        mock_msg.assert_called_once_with("Instance with ID 7 not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_update_obj_exception(self, mock_exc):
        self.session.query.return_value = QueryFake(exc=Exception("fail"))
        with self.assertRaises(ValueError):
            self.repo.update_obj(8, {"name": "X"}, self.session)
        mock_exc.assert_called_once()

    def test_update_attr_success(self):
        inst = Client(id=4, name="Old")
        q = QueryFake(result=inst)
        self.session.query.return_value = MagicMock(filter_by=lambda **kw: q)
        result = self.repo.update_attr(4, "name", "BrandNew", self.session)
        self.assertIs(result, inst)
        self.assertEqual(inst.name, "BrandNew")
        self.session.commit.assert_called_once()

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_update_attr_not_found(self, mock_msg):
        q = QueryFake(result=None)
        self.session.query.return_value = MagicMock(filter_by=lambda **kw: q)
        with self.assertRaises(ValueError):
            self.repo.update_attr(9, "name", "X", self.session)
        mock_msg.assert_called_once_with("Instance with ID 9 not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_update_attr_exception(self, mock_exc):
        q = QueryFake(exc=RuntimeError("err"))
        self.session.query.return_value = MagicMock(filter_by=lambda **kw: q)
        with self.assertRaises(ValueError):
            self.repo.update_attr(9, "name", "X", self.session)
        mock_exc.assert_called_once()

    def test_delete_success(self):
        inst = Client(id=5)
        q = QueryFake(result=inst)
        self.session.query.return_value = MagicMock(filter_by=lambda **kw: q)
        result = self.repo.delete(5, self.session)
        self.assertIs(result, inst)
        self.session.delete.assert_called_once_with(inst)
        self.session.commit.assert_called_once()

    @patch('src.repositories.base_repository.sentry_sdk.capture_message')
    def test_delete_not_found(self, mock_msg):
        q = QueryFake(result=None)
        self.session.query.return_value = MagicMock(filter_by=lambda **kw: q)
        with self.assertRaises(ValueError):
            self.repo.delete(6, self.session)
        mock_msg.assert_called_once_with("Instance with ID 6 not found.")

    @patch('src.repositories.base_repository.sentry_sdk.capture_exception')
    def test_delete_exception(self, mock_exc):
        q = QueryFake(exc=Exception("oops"))
        self.session.query.return_value = MagicMock(filter_by=lambda **kw: q)
        with self.assertRaises(ValueError):
            self.repo.delete(7, self.session)
        mock_exc.assert_called_once()