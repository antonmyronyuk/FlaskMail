import unittest
from app import app, db
from app.models import User


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        user = User(email='example@example.com')
        user.set_password('some_pass_123')
        self.assertTrue(user.check_password('some_pass_123'))
        self.assertFalse(user.check_password('some_pass_1234'))
        self.assertFalse(user.check_password(''))
        self.assertFalse(user.check_password('sdsdsds'))
