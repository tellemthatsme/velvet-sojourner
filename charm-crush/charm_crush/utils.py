"""
Utility functions for Charm Crush Session Manager
Handles file format detection, parsing, encryption helpers, and theming.
"""
import os
import json
import configparser
import uuid
import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
import yaml


class FileFormat:
    """Supported file formats"""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    TXT = "txt"
    
    @classmethod
    def detect_format(cls, file_path: str) -> str:
        """Detect file format from extension"""
        ext = Path(file_path).suffix.lower()
        format_map = {
            ".json": cls.JSON,
            ".yaml": cls.YAML,
            ".yml": cls.YAML,
            ".ini": cls.INI,
            ".txt": cls.TXT,
        }
        return format_map.get(ext, cls.TXT)
    
    @classmethod
    def get_extensions(cls) -> List[str]:
        """Get list of supported extensions"""
        return [".json", ".yaml", ".yml", ".ini", ".txt"]


class FileParser:
    """Parser for different config file formats"""
    
    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, Any]:
        """
        Parse a config file and return (content_type, content)
        """
        format_type = FileFormat.detect_format(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if format_type == FileFormat.JSON:
            data = json.loads(content)
            return format_type, data
        
        elif format_type == FileFormat.YAML:
            data = yaml.safe_load(content)
            return format_type, data
        
        elif format_type == FileFormat.INI:
            config = configparser.ConfigParser()
            config.read_string(content)
            # Convert to nested dict
            data = {section: dict(config[section]) for section in config.sections()}
            return format_type, data
        
        else:  # TXT
            return format_type, content
    
    @staticmethod
    def format_content(content: Any, format_type: str) -> str:
        """Format content as string for the given format type"""
        if format_type == FileFormat.JSON:
            return json.dumps(content, indent=4, ensure_ascii=False)
        
        elif format_type == FileFormat.YAML:
            return yaml.dump(content, default_flow_style=False, allow_unicode=True)
        
        elif format_type == FileFormat.INI:
            if isinstance(content, dict):
                config = configparser.ConfigParser()
                for section, values in content.items():
                    config[section] = values
                output = io.StringIO()
                config.write(output)
                return output.getvalue()
            return content
        
        else:  # TXT
            return str(content) if not isinstance(content, str) else content


class EncryptionHelper:
    """Helper for encryption operations"""
    
    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key = Fernet.generate_key()
        self.fernet = Fernet(key)
        self.key = key
    
    @classmethod
    def create_with_key_file(cls, key_file: str) -> 'EncryptionHelper':
        """Create encryption helper with key from file"""
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)
        return cls(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt bytes data"""
        return self.fernet.encrypt(data)
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """Decrypt bytes data"""
        return self.fernet.decrypt(encrypted_data)


class ThemeManager:
    """Manages application theming"""
    
    # Predefined themes
    THEMES = {
        'dark': {
            "background": "#1e1e1e",
            "foreground": "#d4d4d4",
            "accent": "#007acc",
            "panel": "#252526",
            "border": "#3c3c3c",
            "text": "#d4d4d4",
            "highlight": "#2d2d30",
            "success": "#4ec9b0",
            "warning": "#ce9178",
            "error": "#f14c4c",
            "tree_background": "#1e1e1e",
            "tree_foreground": "#d4d4d4",
            "tree_selection": "#094771",
            "tab_background": "#252526",
            "tab_selected": "#1e1e1e",
        },
        'light': {
            "background": "#ffffff",
            "foreground": "#333333",
            "accent": "#2196f3",
            "panel": "#f5f5f5",
            "border": "#dddddd",
            "text": "#333333",
            "highlight": "#e0e0e0",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "tree_background": "#ffffff",
            "tree_foreground": "#333333",
            "tree_selection": "#bbdefb",
            "tab_background": "#f5f5f5",
            "tab_selected": "#ffffff",
        },
        'blue': {
            "background": "#1a2a3a",
            "foreground": "#e0e0e0",
            "accent": "#4a90d9",
            "panel": "#243447",
            "border": "#3a4a5a",
            "text": "#e0e0e0",
            "highlight": "#2a3a4a",
            "success": "#5cb85c",
            "warning": "#f0ad4e",
            "error": "#d9534f",
            "tree_background": "#1a2a3a",
            "tree_foreground": "#e0e0e0",
            "tree_selection": "#4a90d9",
            "tab_background": "#243447",
            "tab_selected": "#1a2a3a",
        },
        'green': {
            "background": "#1a2a1a",
            "foreground": "#e0e0e0",
            "accent": "#4caf50",
            "panel": "#243424",
            "border": "#3a4a3a",
            "text": "#e0e0e0",
            "highlight": "#2a3a2a",
            "success": "#66bb6a",
            "warning": "#ff9800",
            "error": "#ef5350",
            "tree_background": "#1a2a1a",
            "tree_foreground": "#e0e0e0",
            "tree_selection": "#4caf50",
            "tab_background": "#243424",
            "tab_selected": "#1a2a1a",
        },
        'purple': {
            "background": "#2a1a2a",
            "foreground": "#e0e0e0",
            "accent": "#9c27b0",
            "panel": "#3a2a3a",
            "border": "#4a3a4a",
            "text": "#e0e0e0",
            "highlight": "#3a2a3a",
            "success": "#8bc34a",
            "warning": "#ffc107",
            "error": "#f44336",
            "tree_background": "#2a1a2a",
            "tree_foreground": "#e0e0e0",
            "tree_selection": "#9c27b0",
            "tab_background": "#3a2a3a",
            "tab_selected": "#2a1a2a",
        },
    }
    
    @classmethod
    def get_theme_names(cls) -> List[str]:
        """Get list of available theme names"""
        return list(cls.THEMES.keys())
    
    @classmethod
    def get_theme(cls, theme_name: str) -> Dict[str, str]:
        """Get theme colors by name"""
        return cls.THEMES.get(theme_name, cls.THEMES['dark'])
    
    @classmethod
    def get_stylesheet(cls, theme_name: str) -> str:
        """Get stylesheet for a specific theme"""
        theme = cls.get_theme(theme_name)
        return cls._build_stylesheet(theme)
    
    @classmethod
    def _build_stylesheet(cls, t: Dict[str, str]) -> str:
        """Build stylesheet from theme dictionary"""
        return f"""
        QMainWindow {{
            background-color: {t['background']};
            color: {t['foreground']};
        }}
        
        QWidget {{
            background-color: {t['background']};
            color: {t['foreground']};
            font-family: 'Segoe UI', sans-serif;
            font-size: 10pt;
        }}
        
        QMenuBar {{
            background-color: {t['panel']};
            color: {t['foreground']};
            border-bottom: 1px solid {t['border']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {t['accent']};
        }}
        
        QMenu {{
            background-color: {t['panel']};
            color: {t['foreground']};
            border: 1px solid {t['border']};
        }}
        
        QMenu::item:selected {{
            background-color: {t['accent']};
        }}
        
        QToolBar {{
            background-color: {t['panel']};
            border-bottom: 1px solid {t['border']};
            spacing: 5px;
            padding: 5px;
        }}
        
        QTreeWidget {{
            background-color: {t['tree_background']};
            color: {t['tree_foreground']};
            border: 1px solid {t['border']};
            outline: none;
        }}
        
        QTreeWidget::item:selected {{
            background-color: {t['tree_selection']};
            color: {t['foreground']};
        }}
        
        QTreeWidget::item:hover {{
            background-color: {t['highlight']};
        }}
        
        QTabWidget::pane {{
            background-color: {t['background']};
            border: 1px solid {t['border']};
        }}
        
        QTabBar::tab {{
            background-color: {t['tab_background']};
            color: {t['foreground']};
            padding: 8px 15px;
            border: 1px solid {t['border']};
            border-bottom: none;
        }}
        
        QTabBar::tab:selected {{
            background-color: {t['tab_selected']};
            border-bottom: 2px solid {t['accent']};
        }}
        
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {t['panel']};
            color: {t['foreground']};
            border: 1px solid {t['border']};
            padding: 5px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {t['accent']};
        }}
        
        QPushButton {{
            background-color: {t['panel']};
            color: {t['foreground']};
            border: 1px solid {t['border']};
            padding: 6px 15px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: {t['highlight']};
            border-color: {t['accent']};
        }}
        
        QPushButton:pressed {{
            background-color: {t['accent']};
        }}
        
        QComboBox {{
            background-color: {t['panel']};
            color: {t['foreground']};
            border: 1px solid {t['border']};
            padding: 5px 10px;
            border-radius: 4px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QStatusBar {{
            background-color: {t['panel']};
            color: {t['foreground']};
            border-top: 1px solid {t['border']};
        }}
        
        QGroupBox {{
            border: 1px solid {t['border']};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        
        QProgressBar {{
            background-color: {t['panel']};
            border: 1px solid {t['border']};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {t['accent']};
            border-radius: 4px;
        }}
        
        QSplitter::handle {{
            background-color: {t['border']};
        }}
        
        QScrollBar:vertical {{
            background-color: {t['background']};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {t['panel']};
            min-height: 20px;
            border-radius: 6px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {t['accent']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {t['background']};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {t['panel']};
            min-width: 20px;
            border-radius: 6px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {t['accent']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
    
    @classmethod
    def get_dark_stylesheet(cls) -> str:
        """Get dark theme stylesheet for PyQt6 (backward compatibility)"""
        return cls.get_stylesheet('dark')


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp
