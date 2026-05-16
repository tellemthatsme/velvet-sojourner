"""
Settings Manager for Charm Crush
Handles application configuration and user preferences
"""
import json
import os
from typing import Any, Dict, Optional


class SettingsManager:
    """Manages application settings and user preferences with persistent storage"""
    
    _instance = None
    
    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = config_path
        else:
            app_data = os.environ.get('APPDATA', os.environ.get('HOME', os.path.expanduser('~')))
            self.config_path = os.path.join(app_data, 'CharmCrush', 'config.json')
            
        self.settings = self._get_default_settings()
        self.load_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Returns the default settings"""
        return {
            'theme': 'dark',
            'version': '2.0.0',
            'auto_save': {
                'enabled': False,
                'interval': 60
            },
            'editor': {
                'font_size': 11,
                'tab_size': 4,
                'show_line_numbers': True,
                'word_wrap': False,
                'highlight_current_line': True,
                'bracket_matching': True,
                'syntax_highlighting': True
            },
            'database': {
                'connection_pool_size': 5
            },
            'settings': {
                'recent_sessions_limit': 10,
                'remember_last_session': True,
                'check_updates': True,
                'use_spaces': True
            },
            'cloud_sync': {
                'enabled': False,
                'provider': 'dropbox',
                'auto_sync': False,
                'sync_interval': 300
            },
            'sharing': {
                'allowed': True,
                'default_permission': 'read'
            }
        }
    
    def load_settings(self):
        """Loads settings from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_settings = json.load(f)
                    self.settings.update(file_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Saves current settings to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'editor.font_size')"""
        parts = key.split('.')
        val = self.settings
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return default
        return val
        
    def set(self, key: str, value: Any):
        """Set a setting value using dot notation"""
        parts = key.split('.')
        ref = self.settings
        for part in parts[:-1]:
            if part not in ref:
                ref[part] = {}
            ref = ref[part]
        ref[parts[-1]] = value
        self.save_settings()

    def get_theme(self) -> str:
        return self.get('theme', 'dark')
        
    def set_theme(self, theme: str):
        self.set('theme', theme)
        
    def is_auto_save_enabled(self) -> bool:
        return self.get('auto_save.enabled', False)
        
    def set_auto_save(self, enabled: bool):
        self.set('auto_save.enabled', enabled)
        
    def get_auto_save_interval(self) -> int:
        return self.get('auto_save.interval', 60)
        
    def set_auto_save_interval(self, interval: int):
        self.set('auto_save.interval', interval)
        
    def get_tab_size(self) -> int:
        return self.get('editor.tab_size', 4)
        
    def set_tab_size(self, size: int):
        self.set('editor.tab_size', size)
        
    def get_editor_font_size(self) -> int:
        return self.get('editor.font_size', 11)
        
    def set_editor_font_size(self, size: int):
        self.set('editor.font_size', size)
        
    def export_settings(self, file_path: str) -> bool:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
            
    def reset_to_defaults(self):
        self.settings = self._get_default_settings()
        self.save_settings()

    # --- Recent sessions ---
    def get_recent_sessions_limit(self) -> int:
        return self.get('settings.recent_sessions_limit', 10)

    def set_recent_sessions_limit(self, limit: int):
        self.set('settings.recent_sessions_limit', limit)

    # --- Editor flags ---
    def is_line_numbers_enabled(self) -> bool:
        return self.get('editor.show_line_numbers', True)

    def set_line_numbers(self, enabled: bool):
        self.set('editor.show_line_numbers', enabled)

    def is_word_wrap_enabled(self) -> bool:
        return self.get('editor.word_wrap', False)

    def set_word_wrap(self, enabled: bool):
        self.set('editor.word_wrap', enabled)

    def is_highlight_current_line(self) -> bool:
        return self.get('editor.highlight_current_line', True)

    def set_highlight_current_line(self, enabled: bool):
        self.set('editor.highlight_current_line', enabled)

    def is_bracket_matching(self) -> bool:
        return self.get('editor.bracket_matching', True)

    def set_bracket_matching(self, enabled: bool):
        self.set('editor.bracket_matching', enabled)

    def is_syntax_highlighting(self) -> bool:
        return self.get('editor.syntax_highlighting', True)

    def set_syntax_highlighting(self, enabled: bool):
        self.set('editor.syntax_highlighting', enabled)

    # --- Cloud sync ---
    def is_cloud_sync_enabled(self) -> bool:
        return self.get('cloud_sync.enabled', False)

    def set_cloud_sync(self, enabled: bool):
        self.set('cloud_sync.enabled', enabled)

    def get_cloud_provider(self) -> str:
        return self.get('cloud_sync.provider', 'dropbox')

    def set_cloud_provider(self, provider: str):
        self.set('cloud_sync.provider', provider)

    # --- Sharing ---
    def is_sharing_allowed(self) -> bool:
        return self.get('sharing.allowed', True)

    def set_sharing_allowed(self, allowed: bool):
        self.set('sharing.allowed', allowed)
