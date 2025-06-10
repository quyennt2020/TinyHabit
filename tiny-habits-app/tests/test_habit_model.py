import unittest
from datetime import datetime
from app import db
from app.models import User, Habit
from tests.test_basic import BasicTests

class TestHabitModel(BasicTests):

    def _create_user(self, username='testuser', email='test@example.com', password='password'):
        """Helper method to create and return a user."""
        user = User(username=username, email=email)
        user.set_password(password)
        # Note: We don't add or commit here, let the test method decide
        return user

    def test_habit_creation(self):
        """Test the creation of a Habit instance."""
        # Create and save a user first
        user = self._create_user()
        db.session.add(user)
        db.session.commit()

        # Now create a habit associated with this user
        habit = Habit(
            anchor_moment='After I wake up',
            tiny_behavior='I will drink a glass of water',
            celebration='I will say "Hydrated!"',
            author=user  # Associate with the user object
        )
        db.session.add(habit)
        db.session.commit()

        self.assertIsNotNone(habit.id, "Habit ID should not be None after saving.")
        self.assertEqual(habit.author, user, "Habit author should match the created user.")
        self.assertEqual(habit.user_id, user.id, "Habit user_id should match the created user's id.")
        self.assertIsNotNone(habit.creation_date, "Habit creation_date should not be None.")
        self.assertIsInstance(habit.creation_date, datetime, "creation_date should be a datetime object.")
        self.assertEqual(habit.streak, 0, "Default streak should be 0.")
        self.assertIsNone(habit.last_completed_date, "last_completed_date should be None initially.")

    def test_habit_repr(self):
        """Test the __repr__ method of the Habit model."""
        user = self._create_user(username="repr_user", email="repr_user@example.com")
        db.session.add(user)
        db.session.commit()

        habit_behavior = 'Test this repr'
        habit = Habit(
            anchor_moment='Anchor for repr',
            tiny_behavior=habit_behavior,
            celebration='Celebrate repr',
            author=user
        )
        db.session.add(habit)
        db.session.commit()

        expected_repr = f'<Habit {habit_behavior}>'
        self.assertEqual(repr(habit), expected_repr)

if __name__ == '__main__':
    unittest.main()
