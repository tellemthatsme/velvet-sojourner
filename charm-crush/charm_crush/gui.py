"""
Main GUI Application for Charm Crush Session Manager
Built with PyQt6 with dark theme support.
"""
import sys
import os
import json
import threading
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QTreeWidget, QTreeWidgetItem, QTabWidget, QFormLayout,
                              QGroupBox, QComboBox, QCheckBox, QSpinBox, QFileDialog,
                              QMessageBox, QStatusBar, QToolBar, QMenuBar, QMenu,
                              QDialog, QDialogButtonBox, QListWidget, QListWidgetItem,
                              QSplitter, QFrame, QScrollArea, QTextEdit, QInputDialog,
                              QProgressDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap, QColor, QPalette, QKeySequence, QShortcut

from .user_auth import UserDatabase
from .session_manager import SessionManager
from .config_editor import ConfigEditor, FindReplaceDialog
from .utils import ThemeManager, format_timestamp
from .settings import SettingsManager


class LoginDialog(QDialog):
    """Login/Register dialog"""
    
    def __init__(self, user_auth, parent=None):
        super().__init__(parent)
        self.user_auth = user_auth
        self.authenticated_user_id = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Charm Crush - Login")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Charm Crush Session Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Login tab
        login_tab = QWidget()
        login_layout = QFormLayout()
        
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_layout.addRow("Username:", self.login_username)
        login_layout.addRow("Password:", self.login_password)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.do_login)
        login_layout.addRow("", self.login_btn)
        
        login_tab.setLayout(login_layout)
        self.tabs.addTab(login_tab, "Login")
        
        # Register tab
        register_tab = QWidget()
        register_layout = QFormLayout()
        
        self.reg_username = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_confirm_password = QLineEdit()
        self.reg_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        register_layout.addRow("Username:", self.reg_username)
        register_layout.addRow("Password:", self.reg_password)
        register_layout.addRow("Confirm Password:", self.reg_confirm_password)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.do_register)
        register_layout.addRow("", self.register_btn)
        
        register_tab.setLayout(register_layout)
        self.tabs.addTab(register_tab, "Register")
        
        layout.addWidget(self.tabs)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def do_login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        
        if not username or not password:
            self.status_label.setText("Please enter username and password")
            return
        
        user_id = self.user_auth.authenticate_user(username, password)
        if user_id:
            self.authenticated_user_id = user_id
            self.accept()
        else:
            self.status_label.setText("Invalid credentials or account not found")
    
    def do_register(self):
        username = self.reg_username.text()
        password = self.reg_password.text()
        confirm = self.reg_confirm_password.text()
        
        if not username or not password:
            self.status_label.setText("Please fill in all fields")
            return
        
        if password != confirm:
            self.status_label.setText("Passwords do not match")
            return
        
        if len(password) < 8:
            self.status_label.setText("Password must be at least 8 characters")
            return
        
        success, user_id = self.user_auth.create_user(username, password)
        if success:
            self.status_label.setText("Registration successful! Please login.")
            self.tabs.setCurrentIndex(0)
        else:
            self.status_label.setText("Username already exists")


