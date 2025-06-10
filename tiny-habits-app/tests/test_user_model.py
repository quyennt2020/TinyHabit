import unittest
from app import db
from app.models import User
from tests.test_basic import BasicTests

class TestUserModel(BasicTests):

    def test_password_hashing(self):
        """Test password hashing and checking."""
        u = User(username='susan', email='susan@example.com')
        u.set_password('correct_password')
        self.assertIsNotNone(u.password_hash)
        self.assertNotEqual(u.password_hash, 'correct_password')
        self.assertTrue(u.check_password('correct_password'))
        self.assertFalse(u.check_password('wrong_password'))

    def test_user_creation_defaults(self):
        """Test default values upon user creation (if any beyond ORM)."""
        # This model doesn't have many non-ORM defaults other than those tested by ORM itself
        # (e.g. id assigned on commit). If there were specific defaults in the model's __init__
        # or @declarative_mixin, they would be tested here.
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(u.id)
        # Example: if a user had a default role or status
        # self.assertEqual(u.status, 'active')

    def test_repr(self):
        """Test the __repr__ method of the User model."""
        u = User(username='testuser_repr', email='repr@example.com')
        db.session.add(u)
        db.session.commit()
        expected_repr = f'<User {u.username}>'
        self.assertEqual(repr(u), expected_repr)

if __name__ == '__main__':
    unittest.main()
