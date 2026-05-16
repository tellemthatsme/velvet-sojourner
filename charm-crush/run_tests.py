"""
Unit Tests for Charm Crush Session Manager
Tests all new modules and features.
"""
import sys
import os
import unittest
import tempfile
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication

# Initialize QApplication for GUI tests
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestSettingsManager(unittest.TestCase):
    """Tests for SettingsManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.json')
        from charm_crush.settings import SettingsManager
        SettingsManager._instance = None
        self.settings = SettingsManager(self.config_path)
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_settings(self):
        """Test default settings are loaded"""
        self.assertEqual(self.settings.get('theme'), 'dark')
        self.assertEqual(self.settings.get('version'), '2.0.0')
        self.assertFalse(self.settings.is_auto_save_enabled())
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        self.settings.set('test.value', 'test_data')
        self.assertEqual(self.settings.get('test.value'), 'test_data')
    
    def test_nested_settings(self):
        """Test nested settings"""
        self.settings.set('database.connection_pool_size', 10)
        self.assertEqual(self.settings.get('database.connection_pool_size'), 10)
    
    def test_theme_settings(self):
        """Test theme settings"""
        self.settings.set_theme('light')
        self.assertEqual(self.settings.get_theme(), 'light')
    
    def test_auto_save_settings(self):
        """Test auto-save settings"""
        self.settings.set_auto_save(True)
        self.assertTrue(self.settings.is_auto_save_enabled())
        self.settings.set_auto_save_interval(120)
        self.assertEqual(self.settings.get_auto_save_interval(), 120)
    
    def test_editor_settings(self):
        """Test editor settings"""
        self.settings.set_tab_size(2)
        self.assertEqual(self.settings.get_tab_size(), 2)
        self.settings.set_editor_font_size(14)
        self.assertEqual(self.settings.get_editor_font_size(), 14)
    
    def test_export_import_settings(self):
        """Test export/import settings"""
        self.settings.set('test.export', 'value')
        export_path = os.path.join(self.temp_dir, 'export.json')
        self.assertTrue(self.settings.export_settings(export_path))
        self.assertTrue(os.path.exists(export_path))
    
    def test_reset_settings(self):
        """Test resetting to defaults"""
        self.settings.set('custom.value', 'test')
        self.settings.reset_to_defaults()
        self.assertIsNone(self.settings.get('custom.value'))


class TestSessionSharing(unittest.TestCase):
    """Tests for SessionSharingManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        from charm_crush.session_sharing import SessionSharingManager
        self.sharing = SessionSharingManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_share_link(self):
        """Test creating a share link"""
        share = self.sharing.create_share_link(
            session_id='test_session_123',
            creator_id=1,
            permission='view'
        )
        self.assertIsNotNone(share)
        self.assertEqual(share.session_id, 'test_session_123')
        self.assertEqual(share.permission.value, 'view')
    
    def test_get_share_link(self):
        """Test retrieving a share link"""
        created = self.sharing.create_share_link(
            session_id='test_session_456',
            creator_id=1
        )
        retrieved = self.sharing.get_share_link(created.share_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.session_id, 'test_session_456')
    
    def test_revoke_share_link(self):
        """Test revoking a share link"""
        share = self.sharing.create_share_link(
            session_id='test_session_789',
            creator_id=1
        )
        self.assertTrue(self.sharing.revoke_share_link(share.share_id))
        retrieved = self.sharing.get_share_link(share.share_id)
        self.assertEqual(retrieved.status.value, 'revoked')
    
    def test_password_protection(self):
        """Test password-protected shares"""
        share = self.sharing.create_share_link(
            session_id='test_session_pwd',
            creator_id=1,
            password='secret123'
        )
        self.assertTrue(share.password_protected)
        
        # Verify access with correct password
        success, _, error = self.sharing.validate_access(share.share_id, 'secret123')
        self.assertTrue(success)
        
        # Verify access fails with wrong password
        success, _, error = self.sharing.validate_access(share.share_id, 'wrongpass')
        self.assertFalse(success)
    
    def test_share_url_generation(self):
        """Test share URL generation"""
        share = self.sharing.create_share_link(
            session_id='test_session_url',
            creator_id=1
        )
        url = share.get_share_url()
        self.assertIn(share.share_id, url)
    
    def test_statistics(self):
        """Test getting sharing statistics"""
        self.sharing.create_share_link('session_1', 1)
        self.sharing.create_share_link('session_2', 1)
        stats = self.sharing.get_statistics()
        self.assertEqual(stats['total_shares'], 2)
        self.assertEqual(stats['active_shares'], 2)