class NewSessionDialog(QDialog):
    """Dialog for creating a new session"""
    
    def __init__(self, templates=None, parent=None):
        super().__init__(parent)
        self.session_name = None
        self.session_description = ""
        self.session_template = None
        self.templates = templates or []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("New Session")
        self.setMinimumSize(450, 250)
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter session name")
        layout.addRow("Name:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addRow("Description:", self.description_input)
        
        # Template selection
        if self.templates:
            self.template_combo = QComboBox()
            self.template_combo.addItem("Empty Session", "empty")
            for template in self.templates:
                self.template_combo.addItem(template.replace('_', ' ').title(), template)
            layout.addRow("Template:", self.template_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow("", button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        self.session_name = self.name_input.text().strip()
        if not self.session_name:
            QMessageBox.warning(self, "Error", "Please enter a session name")
            return
        
        self.session_description = self.description_input.toPlainText().strip()
        
        if hasattr(self, 'template_combo'):
            self.session_template = self.template_combo.currentData()
        
        super().accept()


class RenameSessionDialog(QDialog):
    """Dialog for renaming a session"""
    
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.new_name = None
        self.init_ui(current_name)
    
    def init_ui(self, current_name):
        self.setWindowTitle("Rename Session")
        self.setFixedSize(400, 120)
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setText(current_name)
        layout.addRow("New Name:", self.name_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow("", button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        self.new_name = self.name_input.text().strip()
        if not self.new_name:
            QMessageBox.warning(self, "Error", "Please enter a session name")
            return
        
        super().accept()


class BatchOperationsDialog(QDialog):
    """Dialog for batch session operations"""
    
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self._operation = None
        self._selected_sessions = []
        self._tag = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Batch Session Operations")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Operation selection
        op_group = QGroupBox("Operation")
        op_layout = QHBoxLayout()
        
        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["Delete Sessions", "Export Sessions", "Add Tag", "Remove Tag"])
        op_layout.addWidget(self.operation_combo)
        
        op_group.setLayout(op_layout)
        layout.addWidget(op_group)
        
        # Tag input (for add/remove tag operations)
        self.tag_group = QGroupBox("Tag")
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter tag name...")
        tag_layout = QVBoxLayout()
        tag_layout.addWidget(self.tag_input)
        self.tag_group.setLayout(tag_layout)
        self.tag_group.setVisible(False)
        layout.addWidget(self.tag_group)
        
        self.operation_combo.currentIndexChanged.connect(self.on_operation_changed)
        
        # Session selection
        select_group = QGroupBox("Select Sessions")
        select_layout = QVBoxLayout()
        
        self.session_list = QListWidget()
        self.session_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        sessions = self.session_manager.get_all_sessions()
        for session in sessions:
            item = QListWidgetItem(session['name'])
            item.setData(Qt.ItemDataRole.UserRole, session['id'])
            self.session_list.addItem(item)
        
        select_layout.addWidget(self.session_list)
        
        # Select buttons
        select_btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.session_list.selectAll)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.session_list.clearSelection)
        select_btn_layout.addWidget(select_all_btn)
        select_btn_layout.addWidget(deselect_all_btn)
        select_layout.addLayout(select_btn_layout)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def on_operation_changed(self, index):
        """Show/hide tag input based on operation."""
        self.tag_group.setVisible(index in [2, 3])  # Add Tag or Remove Tag
    
    def accept(self):
        self._selected_sessions = []
        for item in self.session_list.selectedItems():
            self._selected_sessions.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not self._selected_sessions:
            QMessageBox.warning(self, "Error", "Please select at least one session")
            return
        
        operation_map = {
            0: 'delete',
            1: 'export',
            2: 'add_tag',
            3: 'remove_tag'
        }
        self._operation = operation_map.get(self.operation_combo.currentIndex(), 'delete')
        
        if self._operation in ('add_tag', 'remove_tag'):
            self._tag = self.tag_input.text().strip()
            if not self._tag:
                QMessageBox.warning(self, "Error", "Please enter a tag name")
                return
        
        super().accept()
    
    def get_operation(self):
        return self._operation
    
    def get_selected_sessions(self):
        return self._selected_sessions
    
    def get_tag(self):
        return self._tag


class SessionStatsDialog(QDialog):
    """Dialog showing session statistics"""
    
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Session Statistics")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        stats = self.session_manager.get_session_stats()
        
        # Create stats display
        stats_text = f"""
        <h2>Session Statistics</h2>
        
        <p><b>Total Sessions:</b> {stats['total_sessions']}</p>
        <p><b>Total Files:</b> {stats['total_files']}</p>
        <p><b>Total Size:</b> {stats['total_size_human']}</p>
        <p><b>Average Files per Session:</b> {stats['average_files_per_session']:.1f}</p>
        
        <h3>Activity (Last 30 Days)</h3>
        <p><b>Recent Sessions:</b> {self.session_manager.get_user_activity_stats(30)['recent_sessions']}</p>
        
        <h3>Tags</h3>
        <p><b>Unique Tags:</b> {len(self.session_manager.get_all_tags())}</p>
        """
        
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        layout.addWidget(stats_label)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager()
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        self.setWindowTitle("Settings - Charm Crush")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Tabs for settings categories
        self.tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        self.tabs.addTab(general_tab, "General")
        
        # Editor tab
        editor_tab = self.create_editor_tab()
        self.tabs.addTab(editor_tab, "Editor")
        
        # Cloud tab
        cloud_tab = self.create_cloud_tab()
        self.tabs.addTab(cloud_tab, "Cloud Sync")
        
        # Sharing tab
        sharing_tab = self.create_sharing_tab()
        self.tabs.addTab(sharing_tab, "Sharing")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self.reset_settings)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Theme selection
        from .utils import ThemeManager
        self.theme_combo = QComboBox()
        theme_names = ThemeManager.get_theme_names()
        theme_display_names = [name.title() for name in theme_names]
        self.theme_combo.addItems(theme_display_names)
        layout.addRow("Theme:", self.theme_combo)
        
        # Custom accent color
        self.accent_color_btn = QPushButton("Choose Accent Color")
        self.accent_color_btn.setMaximumWidth(150)
        layout.addRow("Custom accent:", self.accent_color_btn)
        
        # Auto-save
        self.auto_save_check = QCheckBox("Enable auto-save")
        layout.addRow("", self.auto_save_check)
        
        # Auto-save interval
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(30, 600)
        self.auto_save_interval.setSuffix(" seconds")
        layout.addRow("Auto-save interval:", self.auto_save_interval)
        
        # Recent sessions limit
        self.recent_limit = QSpinBox()
        self.recent_limit.setRange(5, 50)
        layout.addRow("Recent sessions limit:", self.recent_limit)
        
        # Remember last session
        self.remember_last_check = QCheckBox("Remember last session on startup")
        layout.addRow("", self.remember_last_check)
        
        # Check for updates
        self.check_updates_check = QCheckBox("Check for updates on startup")
        layout.addRow("", self.check_updates_check)
        
        tab.setLayout(layout)
        return tab
    
    def create_editor_tab(self) -> QWidget:
        """Create editor settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        layout.addRow("Font size:", self.font_size)
        
        # Tab size
        self.tab_size = QSpinBox()
        self.tab_size.setRange(2, 8)
        layout.addRow("Tab size:", self.tab_size)
        
        # Use spaces instead of tabs
        self.use_spaces_check = QCheckBox("Use spaces instead of tabs")
        layout.addRow("", self.use_spaces_check)
        
        # Line numbers
        self.line_numbers_check = QCheckBox("Show line numbers")
        layout.addRow("", self.line_numbers_check)
        
        # Word wrap
        self.word_wrap_check = QCheckBox("Enable word wrap")
        layout.addRow("", self.word_wrap_check)
        
        # Highlight current line
        self.highlight_line_check = QCheckBox("Highlight current line")
        layout.addRow("", self.highlight_line_check)
        
        # Bracket matching
        self.bracket_matching_check = QCheckBox("Enable bracket matching")
        layout.addRow("", self.bracket_matching_check)
        
        # Syntax highlighting
        self.syntax_highlighting_check = QCheckBox("Enable syntax highlighting")
        layout.addRow("", self.syntax_highlighting_check)
        
        tab.setLayout(layout)
        return tab
    
    def create_cloud_tab(self) -> QWidget:
        """Create cloud sync settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Enable cloud sync
        self.cloud_sync_check = QCheckBox("Enable cloud synchronization")
        layout.addRow("", self.cloud_sync_check)
        
        # Cloud provider
        self.cloud_provider_combo = QComboBox()
        self.cloud_provider_combo.addItems(["Dropbox", "Google Drive", "OneDrive"])
        layout.addRow("Cloud provider:", self.cloud_provider_combo)
        
        # Auto-sync
        self.auto_sync_check = QCheckBox("Auto-sync changes")
        layout.addRow("", self.auto_sync_check)
        
        # Sync interval
        self.sync_interval = QSpinBox()
        self.sync_interval.setRange(60, 3600)
        self.sync_interval.setSuffix(" seconds")
        layout.addRow("Sync interval:", self.sync_interval)
        
        tab.setLayout(layout)
        return tab
    
    def create_sharing_tab(self) -> QWidget:
        """Create sharing settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Allow sharing
        self.sharing_allowed_check = QCheckBox("Allow session sharing")
        layout.addRow("", self.sharing_allowed_check)
        
        # Default permission
        self.default_permission_combo = QComboBox()
        self.default_permission_combo.addItems(["Read Only", "Read/Write", "Admin"])
        layout.addRow("Default permission:", self.default_permission_combo)
        
        tab.setLayout(layout)
        return tab
    
    def load_current_settings(self):
        """Load current settings into dialog"""
        # General settings
        from .utils import ThemeManager
        theme = self.settings.get_theme()
        theme_names = ThemeManager.get_theme_names()
        if theme in theme_names:
            self.theme_combo.setCurrentText(theme.title())
        
        self.auto_save_check.setChecked(self.settings.is_auto_save_enabled())
        self.auto_save_interval.setValue(self.settings.get_auto_save_interval())
        self.recent_limit.setValue(self.settings.get_recent_sessions_limit())
        self.remember_last_check.setChecked(self.settings.get('settings.remember_last_session', True))
        self.check_updates_check.setChecked(self.settings.get('settings.check_updates', True))
        
        # Editor settings
        self.font_size.setValue(self.settings.get_editor_font_size())
        self.tab_size.setValue(self.settings.get_tab_size())
        self.use_spaces_check.setChecked(self.settings.get('settings.use_spaces', True))
        self.line_numbers_check.setChecked(self.settings.is_line_numbers_enabled())
        self.word_wrap_check.setChecked(self.settings.is_word_wrap_enabled())
        self.highlight_line_check.setChecked(self.settings.is_highlight_current_line())
        self.bracket_matching_check.setChecked(self.settings.is_bracket_matching())
        self.syntax_highlighting_check.setChecked(self.settings.is_syntax_highlighting())
        
        # Cloud settings
        self.cloud_sync_check.setChecked(self.settings.is_cloud_sync_enabled())
        provider = self.settings.get_cloud_provider()
        self.cloud_provider_combo.setCurrentText(provider.title())
        self.auto_sync_check.setChecked(self.settings.get('cloud_sync.auto_sync', False))
        self.sync_interval.setValue(self.settings.get('cloud_sync.sync_interval', 300))
        
        # Sharing settings
        self.sharing_allowed_check.setChecked(self.settings.is_sharing_allowed())
        permission = self.settings.get('sharing.default_permission', 'read')
        perm_map = {'read': 'Read Only', 'write': 'Read/Write', 'admin': 'Admin'}
        self.default_permission_combo.setCurrentText(perm_map.get(permission, 'Read Only'))
    
    def apply_settings(self):
        """Apply settings changes"""
        # General settings
        theme = self.theme_combo.currentText().lower()
        self.settings.set_theme(theme)
        
        self.settings.set_auto_save(self.auto_save_check.isChecked())
        self.settings.set_auto_save_interval(self.auto_save_interval.value())
        self.settings.set_recent_sessions_limit(self.recent_limit.value())
        self.settings.set('settings.remember_last_session', self.remember_last_check.isChecked())
        self.settings.set('settings.check_updates', self.check_updates_check.isChecked())
        
        # Editor settings
        self.settings.set_editor_font_size(self.font_size.value())
        self.settings.set_tab_size(self.tab_size.value())
        self.settings.set('settings.use_spaces', self.use_spaces_check.isChecked())
        self.settings.set_line_numbers(self.line_numbers_check.isChecked())
        self.settings.set_word_wrap(self.word_wrap_check.isChecked())
        self.settings.set_highlight_current_line(self.highlight_line_check.isChecked())
        self.settings.set_bracket_matching(self.bracket_matching_check.isChecked())
        self.settings.set_syntax_highlighting(self.syntax_highlighting_check.isChecked())
        
        # Cloud settings
        self.settings.set_cloud_sync(self.cloud_sync_check.isChecked())
        provider = self.cloud_provider_combo.currentText().lower().replace(' ', '')
        self.settings.set_cloud_provider(provider)
        self.settings.set('cloud_sync.auto_sync', self.auto_sync_check.isChecked())
        self.settings.set('cloud_sync.sync_interval', self.sync_interval.value())
        
        # Sharing settings
        self.settings.set_sharing_allowed(self.sharing_allowed_check.isChecked())
        perm_map = {'Read Only': 'read', 'Read/Write': 'write', 'Admin': 'admin'}
        self.settings.set('sharing.default_permission', perm_map.get(self.default_permission_combo.currentText(), 'read'))
        
        # Apply theme to parent window if exists
        if hasattr(self, 'parent') and self.parent():
            parent = self.parent()
            if hasattr(parent, 'apply_theme'):
                parent.apply_theme(theme)
        
        QMessageBox.information(self, "Settings", "Settings applied successfully!")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        result = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self.load_current_settings()
            QMessageBox.information(self, "Settings", "Settings reset to defaults!")
    
    def accept(self):
        """Dialog accepted - apply settings and close"""
        self.apply_settings()
        super().accept()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.settings = SettingsManager()
        self.user_auth = UserDatabase()
        self.current_user_id = None
        self.current_user = None
        self.session_manager = None
        
        # Recent sessions
        self._recent_sessions = []
        self._max_recent_sessions = 10
        self._recent_sessions_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'CharmCrush', 'recent_sessions.json'
        )
        
        # Recovery file
        self._recovery_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'CharmCrush', 'recovery.json'
        )
        
        self.init_ui()
        self.apply_theme()
        self.show_login()
        self._load_recent_sessions()
        self._check_recovery()
    
    def init_ui(self):
        self.setWindowTitle("Charm Crush Session Manager")
        self.setMinimumSize(1200, 800)
        
        # Menu bar
        self.create_menu_bar()
        
        # Tool bar
        self.create_toolbar()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Session tree
        left_panel = self.create_session_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Tabbed editor
        right_panel = self.create_editor_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 900])
        layout.addWidget(splitter)
        
        central.setLayout(layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_session_action = QAction("New Session", self)
        new_session_action.setShortcut("Ctrl+N")
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)
        
        open_file_action = QAction("Open File", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_current_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("Import Session", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_session)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export Session", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_current_session)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Recent sessions submenu
        self.recent_sessions_menu = file_menu.addMenu("Recent Sessions")
        self._update_recent_sessions_menu()
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Session menu
        session_menu = menubar.addMenu("Session")
        
        rename_action = QAction("Rename", self)
        rename_action.setShortcut("F2")
        rename_action.triggered.connect(self.rename_current_session)
        session_menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_current_session)
        session_menu.addAction(delete_action)
        
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(self.duplicate_session)
        session_menu.addAction(duplicate_action)
        
        session_menu.addSeparator()
        
        add_file_action = QAction("Add File to Session", self)
        add_file_action.triggered.connect(self.add_file_to_session)
        session_menu.addAction(add_file_action)
        
        session_menu.addSeparator()
        
        batch_ops_action = QAction("Batch Operations...", self)
        batch_ops_action.triggered.connect(self.show_batch_operations)
        session_menu.addAction(batch_ops_action)
        
        session_menu.addSeparator()
        
        session_stats_action = QAction("Statistics...", self)
        session_stats_action.triggered.connect(self.show_session_stats)
        session_menu.addAction(session_stats_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("Find...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        find_replace_action = QAction("Find/Replace...", self)
        find_replace_action.setShortcut("Ctrl+H")
        find_replace_action.triggered.connect(self.show_find_replace_dialog)
        edit_menu.addAction(find_replace_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        collapse_all_action = QAction("Collapse All", self)
        collapse_all_action.triggered.connect(self.collapse_all_sessions)
        view_menu.addAction(collapse_all_action)
        
        expand_all_action = QAction("Expand All", self)
        expand_all_action.triggered.connect(self.expand_all_sessions)
        view_menu.addAction(expand_all_action)
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        from .utils import ThemeManager
        theme_names = ThemeManager.get_theme_names()
        for theme_name in theme_names:
            action = QAction(theme_name.title(), self)
            action.setData(theme_name)
            action.triggered.connect(lambda checked, t=theme_name: self.switch_theme(t))
            theme_menu.addAction(action)
        
        view_menu.addSeparator()
        
        settings_action = QAction("Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        view_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # New session
        new_btn = QPushButton("New Session")
        new_btn.clicked.connect(self.new_session)
        toolbar.addWidget(new_btn)
        
        # Add file
        add_btn = QPushButton("Add File")
        add_btn.clicked.connect(self.add_file_to_session)
        toolbar.addWidget(add_btn)
        
        toolbar.addSeparator()
        
        # Save
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_current_file)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # Find
        find_btn = QPushButton("Find")
        find_btn.clicked.connect(self.show_find_dialog)
        toolbar.addWidget(find_btn)
        
        toolbar.addSeparator()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sessions...")
        self.search_input.setMaximumWidth(200)
        self.search_input.textChanged.connect(self.filter_sessions)
        toolbar.addWidget(self.search_input)
    
    def create_session_panel(self) -> QWidget:
        """Create the session tree panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Session list
        self.session_tree = QTreeWidget()
        self.session_tree.setHeaderLabels(["Sessions"])
        self.session_tree.setRootIsDecorated(True)
        self.session_tree.itemClicked.connect(self.on_session_clicked)
        self.session_tree.itemDoubleClicked.connect(self.on_session_double_clicked)
        
        layout.addWidget(self.session_tree)
        
        panel.setLayout(layout)
        return panel
    
    def create_editor_panel(self) -> QWidget:
        """Create the tabbed editor panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Welcome tab
        welcome_tab = self.create_welcome_tab()
        self.editor_tabs.addTab(welcome_tab, "Welcome")
        
        layout.addWidget(self.editor_tabs)
        
        panel.setLayout(layout)
        return panel
    
    def create_welcome_tab(self):
        """Create welcome tab"""
        welcome_tab = QWidget()
        welcome_layout = QVBoxLayout()
        
        welcome_title = QLabel("Welcome to Charm Crush Session Manager")
        welcome_title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_title)
        
        welcome_text = QLabel(
            "Create a new session to get started, or import an existing session.\n\n"
            "Features:\n"
            "• Create and manage sessions\n"
            "• Edit config files with syntax highlighting (JSON, YAML, INI, TXT)\n"
            "• Import/export sessions\n"
            "• Multiple user accounts with encrypted storage\n"
            "• Session templates for quick setup\n"
            "• Batch operations on multiple sessions\n"
            "• Find and replace in editor\n"
            "• Bracket matching\n"
            "• Auto-save functionality"
        )
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_text.setStyleSheet("margin: 20px;")
        welcome_layout.addWidget(welcome_text)
        
        welcome_layout.addStretch()
        welcome_tab.setLayout(welcome_layout)
        return welcome_tab
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+S - Save
        save_shortcut = QShortcut("Ctrl+S", self)
        save_shortcut.activated.connect(self.save_current_file)
        
        # Ctrl+N - New session
        new_shortcut = QShortcut("Ctrl+N", self)
        new_shortcut.activated.connect(self.new_session)
        
        # Ctrl+F - Find
        find_shortcut = QShortcut("Ctrl+F", self)
        find_shortcut.activated.connect(self.show_find_dialog)
        
        # Ctrl+H - Find/Replace
        find_replace_shortcut = QShortcut("Ctrl+H", self)
        find_replace_shortcut.activated.connect(self.show_find_replace_dialog)
        
        # F2 - Rename
        rename_shortcut = QShortcut("F2", self)
        rename_shortcut.activated.connect(self.rename_current_session)
        
        # Delete - Delete
        delete_shortcut = QShortcut("Delete", self)
        delete_shortcut.activated.connect(self.delete_current_session)
    
    def apply_theme(self, theme_name: str = None):
        """Apply theme to the application"""
        if theme_name is None:
            theme_name = self.settings.get_theme() if hasattr(self, 'settings') else 'dark'
        self.setStyleSheet(ThemeManager.get_stylesheet(theme_name))
    
    def apply_dark_theme(self):
        """Apply dark theme to the application (backward compatibility)"""
        self.apply_theme('dark')
    
    def show_login(self):
        """Show login dialog"""
        dialog = LoginDialog(self.user_auth, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_user_id = dialog.authenticated_user_id
            self.current_user = self.user_auth.get_user(self.current_user_id)
            self.session_manager = SessionManager(self.user_auth, self.current_user_id)
            self.statusBar.showMessage(f"Logged in as: {self.current_user['username']}")
            self.refresh_session_tree()
        else:
            sys.exit(0)
    
    # ============ Recent Sessions ============
    
    def _load_recent_sessions(self):
        """Load recent sessions from file"""
        try:
            if os.path.exists(self._recent_sessions_file):
                with open(self._recent_sessions_file, 'r') as f:
                    self._recent_sessions = json.load(f)
        except:
            self._recent_sessions = []
    
    def _save_recent_sessions(self):
        """Save recent sessions to file"""
        try:
            os.makedirs(os.path.dirname(self._recent_sessions_file), exist_ok=True)
            with open(self._recent_sessions_file, 'w') as f:
                json.dump(self._recent_sessions, f)
        except:
            pass
    
    def _update_recent_sessions_menu(self):
        """Update recent sessions menu"""
        self.recent_sessions_menu.clear()
        
        for session_info in self._recent_sessions[:self._max_recent_sessions]:
            action = QAction(session_info['name'], self)
            action.setData(session_info['id'])
            action.triggered.connect(lambda checked, sid=session_info['id']: self.open_recent_session(sid))
            self.recent_sessions_menu.addAction(action)
        
        if self._recent_sessions:
            self.recent_sessions_menu.addSeparator()
            clear_action = QAction("Clear List", self)
            clear_action.triggered.connect(self._clear_recent_sessions)
            self.recent_sessions_menu.addAction(clear_action)
    
    def _add_to_recent_sessions(self, session_id: str, session_name: str):
        """Add session to recent list"""
        # Remove if already exists
        self._recent_sessions = [s for s in self._recent_sessions if s['id'] != session_id]
        
        # Add to beginning
        self._recent_sessions.insert(0, {'id': session_id, 'name': session_name})
        
        # Limit size
        self._recent_sessions = self._recent_sessions[:self._max_recent_sessions]
        
        # Save and update menu
        self._save_recent_sessions()
        self._update_recent_sessions_menu()
    
    def _clear_recent_sessions(self):
        """Clear recent sessions list"""
        self._recent_sessions = []
        self._save_recent_sessions()
        self._update_recent_sessions_menu()
    
    def open_recent_session(self, session_id: str):
        """Open a recent session"""
        session = self.session_manager.get_session(session_id)
        if session:
            self._add_to_recent_sessions(session_id, session['name'])
            # Expand and show session
            for i in range(self.session_tree.topLevelItemCount()):
                item = self.session_tree.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == session_id:
                    item.setExpanded(True)
                    self.session_tree.setCurrentItem(item)
                    break
    
    # ============ Session Recovery ============
    
    def _check_recovery(self):
        """Check for and load recovery data"""
        try:
            if os.path.exists(self._recovery_file):
                result = QMessageBox.question(
                    self, "Recovery",
                    "Unsaved sessions were found from a previous session. Load them?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if result == QMessageBox.StandardButton.Yes:
                    self._load_recovery()
                # Remove recovery file
                try:
                    os.remove(self._recovery_file)
                except:
                    pass
        except:
            pass
    
    def _save_recovery(self):
        """Save current state for recovery"""
        recovery_data = {
            'unsaved_sessions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            os.makedirs(os.path.dirname(self._recovery_file), exist_ok=True)
            with open(self._recovery_file, 'w') as f:
                json.dump(recovery_data, f)
        except:
            pass
    
    def _load_recovery(self):
        """Load recovered sessions"""
        # Recovery implementation
        pass
    
    # ============ Session Tree ============
    
    def refresh_session_tree(self):
        """Refresh the session tree"""
        self.session_tree.clear()
        
        if not self.session_manager:
            return
        
        sessions = self.session_manager.get_all_sessions()
        
        for session in sessions:
            item = QTreeWidgetItem([session['name']])
            item.setData(0, Qt.ItemDataRole.UserRole, session['id'])
            item.setToolTip(0, session.get('description', ''))
            
            # Add files as children
            session_data = self.session_manager.get_session(session['id'])
            if session_data and session_data.get('files'):
                for file_info in session_data['files']:
                    file_item = QTreeWidgetItem([os.path.basename(file_info['file_path'])])
                    file_item.setData(0, Qt.ItemDataRole.UserRole, {
                        'session_id': session['id'],
                        'file_id': file_info['id'],
                        'file_path': file_info['file_path'],
                        'format': file_info['format']
                    })
                    item.addChild(file_item)
            
            self.session_tree.addTopLevelItem(item)
        
        self.session_tree.expandAll()
    
    def filter_sessions(self, query: str):
        """Filter sessions based on search query"""
        if not query:
            self.refresh_session_tree()
            return
        
        self.session_tree.clear()
        matching = self.session_manager.search_sessions(query)
        
        for session in matching:
            item = QTreeWidgetItem([session['name']])
            item.setData(0, Qt.ItemDataRole.UserRole, session['id'])
            self.session_tree.addTopLevelItem(item)
    
    def on_session_clicked(self, item, column):
        """Handle session click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, dict) and 'file_path' in data:
            # File clicked - open in editor
            self.open_file_from_session(data)
    
    def on_session_double_clicked(self, item, column):
        """Handle session double click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            # Session clicked - expand/collapse
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
    
    # ============ Session Operations ============
    
    def new_session(self):
        """Create a new session"""
        templates = self.session_manager.get_available_templates() if self.session_manager else []
        dialog = NewSessionDialog(templates, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.session_template and dialog.session_template != 'empty':
                session_id = self.session_manager.create_session_from_template(
                    dialog.session_template,
                    dialog.session_name,
                    dialog.session_description
                )
            else:
                session_id = self.session_manager.create_session(
                    dialog.session_name,
                    dialog.session_description
                )
            
            if session_id:
                self.refresh_session_tree()
                self._add_to_recent_sessions(session_id, dialog.session_name)
                self.statusBar.showMessage(f"Created session: {dialog.session_name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to create session")
    
    def open_file(self):
        """Open a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Config Files (*.json *.yaml *.yml *.ini *.txt);;All Files (*)"
        )
        if file_path:
            self.open_file_external(file_path)
    
    def open_file_external(self, file_path: str):
        """Open an external file"""
        from .config_editor import ConfigEditor
        
        editor = ConfigEditor()
        if editor.load_file(file_path):
            tab_title = os.path.basename(file_path)
            index = self.editor_tabs.addTab(editor, tab_title)
            self.editor_tabs.setCurrentIndex(index)
            self.statusBar.showMessage(f"Opened: {file_path}")
        else:
            QMessageBox.warning(self, "Error", "Failed to open file")
    
    def open_file_from_session(self, file_data: dict):
        """Open a file from session"""
        session_id = file_data['session_id']
        file_path = file_data['file_path']
        file_id = file_data['file_id']
        file_format = file_data['format']
        
        # Check if already open
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if isinstance(editor, ConfigEditor):
                if getattr(editor, 'session_file_id', None) == file_id:
                    self.editor_tabs.setCurrentIndex(i)
                    return
        
        # Load from session
        session = self.session_manager.get_session(session_id)
        if session:
            from .config_editor import ConfigEditor
            
            editor = ConfigEditor()
            content = ""
            for f in session.get('files', []):
                if f['id'] == file_id:
                    if f['content']:
                        try:
                            content = f['content'].decode('utf-8')
                        except:
                            content = str(f['content'])
                    break
            
            editor.load_content(content, file_format)
            editor.session_file_id = file_id
            editor.session_id = session_id
            editor.current_file_path = file_path
            
            tab_title = os.path.basename(file_path)
            index = self.editor_tabs.addTab(editor, tab_title)
            self.editor_tabs.setCurrentIndex(index)
    
    def save_current_file(self):
        """Save the current file"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            if current_widget.save_file():
                self.statusBar.showMessage("File saved")
    
    def save_current_file_as(self):
        """Save current file with new name"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save As", "",
                "Config Files (*.json *.yaml *.yml *.ini *.txt);;All Files (*)"
            )
            if file_path:
                if current_widget.save_file(file_path):
                    # Update tab title
                    tab_title = os.path.basename(file_path)
                    index = self.editor_tabs.currentIndex()
                    self.editor_tabs.setTabText(index, tab_title)
                    self.statusBar.showMessage("File saved")
    
    def close_tab(self, index):
        """Close a tab"""
        widget = self.editor_tabs.widget(index)
        if isinstance(widget, ConfigEditor):
            if widget.is_modified():
                result = QMessageBox.question(
                    self, "Unsaved Changes",
                    "This file has unsaved changes. Save before closing?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )
                if result == QMessageBox.StandardButton.Cancel:
                    return
                elif result == QMessageBox.StandardButton.Yes:
                    self.save_current_file()
        
        self.editor_tabs.removeTab(index)
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        widget = self.editor_tabs.widget(index)
        if isinstance(widget, ConfigEditor):
            self.statusBar.showMessage(f"Editing: {widget.current_file_path or 'Untitled'}")
    
    def rename_current_session(self):
        """Rename the current session"""
        current_item = self.session_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a session first")
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            session_data = self.session_manager.get_session(data)
            if session_data:
                dialog = RenameSessionDialog(session_data['name'], self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    if self.session_manager.rename_session(data, dialog.new_name):
                        self.refresh_session_tree()
                        self._add_to_recent_sessions(data, dialog.new_name)
                        self.statusBar.showMessage(f"Renamed to: {dialog.new_name}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to rename session")
    
    def delete_current_session(self):
        """Delete the current session"""
        current_item = self.session_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a session first")
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            result = QMessageBox.question(
                self, "Delete Session",
                "Are you sure you want to delete this session and all its files?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                if self.session_manager.delete_session(data):
                    self.refresh_session_tree()
                    self.statusBar.showMessage("Session deleted")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete session")
    
    def duplicate_session(self):
        """Duplicate the current session"""
        current_item = self.session_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a session first")
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            new_id = self.session_manager.duplicate_session(data)
            if new_id:
                self.refresh_session_tree()
                session = self.session_manager.get_session(new_id)
                if session:
                    self._add_to_recent_sessions(new_id, session['name'])
                self.statusBar.showMessage("Session duplicated")
            else:
                QMessageBox.warning(self, "Error", "Failed to duplicate session")
    
    def add_file_to_session(self):
        """Add a file to the current session"""
        current_item = self.session_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a session first")
            return
        
        # Get session ID (may be parent item)
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, dict) and 'session_id' in data:
            session_id = data['session_id']
        elif isinstance(data, str):
            session_id = data
        else:
            QMessageBox.warning(self, "Error", "Please select a session first")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add File to Session", "",
            "Config Files (*.json *.yaml *.yml *.ini *.txt);;All Files (*)"
        )
        if file_path:
            from .utils import FileFormat
            format_type = FileFormat.detect_format(file_path)
            
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                if self.session_manager.add_file_to_session(session_id, file_path, format_type, content):
                    self.refresh_session_tree()
                    self.statusBar.showMessage(f"Added file: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to add file")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read file: {str(e)}")
    
    def import_session(self):
        """Import a session from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Session", "",
            "Session Files (*.json);;All Files (*)"
        )
        if file_path:
            # Ask for new name
            name, ok = QInputDialog.getText(self, "Import Session", "Enter name for imported session:")
            if ok:
                success, new_id, errors = self.session_manager.import_session_safe(file_path, name if name else None)
                if success:
                    self.refresh_session_tree()
                    session = self.session_manager.get_session(new_id)
                    if session:
                        self._add_to_recent_sessions(new_id, session['name'])
                    self.statusBar.showMessage("Session imported")
                else:
                    error_msg = "\n".join(errors) if errors else "Failed to import session"
                    QMessageBox.warning(self, "Error", error_msg)
    
    def export_current_session(self):
        """Export the current session"""
        current_item = self.session_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a session first")
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Session", f"{current_item.text(0)}.json",
                "Session Files (*.json);;All Files (*)"
            )
            if file_path:
                if self.session_manager.export_session(data, file_path):
                    self.statusBar.showMessage(f"Session exported to: {file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to export session")
    
    def export_specific_session(self, session_id: str):
        """Export a specific session"""
        session = self.session_manager.get_session(session_id)
        if session:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Session", f"{session['name']}.json",
                "Session Files (*.json);;All Files (*)"
            )
            if file_path:
                if self.session_manager.export_session(session_id, file_path):
                    self.statusBar.showMessage(f"Session exported to: {file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to export session")
    
    def collapse_all_sessions(self):
        """Collapse all session items"""
        for i in range(self.session_tree.topLevelItemCount()):
            self.session_tree.topLevelItem(i).setExpanded(False)
    
    def expand_all_sessions(self):
        """Expand all session items"""
        self.session_tree.expandAll()
    
    def switch_theme(self, theme_name: str):
        """Switch to a different theme"""
        self.apply_theme(theme_name)
        self.settings.set_theme(theme_name)
        self.statusBar.showMessage(f"Theme changed to: {theme_name.title()}")
    
    # ============ Batch Operations ============
    
    def show_batch_operations(self):
        """Show batch operations dialog"""
        if not self.session_manager:
            return
        
        dialog = BatchOperationsDialog(self.session_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            operation = dialog.get_operation()
            session_ids = dialog.get_selected_sessions()
            
            if operation == 'delete':
                self._batch_delete_sessions(session_ids)
            elif operation == 'export':
                self._batch_export_sessions(session_ids)
            elif operation == 'add_tag':
                self._batch_add_tag(session_ids, dialog.get_tag())
            elif operation == 'remove_tag':
                self._batch_remove_tag(session_ids, dialog.get_tag())
    
    def _batch_delete_sessions(self, session_ids):
        """Delete multiple sessions"""
        result = QMessageBox.question(
            self, "Batch Delete",
            f"Are you sure you want to delete {len(session_ids)} sessions?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result == QMessageBox.StandardButton.Yes:
            results = self.session_manager.delete_sessions(session_ids)
            self.refresh_session_tree()
            self.statusBar.showMessage(f"Deleted {results['deleted']} sessions, {results['failed']} failed")
    
    def _batch_export_sessions(self, session_ids):
        """Export multiple sessions"""
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", ""
        )
        if output_dir:
            results = self.session_manager.export_sessions(session_ids, output_dir)
            self.statusBar.showMessage(f"Exported {results['exported']} sessions, {results['failed']} failed")
    
    def _batch_add_tag(self, session_ids, tag):
        """Add tag to multiple sessions"""
        for session_id in session_ids:
            self.session_manager.add_session_tag(session_id, tag)
        self.refresh_session_tree()
        self.statusBar.showMessage(f"Added tag '{tag}' to {len(session_ids)} sessions")
    
    def _batch_remove_tag(self, session_ids, tag):
        """Remove tag from multiple sessions"""
        for session_id in session_ids:
            self.session_manager.remove_session_tag(session_id, tag)
        self.refresh_session_tree()
        self.statusBar.showMessage(f"Removed tag '{tag}' from {len(session_ids)} sessions")
    
    # ============ Session Statistics ============
    
    def show_session_stats(self):
        """Show session statistics dialog"""
        if self.session_manager:
            dialog = SessionStatsDialog(self.session_manager, self)
            dialog.exec()
    
    # ============ Settings ============
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    # ============ Find/Replace ============
    
    def show_find_dialog(self):
        """Show find dialog"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            current_widget.show_find_dialog()
    
    def show_find_replace_dialog(self):
        """Show find/replace dialog"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            current_widget.show_find_replace_dialog()
    
    # ============ Edit Actions ============
    
    def undo(self):
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            current_widget.undo()
    
    def redo(self):
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            current_widget.redo()
    
    def cut(self):
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            current_widget.cut()
    
    def copy(self):
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            current_widget.copy()
    
    def paste(self):
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, ConfigEditor):
            current_widget.paste()
    
    def show_about(self):
        QMessageBox.about(
            self, "About Charm Crush Session Manager",
            "Charm Crush Session Manager v1.0\n\n"
            "A Windows desktop application for managing configuration files and sessions.\n\n"
            "Features:\n"
            "• Load and view config files (JSON, YAML, INI, TXT)\n"
            "• Edit with syntax highlighting\n"
            "• Session management (create, save, load, delete)\n"
            "• Import/export sessions as JSON\n"
            "• Multiple user accounts with encrypted storage\n"
            "• Session templates for quick setup\n"
            "• Batch operations on multiple sessions\n"
            "• Find and replace in editor\n"
            "• Bracket matching\n"
            "• Auto-save functionality"
        )
    
    def closeEvent(self, event):
        """Handle close event"""
        # Check for unsaved changes
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if isinstance(widget, ConfigEditor) and widget.is_modified():
                result = QMessageBox.question(
                    self, "Unsaved Changes",
                    "There are unsaved changes. Quit anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if result == QMessageBox.StandardButton.No:
                    event.ignore()
                    return
                break
        
        # Save recovery data
        self._save_recovery()
        
        # Close connection pool
        if self.user_auth:
            self.user_auth.close_all()
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
