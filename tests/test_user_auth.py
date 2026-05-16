import unittest
import os
import sys
import shutil
import tempfile

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from github_downloader.user_auth import UserDatabase

class TestUserAuth(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory/file for the test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_users.db')
        self.user_db = UserDatabase(self.db_path)

    def tearDown(self):
        # Cleanup
        shutil.rmtree(self.test_dir)

    def test_create_user(self):
        success, user_id = self.user_db.create_user('testuser', 'password123')
        self.assertTrue(success)
        self.assertIsNotNone(user_id)

    def test_duplicate_user(self):
        self.user_db.create_user('testuser', 'password123')
        success, _ = self.user_db.create_user('testuser', 'password456')
        self.assertFalse(success)

    def test_authenticate_success(self):
        self.user_db.create_user('testuser', 'password123')
        user_id = self.user_db.authenticate_user('testuser', 'password123')
        self.assertIsNotNone(user_id)

    def test_authenticate_failure(self):
        self.user_db.create_user('testuser', 'password123')
        user_id = self.user_db.authenticate_user('testuser', 'wrongpassword')
        self.assertIsNone(user_id)
        
        user_id = self.user_db.authenticate_user('nonexistent', 'password123')
        self.assertIsNone(user_id)

    def test_github_credentials(self):
        _, user_id = self.user_db.create_user('testuser', 'password123')
        
        self.user_db.save_github_credentials(
            user_id, 'pat', 'ghp_testtoken', 'github_user'
        )
        
        creds = self.user_db.get_github_credentials(user_id)
        self.assertIsNotNone(creds)
        self.assertEqual(creds['access_token'], 'ghp_testtoken')
        self.assertEqual(creds['github_username'], 'github_user')

if __name__ == '__main__':
    unittest.main()