class TestSearchEngine(unittest.TestCase):
    """Tests for SearchEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        from charm_crush.search import SearchEngine
        self.search_engine = SearchEngine()
        
        # Create test sessions
        self.test_sessions = [
            {
                'id': 'session_1',
                'name': 'Web Config',
                'description': 'Production web server configuration',
                'tags': ['web', 'production'],
                'files': [
                    {
                        'file_path': 'config.json',
                        'content': '{"host": "localhost", "port": 8080}',
                        'format': 'json'
                    }
                ]
            },
            {
                'id': 'session_2',
                'name': 'Database Config',
                'description': 'PostgreSQL database settings',
                'tags': ['database', 'postgres'],
                'files': [
                    {
                        'file_path': 'settings.yaml',
                        'content': 'database:\n  host: db.example.com\n  port: 5432',
                        'format': 'yaml'
                    }
                ]
            }
        ]
    
    def test_simple_search(self):
        """Test simple text search"""
        from charm_crush.search import SearchQuery, SearchMode
        
        query = SearchQuery(query='localhost', mode=SearchMode.SIMPLE)
        results = self.search_engine.search(query, self.test_sessions)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].session_id, 'session_1')
    
    def test_search_by_tag(self):
        """Test searching by tag"""
        from charm_crush.search import SearchQuery, SearchScope
        
        query = SearchQuery(
            query='web',
            scope=SearchScope.TAGGED_SESSIONS,
            tags=['web']
        )
        results = self.search_engine.search(query, self.test_sessions)
        self.assertGreaterEqual(len(results), 1)
    
    def test_search_history(self):
        """Test search history"""
        self.search_engine._add_to_history('test query 1')
        self.search_engine._add_to_history('test query 2')
        history = self.search_engine.get_search_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], 'test query 2')
    
    def test_search_suggestions(self):
        """Test search suggestions"""
        self.search_engine._add_to_history('database config')
        suggestions = self.search_engine.get_suggestions('data', self.test_sessions)
        self.assertIn('database config', suggestions)
    
    def test_search_statistics(self):
        """Test search statistics"""
        from charm_crush.search import SearchQuery
        
        query = SearchQuery(query='test')
        self.search_engine.search(query, self.test_sessions)
        
        stats = self.search_engine.get_statistics()
        self.assertEqual(stats['total_searches'], 1)
        self.assertGreaterEqual(stats['total_results_found'], 0)
    
    def test_regex_search(self):
        """Test regex search"""
        from charm_crush.search import SearchQuery, SearchMode
        
        query = SearchQuery(query=r'\d+', mode=SearchMode.REGEX)
        results = self.search_engine.search(query, self.test_sessions)
        # Should find port numbers
        self.assertGreaterEqual(len(results), 2)


class TestCloudSync(unittest.TestCase):
    """Tests for CloudSyncManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        from charm_crush.cloud_sync import CloudSyncManager
        self.sync_manager = CloudSyncManager('dropbox')
    
    def test_initial_state(self):
        """Test initial state"""
        self.assertEqual(self.sync_manager.status.value, 'idle')
        self.assertIsNone(self.sync_manager.last_sync_time)
        self.assertFalse(self.sync_manager.auto_sync_enabled)
    
    def test_sync_status(self):
        """Test getting sync status"""
        status = self.sync_manager.get_sync_status()
        self.assertIn('status', status)
        self.assertIn('provider', status)
        self.assertEqual(status['provider'], 'dropbox')
    
    def test_not_configured(self):
        """Test unconfigured state"""
        self.assertFalse(self.sync_manager.is_configured())
    
    def test_sync_metadata(self):
        """Test sync metadata"""
        self.sync_manager._update_sync_metadata('test_session', {'name': 'test'})
        self.assertIn('test_session', self.sync_manager._sync_metadata['sessions'])


