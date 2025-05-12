import unittest

from sqlalchemy.orm import sessionmaker

from tests.test_integrations.init_test_db import engine_obj, initialize_database_filled


class BaseTestDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database_filled()
        cls.engine = engine_obj.engine
        cls.SessionFactory = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.SessionFactory()

    def tearDown(self):
        self.session.close()
