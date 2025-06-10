import unittest
from datetime import date, timedelta, datetime
from flask import url_for, session
from app import app, db
from app.models import User, Habit
from tests.test_basic import BasicTests

class TestMainRoutes(BasicTests):

    def _register_and_login_user(self, username='testuser', email='test@example.com', password='password'):
        """Helper to register (directly) and login a user (via POST). Returns the User object."""
        # Direct registration
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Login via POST
        self.client.post(
            url_for('login'),
            data=dict(email=email, password=password),
            follow_redirects=True
        )
        return user # Return the persisted user object

    def _create_habit(self, user, anchor='Anchor', behavior='Behavior', celebration='Celebration'):
        """Helper to create and commit a habit for a user."""
        habit = Habit(
            author=user,
            anchor_moment=anchor,
            tiny_behavior=behavior,
            celebration=celebration
        )
        db.session.add(habit)
        db.session.commit()
        return habit

    # --- Dashboard Tests ---
    def test_dashboard_unauthenticated_redirects(self):
        """Test GET /dashboard when not logged in redirects to login."""
        response = self.client.get(url_for('dashboard'), follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith(url_for('login')))

    def test_dashboard_authenticated_renders(self):
        """Test GET /dashboard when logged in renders correctly."""
        self._register_and_login_user()
        response = self.client.get(url_for('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your Tiny Habits Dashboard", response.data)
        self.assertIn(b"Welcome, testuser!", response.data)

    def test_dashboard_displays_habits(self):
        """Test dashboard displays created habits."""
        user = self._register_and_login_user()
        self._create_habit(user, anchor="After dinner", behavior="Wash one dish", celebration="Sparkling clean!")
        response = self.client.get(url_for('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"After dinner", response.data)
        self.assertIn(b"Wash one dish", response.data)
        self.assertIn(b"Sparkling clean!", response.data)

    def test_dashboard_no_habits_message(self):
        """Test dashboard shows a message if no habits are created."""
        self._register_and_login_user()
        response = self.client.get(url_for('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You haven't added any tiny habits yet.", response.data)

    # --- Add Habit Tests ---
    def test_add_habit_unauthenticated_redirects(self):
        """Test GET /add_habit when not logged in redirects to login."""
        response = self.client.get(url_for('add_habit'), follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith(url_for('login')))

    def test_get_add_habit_page_authenticated(self):
        """Test GET /add_habit when logged in renders correctly."""
        self._register_and_login_user()
        response = self.client.get(url_for('add_habit'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add New Habit", response.data)
        self.assertIn(b"Anchor Moment", response.data)
        self.assertIn(b"New Tiny Habit", response.data)
        self.assertIn(b"Celebration", response.data)

    def test_add_habit_successful(self):
        """Test POST to /add_habit with valid data creates habit and redirects."""
        user = self._register_and_login_user()
        response = self.client.post(
            url_for('add_habit'),
            data=dict(anchor_moment="Morning coffee", tiny_behavior="Read one page", celebration="Learned something!"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b"Your Tiny Habits Dashboard", response.data)
        self.assertIn(b"New tiny habit added!", response.data) # Flash message

        habit = Habit.query.filter_by(tiny_behavior="Read one page").first()
        self.assertIsNotNone(habit)
        self.assertEqual(habit.author, user)
        self.assertEqual(habit.anchor_moment, "Morning coffee")

    def test_add_habit_invalid_data(self):
        """Test POST to /add_habit with invalid/missing data re-renders form with errors."""
        self._register_and_login_user()
        response = self.client.post(
            url_for('add_habit'),
            data=dict(anchor_moment="", tiny_behavior="This will fail", celebration="No anchor"), # Missing anchor
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Re-renders add_habit form
        self.assertIn(b"Add New Habit", response.data)
        self.assertIn(b"This field is required.", response.data) # WTForms default error for DataRequired

    # --- Complete Habit Tests ---
    def test_complete_habit_unauthenticated_redirects(self):
        """Test POST /complete_habit when not logged in redirects."""
        # Create a dummy habit to have an ID, doesn't matter who owns it for this test
        user = User(username='tempuser', email='temp@example.com')
        user.set_password('temp')
        db.session.add(user)
        db.session.commit()
        habit = self._create_habit(user)

        response = self.client.post(url_for('complete_habit', habit_id=habit.id), follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith(url_for('login')))

    def test_complete_habit_successful_first_time(self):
        """Test completing a habit for the first time."""
        user = self._register_and_login_user()
        habit = self._create_habit(user, behavior="First complete")

        response = self.client.post(url_for('complete_habit', habit_id=habit.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b"Awesome! You completed 'First complete'. Now, don't forget your celebration: 'Celebration'!", response.data)

        updated_habit = Habit.query.get(habit.id)
        self.assertIsNotNone(updated_habit.last_completed_date)
        self.assertEqual(updated_habit.last_completed_date.date(), date.today())
        self.assertEqual(updated_habit.streak, 1)

    def test_complete_habit_streak_increment(self):
        """Test habit streak increments correctly when completed on consecutive days."""
        user = self._register_and_login_user()
        habit = self._create_habit(user, behavior="Streak increment")

        # Manually set last_completed_date to yesterday and streak to 1
        habit.last_completed_date = datetime.utcnow() - timedelta(days=1)
        habit.streak = 1
        db.session.commit()

        response = self.client.post(url_for('complete_habit', habit_id=habit.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        updated_habit = Habit.query.get(habit.id)
        self.assertEqual(updated_habit.last_completed_date.date(), date.today())
        self.assertEqual(updated_habit.streak, 2)
        self.assertIn(b"Awesome! You completed 'Streak increment'", response.data)

    def test_complete_habit_streak_reset(self):
        """Test habit streak resets if a day is missed."""
        user = self._register_and_login_user()
        habit = self._create_habit(user, behavior="Streak reset")

        # Manually set last_completed_date to two days ago and streak to 5
        habit.last_completed_date = datetime.utcnow() - timedelta(days=2)
        habit.streak = 5
        db.session.commit()

        response = self.client.post(url_for('complete_habit', habit_id=habit.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        updated_habit = Habit.query.get(habit.id)
        self.assertEqual(updated_habit.last_completed_date.date(), date.today())
        self.assertEqual(updated_habit.streak, 1) # Streak should reset to 1
        self.assertIn(b"Awesome! You completed 'Streak reset'", response.data)

    def test_complete_habit_already_completed_today(self):
        """Test completing a habit that was already completed today."""
        user = self._register_and_login_user()
        habit = self._create_habit(user, behavior="Already done")

        # First completion
        self.client.post(url_for('complete_habit', habit_id=habit.id), follow_redirects=True)

        # Attempt second completion on the same day
        response = self.client.post(url_for('complete_habit', habit_id=habit.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        updated_habit = Habit.query.get(habit.id)
        self.assertEqual(updated_habit.streak, 1) # Streak should remain 1
        self.assertIn(b"You've already completed 'Already done' today! Keep up the great work!", response.data)

    def test_complete_habit_other_user_forbidden(self):
        """Test completing a habit belonging to another user is forbidden."""
        user1 = self._register_and_login_user(username="userone", email="userone@example.com")
        habit1 = self._create_habit(user1)

        # Log out user1 by clearing session - simpler than full logout POST for test setup
        with self.client.session_transaction() as sess:
            sess.clear()

        # Register and login user2
        self._register_and_login_user(username="usertwo", email="usertwo@example.com")

        response = self.client.post(url_for('complete_habit', habit_id=habit1.id), follow_redirects=False)
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_complete_nonexistent_habit(self):
        """Test completing a non-existent habit returns 404."""
        self._register_and_login_user()
        response = self.client.post(url_for('complete_habit', habit_id=9999), follow_redirects=False)
        self.assertEqual(response.status_code, 404) # Not Found

if __name__ == '__main__':
    unittest.main()