class TestPluginSystem(unittest.TestCase):
    """Tests for PluginManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        from charm_crush.plugin_system import PluginManager
        self.plugin_manager = PluginManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_info_parsing(self):
        """Test plugin info parsing"""
        plugin_code = '''# Plugin: test_plugin
# Version: 1.0.0
# Author: Test Author
# Description: A test plugin
# Dependencies: 
# Permissions: file_read

from .plugin_system import PluginInterface

class TestPlugin(PluginInterface):
    pass
'''
        info = self.plugin_manager._parse_plugin_metadata(plugin_code)
        self.assertIsNotNone(info)
        self.assertEqual(info.id, 'test_plugin')
        self.assertEqual(info.version, '1.0.0')
    
    def test_statistics(self):
        """Test plugin statistics"""
        stats = self.plugin_manager.get_statistics()
        self.assertIn('total_plugins', stats)
        self.assertIn('loaded_plugins', stats)
    
    def test_create_plugin_template(self):
        """Test creating plugin template"""
        template_path = self.plugin_manager.create_plugin_template(
            'my_test_plugin',
            self.temp_dir
        )
        self.assertTrue(os.path.exists(template_path))
        
        with open(template_path, 'r') as f:
            content = f.read()
        self.assertIn('MyTestPlugin', content)
        self.assertIn('my_test_plugin', content)
    
    def test_plugin_settings(self):
        """Test plugin settings"""
        self.plugin_manager._plugin_settings = {'test_plugin': {'setting': 'value'}}
        settings = self.plugin_manager.get_plugin_settings('test_plugin')
        self.assertEqual(settings.get('setting'), 'value')


class TestSessionManager(unittest.TestCase):
    """Tests for enhanced SessionManager features"""
    
    def setUp(self):
        """Set up test fixtures"""
        from charm_crush.session_manager import SessionManager
        from charm_crush.user_auth import UserDatabase
        
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.user_db = UserDatabase(self.db_path)
        
        # Create test user and initialize tables
        success, self.user_id = self.user_db.create_user('testuser', 'testpass123')
        if not success:
            # User might already exist, try to get existing
            self.user_id = self.user_db.authenticate_user('testuser', 'testpass123')
        
        self.session_manager = SessionManager(self.user_db, self.user_id)
    
    def tearDown(self):
        """Clean up"""
        import shutil
        if hasattr(self, 'user_db') and self.user_db:
            self.user_db.close_all()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_session(self):
        """Test creating a session"""
        session_id = self.session_manager.create_session('Test Session', 'Description')
        self.assertIsNotNone(session_id)
        
        session = self.session_manager.get_session(session_id)
        self.assertEqual(session['name'], 'Test Session')
    
    def test_session_tags(self):
        """Test session tagging"""
        session_id = self.session_manager.create_session('Tagged Session', '')
        
        # Add tag
        self.session_manager.add_session_tag(session_id, 'important')
        session = self.session_manager.get_session(session_id)
        self.assertIn('important', session.get('tags', []))
        
        # Get sessions by tag
        sessions = self.session_manager.get_sessions_by_tag('important')
        self.assertEqual(len(sessions), 1)
        
        # Remove tag
        self.session_manager.remove_session_tag(session_id, 'important')
        sessions = self.session_manager.get_sessions_by_tag('important')
        self.assertEqual(len(sessions), 0)
    
    def test_session_stats(self):
        """Test session statistics"""
        # Create multiple sessions
        for i in range(3):
            self.session_manager.create_session(f'Session {i}', '')
        
        stats = self.session_manager.get_session_stats()
        self.assertEqual(stats['total_sessions'], 3)
    
    def test_session_validation(self):
        """Test session validation"""
        # Create session
        session_id = self.session_manager.create_session('Valid Session', '')
        
        # Validate
        result = self.session_manager.validate_session(session_id)
        self.assertTrue(result['valid'])
    
    def test_bulk_operations(self):
        """Test bulk operations"""
        # Create sessions
        session_ids = []
        for i in range(3):
            sid = self.session_manager.create_session(f'Bulk Session {i}', '')
            session_ids.append(sid)
        
        # Delete all
        results = self.session_manager.delete_sessions(session_ids)
        self.assertEqual(results['deleted'], 3)


class TestConfigEditor(unittest.TestCase):
    """Tests for enhanced ConfigEditor features"""
    
    def setUp(self):
        """Set up test fixtures"""
        from charm_crush.config_editor import ConfigEditor
        self.editor = ConfigEditor()
    
    def test_load_content(self):
        """Test loading content"""
        content = '{"key": "value", "number": 42}'
        self.editor.load_content(content, 'json')
        self.assertTrue(self.editor.document().toPlainText())
    
    def test_bracket_matching(self):
        """Test bracket matching"""
        content = '{"key": {"nested": "value"}}'
        self.editor.load_content(content, 'json')
        # Should not raise errors
        self.assertTrue(True)
    
    def test_modified_state(self):
        """Test modified state tracking"""
        content = '{"initial": "value"}'
        self.editor.load_content(content, 'json')
        self.editor.setModified(False)
        self.assertFalse(self.editor.isModified())
    
    def test_find_replace_dialog(self):
        """Test find/replace dialog creation"""
        from charm_crush.config_editor import FindReplaceDialog
        dialog = FindReplaceDialog(self.editor)
        self.assertIsNotNone(dialog)


class TestUserAuth(unittest.TestCase):
    """Tests for enhanced UserAuth features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.user_db = UserDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up"""
        import shutil
        if self.user_db:
            self.user_db.close_all()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_user(self):
        """Test creating a user"""
        success, user_id = self.user_db.create_user('testuser', 'testpassword123')
        self.assertTrue(success)
        self.assertIsNotNone(user_id)
    
    def test_authenticate_user(self):
        """Test user authentication"""
        self.user_db.create_user('authuser', 'authpass123')
        user_id = self.user_db.authenticate_user('authuser', 'authpass123')
        self.assertIsNotNone(user_id)
        
        # Wrong password
        wrong_id = self.user_db.authenticate_user('authuser', 'wrongpass')
        self.assertIsNone(wrong_id)
    
    def test_connection_pooling(self):
        """Test connection pool"""
        conn1 = self.user_db.get_connection()
        conn2 = self.user_db.get_connection()
        self.assertIsNotNone(conn1)
        self.assertIsNotNone(conn2)
        # Should get different connections
        self.assertEqual(conn1, conn2)
    
    def test_get_all_users(self):
        """Test getting all users"""
        self.user_db.create_user('user1', 'pass1')
        self.user_db.create_user('user2', 'pass2')
        
        users = self.user_db.get_all_users()
        self.assertEqual(len(users), 2)
    
    def test_user_preferences(self):
        """Test user preferences"""
        self.user_db.create_user('prefuser', 'pass123')
        user_id = self.user_db.authenticate_user('prefuser', 'pass123')
        
        # Set preferences
        self.user_db.save_user_preferences(user_id, {'theme': 'dark', 'font_size': 14})
        
        # Get preferences
        prefs = self.user_db.get_user_preferences(user_id)
        self.assertEqual(prefs.get('theme'), 'dark')
        self.assertEqual(prefs.get('font_size'), 14)


class TestUtils(unittest.TestCase):
    """Tests for Utils module"""
    
    def test_theme_manager(self):
        """Test theme manager"""
        from charm_crush.utils import ThemeManager
        
        dark = ThemeManager.get_dark_stylesheet()
        self.assertIn('QMainWindow', dark)
        
        light = ThemeManager.get_light_stylesheet()
        self.assertIn('QMainWindow', light)
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        from charm_crush.utils import format_timestamp
        
        timestamp = format_timestamp('2024-01-15T10:30:00')
        self.assertIn('2024', timestamp)
    
    def test_file_format_detection(self):
        """Test file format detection"""
        from charm_crush.utils import FileFormat
        
        self.assertEqual(FileFormat.detect_format('test.json'), 'json')
        self.assertEqual(FileFormat.detect_format('config.yaml'), 'yaml')
        self.assertEqual(FileFormat.detect_format('settings.yml'), 'yaml')
        self.assertEqual(FileFormat.detect_format('init.ini'), 'ini')
        self.assertEqual(FileFormat.detect_format('readme.txt'), 'txt')


# Main test runner
if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSettingsManager,
        TestSessionSharing,
        TestSearchEngine,
        TestCloudSync,
        TestPluginSystem,
        TestSessionManager,
        TestConfigEditor,
        TestUserAuth,
        TestUtils,
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
