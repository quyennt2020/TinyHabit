import unittest
from flask import url_for, session
from app import app, db
from app.models import User
from tests.test_basic import BasicTests

class TestAuthRoutes(BasicTests):

    def _register_user(self, username, email, password, password2=None):
        """Helper method to register a user via POST request."""
        if password2 is None:
            password2 = password
        return self.client.post(
            url_for('register'),
            data=dict(username=username, email=email, password=password, password2=password2),
            follow_redirects=True  # Makes it easier to check final page content and flashed messages
        )

    def _login_user(self, email, password):
        """Helper method to log in a user via POST request."""
        return self.client.post(
            url_for('login'),
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    # Registration Tests
    def test_get_register_page(self):
        """Test GET request to the registration page."""
        response = self.client.get(url_for('register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Register", response.data)
        self.assertIn(b"Username", response.data)
        self.assertIn(b"Email", response.data)
        self.assertIn(b"Password", response.data)

    def test_successful_registration(self):
        """Test successful user registration."""
        response = self._register_user('newuser', 'new@example.com', 'password123')
        self.assertEqual(response.status_code, 200) # After redirect to login
        self.assertIn(b"Sign In", response.data) # Should be on login page
        self.assertIn(b"Congratulations, you are now a registered user!", response.data) # Flashed message

        user = User.query.filter_by(email='new@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')

    def test_registration_existing_username(self):
        """Test registration with an existing username."""
        self._register_user('existinguser', 'first@example.com', 'password123') # First user
        response = self._register_user('existinguser', 'second@example.com', 'password456') # Attempt second

        self.assertEqual(response.status_code, 200) # Should re-render register form
        self.assertIn(b"Register", response.data) # Still on register page
        self.assertIn(b"Please use a different username.", response.data) # Error message

    def test_registration_existing_email(self):
        """Test registration with an existing email."""
        self._register_user('anotheruser', 'existing@example.com', 'password123') # First user
        response = self._register_user('yetanother', 'existing@example.com', 'password456') # Attempt second

        self.assertEqual(response.status_code, 200) # Should re-render register form
        self.assertIn(b"Register", response.data) # Still on register page
        self.assertIn(b"Please use a different email address.", response.data) # Error message

    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        response = self.client.post(
            url_for('register'),
            data=dict(username='testuser', email='test@example.com', password='password1', password2='password2'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Re-renders form
        self.assertIn(b"Register", response.data)
        self.assertIn(b"Field must be equal to password.", response.data) # WTForms default error

    # Login Tests
    def test_get_login_page(self):
        """Test GET request to the login page."""
        response = self.client.get(url_for('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign In", response.data) # Changed from "Log In" to match template
        self.assertIn(b"Email", response.data)
        self.assertIn(b"Password", response.data)

    def test_successful_login(self):
        """Test successful user login."""
        self._register_user('loginuser', 'login@example.com', 'password123')
        response = self._login_user('login@example.com', 'password123')

        self.assertEqual(response.status_code, 200) # After redirect to dashboard
        self.assertIn(b"Dashboard", response.data) # Should be on dashboard page
        self.assertIn(b"Hi, loginuser", response.data) # current_user.username displayed

        with self.client.session_transaction() as sess:
            self.assertTrue(sess.get('_user_id') is not None)

    def test_login_nonexistent_user(self):
        """Test login with a non-existent email."""
        response = self._login_user('notauser@example.com', 'fakepassword')
        self.assertEqual(response.status_code, 200) # Re-renders login form
        self.assertIn(b"Sign In", response.data)
        self.assertIn(b"Invalid email or password", response.data) # Flashed error

    def test_login_wrong_password(self):
        """Test login with correct email but wrong password."""
        self._register_user('userpass', 'userpass@example.com', 'correctpassword')
        response = self._login_user('userpass@example.com', 'wrongpassword')

        self.assertEqual(response.status_code, 200) # Re-renders login form
        self.assertIn(b"Sign In", response.data)
        self.assertIn(b"Invalid email or password", response.data) # Flashed error

    def test_login_redirects_to_next_page(self):
        """Test login redirects to the 'next' page parameter if provided."""
        self._register_user('nextuser', 'next@example.com', 'password123')

        # Target URL for 'next'
        target_url = url_for('add_habit')

        login_response = self.client.post(
            url_for('login', next=target_url), # Pass 'next' as query param
            data=dict(email='next@example.com', password='password123'),
            follow_redirects=False # We want to check the 302 redirect location
        )
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.location, target_url)

        # To be absolutely sure, follow the redirect and check the page
        final_response = self.client.get(login_response.location, follow_redirects=True)
        self.assertEqual(final_response.status_code, 200)
        self.assertIn(b"Add New Habit", final_response.data)


    # Logout Test
    def test_logout(self):
        """Test user logout."""
        # Register and login user
        self._register_user('logoutuser', 'logout@example.com', 'password123')
        self._login_user('logout@example.com', 'password123')

        # Check we are logged in by accessing dashboard
        dashboard_response = self.client.get(url_for('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn(b"Hi, logoutuser", dashboard_response.data)

        # Perform logout
        logout_response = self.client.get(url_for('logout'), follow_redirects=True)
        self.assertEqual(logout_response.status_code, 200) # Redirects to index
        # The index redirects to login if not authenticated
        # So we should end up on the login page.
        self.assertIn(b"Sign In", logout_response.data)
        # Check for logout message (if any - current app doesn't flash on logout)
        # self.assertIn(b"You have been logged out.", logout_response.data)


        # Verify logout by trying to access a protected route
        dashboard_again_response = self.client.get(url_for('dashboard'), follow_redirects=False)
        self.assertEqual(dashboard_again_response.status_code, 302) # Should redirect to login
        self.assertTrue(dashboard_again_response.location.startswith(url_for('login')))

        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('_user_id'))


if __name__ == '__main__':
    unittest.main()
