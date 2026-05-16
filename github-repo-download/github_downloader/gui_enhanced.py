"""
GitHub Repo Downloader - Enhanced GUI with all features
Built with PyQt6 - Dark theme, CLI mode, sync, scheduling, and more
"""
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import threading

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QTableWidget, QTableWidgetItem, QProgressBar,
                              QTabWidget, QFormLayout, QGroupBox, QComboBox,
                              QCheckBox, QSpinBox, QFileDialog, QMessageBox,
                              QStatusBar, QToolBar, QMenuBar, QMenu, QDialog,
                              QDialogButtonBox, QListWidget, QListWidgetItem,
                              QSplitter, QFrame, QScrollArea, QTreeWidget,
                              QTreeWidgetItem, QSystemTrayIcon, QMenu as QTrayMenu,
                              QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QDateTime
from PyQt6.QtGui import (QIcon, QAction, QFont, QColor, QPalette, QDragEnterEvent, 
                       QDropEvent, QPixmap, QDrag, QShortcut)

from .user_auth import UserDatabase
from .github_api import GitHubAPIClient, GitHubOAuth, AuthType
from .downloader import GitRepoDownloader, DownloadTask, DownloadStatus, DownloadMethod
from .gui import (CLIMode, ThemeManager, NotificationManager, SyncManager, 
                  BookmarksManager, DownloadThread, MultiAccountManager, 
                  SelectiveDownloadDialog, ScheduledDownloadDialog, LoginDialog, 
                  GitHubAuthDialog, SettingsDialog)

# ============== MAIN WINDOW ==============

class MainWindow(QMainWindow):
    """Main application window with all enhancements"""
    
    def __init__(self, cli_mode=False):
        super().__init__()
        
        # Core components
        self.user_auth = UserDatabase()
        self.current_user_id = None
        self.github_client = None
        self.downloader = None
        self.download_threads = {}
        self.cached_repos = []
        
        # Enhancement managers
        self.theme_manager = ThemeManager()
        self.notification_manager = NotificationManager(self)
        self.sync_manager = None
        self.bookmarks_manager = None
        self.account_manager = MultiAccountManager(self.user_auth)
        
        # Sync timer for scheduled tasks
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.run_scheduled_syncs)
        self.sync_timer.start(60000) # Every minute
        
        # Recent repos - will be loaded after UI init
        self.recent_repos = []
        
        # Drag and drop
        self.setAcceptDrops(True)
        
        # Initialize
        if cli_mode:
            self.run_cli_mode()
        else:
            self.init_ui()
            self.setup_keyboard_shortcuts()
            self.load_recent_repos()  # Load after UI init
            self.show_login()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop"""
        text = event.mimeData().text()
        if text:
            # Parse dropped URL
            self.repo_url.setText(text.strip())
            self.tabs.setCurrentIndex(0)  # Switch to download tab
    
    def init_ui(self):
        self.setWindowTitle("GitHub Repo Downloader")
        self.setMinimumSize(1100, 750)
        
        # Apply dark theme by default
        self.theme_manager.apply_theme(QApplication.instance(), dark=True)
        
        # Menu bar
        self.create_menu_bar()
        
        # Tool bar
        self.create_toolbar()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Quick access bar with recent repos
        self.create_quick_access_bar()
        layout.addWidget(self.quick_access_bar)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Single Download Tab
        self.download_tab = self.create_download_tab()
        self.tabs.addTab(self.download_tab, "⬇️ Download")
        
        # Batch Download Tab
        self.batch_tab = self.create_batch_tab()
        self.tabs.addTab(self.batch_tab, "📚 Batch")
        
        # Search Tab
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, "🔍 Search")
        
        # My Repos Tab
        self.my_repos_tab = self.create_my_repos_tab()
        self.tabs.addTab(self.my_repos_tab, "📁 My Repos")
        
        # Bookmarks Tab
        self.bookmarks_tab = self.create_bookmarks_tab()
        self.tabs.addTab(self.bookmarks_tab, "⭐ Bookmarks")
        
        # Sync Tab
        self.sync_tab = self.create_sync_tab()
        self.tabs.addTab(self.sync_tab, "🔄 Sync")
        
        # History Tab
        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, "📋 History")
        
        layout.addWidget(self.tabs)
        
        # Active downloads
        self.active_downloads_group = QGroupBox("⚡ Active Downloads")
        downloads_layout = QVBoxLayout()
        
        self.downloads_table = QTableWidget()
        self.downloads_table.setColumnCount(6)
        self.downloads_table.setHorizontalHeaderLabels(
            ["Repository", "Status", "Progress", "Current File", "Size", "Actions"]
        )
        self.downloads_table.horizontalHeader().setStretchLastSection(True)
        downloads_layout.addWidget(self.downloads_table)
        
        self.active_downloads_group.setLayout(downloads_layout)
        layout.addWidget(self.active_downloads_group)
        
        central.setLayout(layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Rate limit timer
        self.rate_timer = QTimer()
        self.rate_timer.timeout.connect(self.update_rate_limit)
        self.rate_timer.start(60000)
    
    def create_quick_access_bar(self):
        """Create quick access bar with recent repos"""
        self.quick_access_bar = QGroupBox("⚡ Quick Access")
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Recent:"))
        
        self.recent_combo = QComboBox()
        self.recent_combo.setEditable(True)
        self.recent_combo.setPlaceholderText("Recent repositories...")
        self.recent_combo.currentIndexChanged.connect(self.load_from_recent)
        layout.addWidget(self.recent_combo)
        
        add_bookmark_btn = QPushButton("⭐+")
        add_bookmark_btn.setToolTip("Add to bookmarks")
        add_bookmark_btn.clicked.connect(self.add_current_to_bookmarks)
        layout.addWidget(add_bookmark_btn)
        
        layout.addStretch()
        
        theme_btn = QPushButton("🌙")
        theme_btn.setToolTip("Toggle dark/light theme")
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)
        
        self.quick_access_bar.setLayout(layout)
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_download = QAction("New Download", self)
        new_download.setShortcut("Ctrl+N")
        new_download.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        file_menu.addAction(new_download)
        
        batch_download = QAction("Batch Download", self)
        batch_download.setShortcut("Ctrl+B")
        batch_download.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        file_menu.addAction(batch_download)
        
        file_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Account menu
        account_menu = menubar.addMenu("Account")
        
        login_action = QAction("Login", self)
        login_action.triggered.connect(self.show_login)
        account_menu.addAction(login_action)
        
        switch_account = QAction("Switch Account", self)
        switch_account.triggered.connect(self.show_switch_account)
        account_menu.addAction(switch_account)
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        account_menu.addAction(logout_action)
        
        account_menu.addSeparator()
        
        github_auth_action = QAction("GitHub Authentication", self)
        github_auth_action.triggered.connect(self.show_github_auth)
        account_menu.addAction(github_auth_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        toggle_theme = QAction("Toggle Dark/Light Theme", self)
        toggle_theme.setShortcut("Ctrl+T")
        toggle_theme.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        schedule_action = QAction("Schedule Download", self)
        schedule_action.triggered.connect(self.show_schedule_dialog)
        tools_menu.addAction(schedule_action)
        
        sync_action = QAction("Sync All Repos", self)
        sync_action.triggered.connect(self.sync_all_repos)
        tools_menu.addAction(sync_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        terms_action = QAction("GitHub Terms Compliance", self)
        terms_action.triggered.connect(self.show_terms)
        help_menu.addAction(terms_action)
    
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        home_btn = QPushButton("🏠")
        home_btn.setToolTip("Home")
        home_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        toolbar.addWidget(home_btn)
        
        toolbar.addSeparator()
        
        login_btn = QPushButton("👤 Login")
        login_btn.clicked.connect(self.show_login)
        toolbar.addWidget(login_btn)
        
        auth_btn = QPushButton("🔐 GitHub Auth")
        auth_btn.clicked.connect(self.show_github_auth)
        toolbar.addWidget(auth_btn)
        
        toolbar.addSeparator()
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_btn)
    
    def create_download_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Repository input
        repo_group = QGroupBox("Repository")
        repo_layout = QFormLayout()
        
        self.repo_url = QLineEdit()
        self.repo_url.setPlaceholderText("https://github.com/owner/repo or owner/repo")
        repo_layout.addRow("Repository URL:", self.repo_url)
        
        self.repo_branch = QLineEdit()
        self.repo_branch.setPlaceholderText("main (leave empty for default)")
        repo_layout.addRow("Branch:", self.repo_branch)
        
        repo_group.setLayout(repo_layout)
        layout.addWidget(repo_group)
        
        # Download options
        options_group = QGroupBox("Download Options")
        options_layout = QFormLayout()
        
        self.download_path = QLineEdit()
        self.download_path.setText(os.path.expanduser("~\\Downloads"))
        self.browse_btn = QPushButton("📁")
        self.browse_btn.clicked.connect(self.browse_download_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.download_path)
        path_layout.addWidget(self.browse_btn)
        options_layout.addRow("Download to:", path_layout)
        
        self.download_method = QComboBox()
        self.download_method.addItems(["Git Clone", "Download ZIP", "Download TAR.gz", "Selective Download"])
        options_layout.addRow("Method:", self.download_method)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Download button
        self.download_btn = QPushButton("⬇️ Download Repository")
        self.download_btn.setMinimumHeight(45)
        self.download_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.download_btn.clicked.connect(self.start_single_download)
        layout.addWidget(self.download_btn)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_batch_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Input
        input_group = QGroupBox("Repository List (one per line or drag files)")
        input_layout = QVBoxLayout()
        
        self.batch_list = QListWidget()
        self.batch_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.batch_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        input_layout.addWidget(self.batch_list)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Add URL")
        add_btn.clicked.connect(self.add_batch_url)
        btn_layout.addWidget(add_btn)
        
        from_file_btn = QPushButton("📄 From File")
        from_file_btn.clicked.connect(self.load_from_file)
        btn_layout.addWidget(from_file_btn)
        
        remove_btn = QPushButton("🗑️ Remove")
        remove_btn.clicked.connect(self.remove_batch_urls)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("✨ Clear")
        clear_btn.clicked.connect(self.batch_list.clear)
        btn_layout.addWidget(clear_btn)
        
        input_layout.addLayout(btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Options
        batch_options = QGroupBox("Options")
        options_layout = QFormLayout()
        
        self.batch_output_path = QLineEdit()
        self.batch_output_path.setText(os.path.expanduser("~\\Downloads"))
        self.batch_browse_btn = QPushButton("📁")
        self.batch_browse_btn.clicked.connect(self.browse_batch_path)
        
        batch_path_layout = QHBoxLayout()
        batch_path_layout.addWidget(self.batch_output_path)
        batch_path_layout.addWidget(self.batch_browse_btn)
        options_layout.addRow("Output directory:", batch_path_layout)
        
        self.batch_method = QComboBox()
        self.batch_method.addItems(["Git Clone", "Download ZIP", "Download TAR.gz"])
        options_layout.addRow("Method:", self.batch_method)
        
        self.parallel_check = QCheckBox("Download in parallel (max 3)")
        self.parallel_check.setChecked(True)
        options_layout.addRow("", self.parallel_check)
        
        batch_options.setLayout(options_layout)
        layout.addWidget(batch_options)
        
        # Start batch
        self.batch_download_btn = QPushButton("📚 Start Batch Download")
        self.batch_download_btn.setMinimumHeight(45)
        self.batch_download_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #4CAF50;")
        self.batch_download_btn.clicked.connect(self.start_batch_download)
        layout.addWidget(self.batch_download_btn)
        
        tab.setLayout(layout)
        return tab
    
    def create_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        search_group = QGroupBox("Search GitHub")
        search_layout = QHBoxLayout()
        
        self.search_query = QLineEdit()
        self.search_query.setPlaceholderText("Search repositories...")
        self.search_query.returnPressed.connect(self.search_repos)
        search_layout.addWidget(self.search_query)
        
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self.search_repos)
        search_layout.addWidget(self.search_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(5)
        self.search_results.setHorizontalHeaderLabels(
            ["Name", "Owner", "Stars", "Description", "Action"]
        )
        self.search_results.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.search_results)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_my_repos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        user_group = QGroupBox("User Repositories")
        user_layout = QHBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("GitHub username (leave empty for authenticated user)")
        user_layout.addWidget(self.username_input)
        
        self.load_repos_btn = QPushButton("📥 Load Repos")
        self.load_repos_btn.clicked.connect(self.load_user_repos)
        user_layout.addWidget(self.load_repos_btn)
        
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        all_repos_group = QGroupBox("Download All Repositories")
        all_repos_layout = QVBoxLayout()
        
        all_repos_top_layout = QHBoxLayout()
        
        self.all_repos_path = QLineEdit()
        self.all_repos_path.setText(os.path.expanduser("~\\Downloads"))
        all_repos_top_layout.addWidget(self.all_repos_path)
        
        self.all_repos_browse_btn = QPushButton("📁")
        self.all_repos_browse_btn.clicked.connect(self.browse_all_repos_path)
        all_repos_top_layout.addWidget(self.all_repos_browse_btn)
        
        all_repos_layout.addLayout(all_repos_top_layout)
        
        all_repos_bottom_layout = QHBoxLayout()
        
        self.all_repos_method = QComboBox()
        self.all_repos_method.addItems(["Git Clone", "Download ZIP", "Download TAR.gz"])
        all_repos_bottom_layout.addWidget(self.all_repos_method)
        
        self.download_all_btn = QPushButton("⬇️ Download ALL Repositories")
        self.download_all_btn.setMinimumHeight(45)
        self.download_all_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #4CAF50;")
        self.download_all_btn.clicked.connect(self.download_all_repos)
        all_repos_bottom_layout.addWidget(self.download_all_btn)
        
        self.all_repos_parallel_check = QCheckBox("Parallel")
        self.all_repos_parallel_check.setChecked(True)
        all_repos_bottom_layout.addWidget(self.all_repos_parallel_check)
        
        all_repos_layout.addLayout(all_repos_bottom_layout)
        all_repos_group.setLayout(all_repos_layout)
        layout.addWidget(all_repos_group)
        
        repos_group = QGroupBox("Repositories")
        repos_layout = QVBoxLayout()
        
        self.repos_table = QTableWidget()
        self.repos_table.setColumnCount(5)
        self.repos_table.setHorizontalHeaderLabels(
            ["Name", "Description", "Language", "Updated", "Action"]
        )
        self.repos_table.horizontalHeader().setStretchLastSection(True)
        repos_layout.addWidget(self.repos_table)
        
        repos_group.setLayout(repos_layout)
        layout.addWidget(repos_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_bookmarks_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        bookmark_group = QGroupBox("⭐ Bookmarks")
        bookmark_layout = QVBoxLayout()
        
        # Search bookmarks
        search_layout = QHBoxLayout()
        
        self.bookmark_search = QLineEdit()
        self.bookmark_search.setPlaceholderText("Search bookmarks...")
        self.bookmark_search.textChanged.connect(self.filter_bookmarks)
        search_layout.addWidget(self.bookmark_search)
        
        add_bookmark = QPushButton("+ Add")
        add_bookmark.clicked.connect(self.show_add_bookmark)
        search_layout.addWidget(add_bookmark)
        
        bookmark_layout.addLayout(search_layout)
        
        # Bookmarks list
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        bookmark_layout.addWidget(self.bookmarks_list)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        download_btn = QPushButton("⬇️ Download Selected")
        download_btn.clicked.connect(self.download_from_bookmarks)
        actions_layout.addWidget(download_btn)
        
        remove_btn = QPushButton("🗑️ Remove")
        remove_btn.clicked.connect(self.remove_bookmarks)
        actions_layout.addWidget(remove_btn)
        
        actions_layout.addStretch()
        
        bookmark_layout.addLayout(actions_layout)
        bookmark_group.setLayout(bookmark_layout)
        layout.addWidget(bookmark_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_sync_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        sync_group = QGroupBox("🔄 Repository Sync")
        sync_layout = QVBoxLayout()
        
        # Scheduled syncs
        scheduled_group = QGroupBox("Scheduled Syncs")
        scheduled_layout = QVBoxLayout()
        
        self.scheduled_list = QListWidget()
        scheduled_layout.addWidget(self.scheduled_list)
        
        scheduled_btn_layout = QHBoxLayout()
        
        add_schedule = QPushButton("+ Add Schedule")
        add_schedule.clicked.connect(self.show_schedule_dialog)
        scheduled_btn_layout.addWidget(add_schedule)
        
        remove_schedule = QPushButton("Remove")
        remove_schedule.clicked.connect(self.remove_schedule)
        scheduled_btn_layout.addWidget(remove_schedule)
        
        scheduled_btn_layout.addStretch()
        
        sync_now = QPushButton("🔄 Sync Now")
        sync_now.clicked.connect(self.sync_all_repos)
        scheduled_btn_layout.addWidget(sync_now)
        
        scheduled_layout.addLayout(scheduled_btn_layout)
        scheduled_group.setLayout(scheduled_layout)
        sync_layout.addWidget(scheduled_group)
        
        # Local repos sync
        local_group = QGroupBox("Sync Local Repositories")
        local_layout = QFormLayout()
        
        self.local_repos_path = QLineEdit()
        self.local_repos_path.setText(os.path.expanduser("~\\Documents\\GitHub"))
        local_layout.addRow("Local repos folder:", self.local_repos_path)
        
        sync_btn = QPushButton("🔄 Sync All Local Repos")
        sync_btn.clicked.connect(self.sync_local_repos)
        local_layout.addRow("", sync_btn)
        
        local_group.setLayout(local_layout)
        sync_layout.addWidget(local_group)
        
        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            ["Repository", "Date", "Path", "Files", "Size", "Status", "Action"]
        )
        self.history_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.history_table)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_history)
        btn_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        tab.setLayout(layout)
        return tab
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut("Ctrl+D", self, self.download_current)
        QShortcut("Ctrl+L", self, self.focus_download_path)
        QShortcut("Ctrl+R", self, self.load_user_repos)
        QShortcut("Ctrl+S", self, self.show_settings)
        QShortcut("Ctrl+F", self, self.focus_search)
    
    def focus_download_path(self):
        self.download_path.setFocus()
        self.download_path.selectAll()
    
    def focus_search(self):
        self.search_query.setFocus()
        self.search_query.selectAll()
    
    def download_current(self):
        self.start_single_download()
    
    def toggle_theme(self):
        is_dark = self.theme_manager.toggle_theme(QApplication.instance())
        self.statusBar.showMessage(f"Theme: {'Dark' if is_dark else 'Light'}")
    
    def show_switch_account(self):
        """Show dialog to switch between accounts"""
        accounts = self.account_manager.accounts
        
        if not accounts:
            QMessageBox.information(self, "No Accounts", "No saved accounts. Add a GitHub token to save an account.")
            return
        
        items = [f"{a['name']} ({a['username']})" for a in accounts]
        item, ok = QInputDialog.getItem(self, "Switch Account", "Select account:", items, 0, False)
        
        if ok:
            self.account_manager.switch_account(items.index(item))
            self.update_github_status()
    
    def show_add_bookmark(self):
        url, ok = QInputDialog.getText(self, "Add Bookmark", "Enter repository URL:")
        if ok and url:
            name, ok = QInputDialog.getText(self, "Bookmark Name", "Enter name (optional):")
            if self.bookmarks_manager:
                self.bookmarks_manager.add_bookmark(url, name if ok else None)
                self.refresh_bookmarks()
    
    def filter_bookmarks(self):
        query = self.bookmark_search.text()
        if self.bookmarks_manager:
            bookmarks = self.bookmarks_manager.search_bookmarks(query)
            self.display_bookmarks(bookmarks)
    
    def display_bookmarks(self, bookmarks):
        self.bookmarks_list.clear()
        for b in bookmarks:
            item = QListWidgetItem(f"⭐ {b['name']}")
            item.setData(Qt.ItemDataRole.UserRole, b['url'])
            self.bookmarks_list.addItem(item)
    
    def refresh_bookmarks(self):
        if self.bookmarks_manager:
            self.display_bookmarks(self.bookmarks_manager.get_bookmarks())
    
    def download_from_bookmarks(self):
        for item in self.bookmarks_list.selectedItems():
            url = item.data(Qt.ItemDataRole.UserRole)
            self.repo_url.setText(url)
            self.tabs.setCurrentIndex(0)
    
    def remove_bookmarks(self):
        for item in self.bookmarks_list.selectedItems():
            url = item.data(Qt.ItemDataRole.UserRole)
            if self.bookmarks_manager:
                self.bookmarks_manager.remove_bookmark(url)
        self.refresh_bookmarks()
    
    def add_current_to_bookmarks(self):
        url = self.repo_url.text()
        if url and self.bookmarks_manager:
            self.bookmarks_manager.add_bookmark(url)
            self.statusBar.showMessage("Added to bookmarks!")
            QMessageBox.information(self, "Bookmarked", f"{url} added to bookmarks!")
    
    def show_schedule_dialog(self):
        dialog = ScheduledDownloadDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            schedule = dialog.get_schedule()
            if self.sync_manager:
                self.sync_manager.add_scheduled_sync(
                    schedule['repo_url'], 
                    schedule['type'], 
                    schedule['time_spec']
                )
                self.refresh_scheduled_list()
    
    def refresh_scheduled_list(self):
        self.scheduled_list.clear()
        if self.sync_manager:
            for sync in self.sync_manager.scheduled_syncs:
                item = QListWidgetItem(f"{sync['repo_url']} - {sync['type']} - Next: {sync['next_sync']}")
                self.scheduled_list.addItem(item)
    
    def remove_schedule(self):
        for item in self.scheduled_list.selectedItems():
            # Remove from sync manager
            pass
        self.refresh_scheduled_list()
    
    def run_scheduled_syncs(self):
        """Run scheduled syncs if manager is available"""
        if self.sync_manager:
            results = self.sync_manager.process_scheduled_syncs()
            for res in results:
                if res and res.success:
                    self.notification_manager.show_notification(
                        "Sync Complete", 
                        f"Successfully synced repository"
                    )

    def sync_all_repos(self):
        """Sync all bookmarked repositories"""
        if not self.github_client:
            QMessageBox.warning(self, "Error", "Please authenticate first")
            return
        
        if not self.bookmarks_manager or not self.sync_manager:
            return

        bookmarks = self.bookmarks_manager.get_bookmarks()
        if not bookmarks:
            QMessageBox.information(self, "No Bookmarks", "No bookmarked repositories to sync.")
            return

        self.statusBar.showMessage(f"Syncing {len(bookmarks)} repositories...")
        for b in bookmarks:
            self.sync_manager.execute_sync(b['url'])
        
        QMessageBox.information(self, "Sync Complete", f"Finished syncing {len(bookmarks)} repositories.")
        self.statusBar.showMessage("Sync completed")
    
    def sync_local_repos(self):
        path = self.local_repos_path.text()
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Path does not exist")
            return
        
        if self.sync_manager:
            self.statusBar.showMessage("Syncing local repositories...")
            results = self.sync_manager.sync_local_repos(path)
            
            success_count = sum(1 for r in results if 'result' in r and r['result'].success)
            QMessageBox.information(self, "Sync Complete", 
                                   f"Scanned {len(results)} directories.\n"
                                   f"Successfully synced {success_count} repositories.")
            self.statusBar.showMessage("Local sync completed")
    
    def load_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file with URLs", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, 'r') as f:
                for line in f:
                    url = line.strip()
                    if url:
                        self.batch_list.addItem(url)
    
    def load_recent_repos(self):
        recent_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', 'recent_repos.json'
        )
        if os.path.exists(recent_file):
            try:
                with open(recent_file, 'r') as f:
                    self.recent_repos = json.load(f)
            except:
                self.recent_repos = []
        self.update_recent_combo()
    
    def save_recent_repos(self):
        recent_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', 'recent_repos.json'
        )
        os.makedirs(os.path.dirname(recent_file), exist_ok=True)
        with open(recent_file, 'w') as f:
            json.dump(self.recent_repos, f)
    
    def update_recent_combo(self):
        self.recent_combo.clear()
        for repo in self.recent_repos[:10]:
            self.recent_combo.addItem(repo['name'], repo['url'])
    
    def load_from_recent(self, index):
        url = self.recent_combo.currentData()
        if url:
            self.repo_url.setText(url)
    
    def add_to_recent(self, repo_url, name):
        # Remove if exists
        self.recent_repos = [r for r in self.recent_repos if r['url'] != repo_url]
        # Add to front
        self.recent_repos.insert(0, {'url': repo_url, 'name': name})
        # Keep only last 20
        self.recent_repos = self.recent_repos[:20]
        self.save_recent_repos()
        self.update_recent_combo()
    
    # ============== EXISTING METHODS (simplified for brevity) ==============
    
    def browse_download_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory",
                                                self.download_path.text())
        if path:
            self.download_path.setText(path)
    
    def browse_batch_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory",
                                                self.batch_output_path.text())
        if path:
            self.batch_output_path.setText(path)
    
    def browse_all_repos_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory",
                                                self.all_repos_path.text())
        if path:
            self.all_repos_path.setText(path)
    
    def add_batch_url(self):
        url, ok = QInputDialog.getText(self, "Add Repository", "Enter repository URL:")
        if ok and url:
            self.batch_list.addItem(url)
    
    def remove_batch_urls(self):
        for item in self.batch_list.selectedItems():
            self.batch_list.takeItem(self.batch_list.row(item))
    
    def show_login(self):
        from .gui import LoginDialog
        dialog = LoginDialog(self.user_auth, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_user_id = dialog.authenticated_user_id
            user = self.user_auth.get_user(self.current_user_id)
            self.statusBar.showMessage(f"Logged in as: {user['username']}")
            self.update_github_status()
            self.load_history()
            # Initialize managers
            self.bookmarks_manager = BookmarksManager(self.user_auth, self.current_user_id)
            self.refresh_bookmarks()
            self.sync_manager = SyncManager(self.user_auth, self.github_client)
            self.refresh_scheduled_list()
    
    def logout(self):
        self.current_user_id = None
        self.github_client = None
        self.bookmarks_manager = None
        self.sync_manager = None
        self.statusBar.showMessage("Logged out")
    
    def show_github_auth(self):
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "Please login first")
            return
        from .gui import GitHubAuthDialog
        dialog = GitHubAuthDialog(self.user_auth, self.current_user_id, self)
        dialog.exec()
        self.update_github_status()
    
    def show_settings(self):
        from .gui import SettingsDialog
        dialog = SettingsDialog(self.user_auth, self.current_user_id, self)
        dialog.exec()
    
    def show_about(self):
        QMessageBox.about(self, "About GitHub Repo Downloader",
                         "GitHub Repo Downloader v2.0\n\n"
                         "Enhanced with Dark Theme, CLI Mode, Sync, Scheduling, Bookmarks, and More!\n\n"
                         "Features:\n"
                         "• User account system\n"
                         "• GitHub authentication (PAT/OAuth)\n"
                         "• Single and batch downloads\n"
                         "• Download ALL repos\n"
                         "• Dark/Light theme\n"
                         "• CLI mode\n"
                         "• Repo sync & scheduling\n"
                         "• Bookmarks\n"
                         "• Rate limit compliance")
    
    def show_terms(self):
        QMessageBox.information(self, "GitHub Terms Compliance",
                               "This application complies with GitHub's Terms of Service:\n\n"
                               "• Uses official GitHub API\n"
                               "• Implements rate limiting (80% safety margin)\n"
                               "• Respects 'Retry-After' headers\n"
                               "• Only accesses authorized repositories")
    
    def update_github_status(self):
        if self.current_user_id:
            creds = self.user_auth.get_github_credentials(self.current_user_id)
            if creds and creds['access_token']:
                self.github_client = GitHubAPIClient(creds['access_token'], AuthType.PAT)
                valid, username, name = self.github_client.validate_token()
                if valid:
                    self.statusBar.showMessage(f"GitHub: Connected as {username}")
                else:
                    self.statusBar.showMessage("GitHub: Token invalid")
            else:
                self.statusBar.showMessage("GitHub: Not authenticated")
        else:
            self.statusBar.showMessage("GitHub: Not authenticated")
    
    def update_rate_limit(self):
        if self.github_client:
            rate_info = self.github_client.get_rate_limit()
            if rate_info:
                self.statusBar.showMessage(
                    f"Rate Limit: {rate_info['core'].remaining}/{rate_info['core'].limit} "
                    f"(resets in {rate_info['core'].seconds_until_reset()}s)"
                )
    
    def get_github_token(self):
        if self.current_user_id:
            creds = self.user_auth.get_github_credentials(self.current_user_id)
            if creds:
                return creds['access_token']
        return None
    
    def get_method_from_combo(self, combo):
        index = combo.currentIndex()
        if index == 0:
            return DownloadMethod.GIT_CLONE
        elif index == 1:
            return DownloadMethod.DOWNLOAD_ZIP
        elif index == 2:
            return DownloadMethod.DOWNLOAD_TAR
        return DownloadMethod.GIT_CLONE
    
    def start_single_download(self):
        repo_url = self.repo_url.text()
        if not repo_url:
            QMessageBox.warning(self, "Error", "Please enter a repository URL")
            return
        
        # Handle Selective Download (index 3)
        method_index = self.download_method.currentIndex()
        if method_index == 3:  # Selective Download
            self.show_selective_download_dialog()
            return
        
        output_path = self.download_path.text() or os.path.join(os.path.expanduser("~"), "Downloads")
        method = self.get_method_from_combo(self.download_method)
        branch = self.repo_branch.text() or "main"
        
        token = self.get_github_token()
        self.downloader = GitRepoDownloader(token)
        
        try:
            task = self.downloader.create_download_task(repo_url, output_path, method, branch)
            
            # Add to recent
            self.add_to_recent(repo_url, f"{task.owner}/{task.repo}")
            
            thread = DownloadThread(self.downloader, task.id)
            thread.progress_updated.connect(self.update_download_progress)
            thread.download_complete.connect(self.download_finished)
            thread.start()
            
            self.download_threads[task.id] = thread
            self.refresh_downloads_table()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def show_selective_download_dialog(self):
        """Show dialog for selecting specific files/folders to download"""
        repo_url = self.repo_url.text()
        
        # Parse the URL to get owner and repo
        downloader = GitRepoDownloader()
        owner, repo = downloader.parse_repo_url(repo_url)
        
        if not owner or not repo:
            QMessageBox.warning(self, "Error", "Invalid repository URL")
            return
        
        branch = self.repo_branch.text() or "main"
        
        dialog = SelectiveDownloadDialog(self.github_client, owner, repo, branch, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_paths = dialog.get_selected_paths()
            if selected_paths:
                QMessageBox.information(
                    self, "Selected Files", 
                    f"Selected {len(selected_paths)} items for download.\n\n"
                    "Note: Individual file download is not yet fully implemented.\n"
                    "Please use 'Git Clone' or 'Download ZIP' for now."
                )
            else:
                QMessageBox.information(self, "No Selection", "No files selected.")
    
    def start_batch_download(self):
        count = self.batch_list.count()
        if count == 0:
            QMessageBox.warning(self, "Error", "Please add repositories first")
            return
        
        output_path = self.batch_output_path.text()
        method = self.get_method_from_combo(self.batch_method)
        
        token = self.get_github_token()
        self.downloader = GitRepoDownloader(token)
        
        for i in range(count):
            item = self.batch_list.item(i)
            url = item.text()
            
            try:
                task = self.downloader.create_download_task(url, output_path, method)
                thread = DownloadThread(self.downloader, task.id)
                thread.progress_updated.connect(self.update_download_progress)
                thread.download_complete.connect(self.download_finished)
                thread.start()
                self.download_threads[task.id] = thread
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Invalid URL: {url}")
        
        self.refresh_downloads_table()
    
    def update_download_progress(self, task):
        self.refresh_downloads_table()
    
    def download_finished(self, task_id, success):
        if self.downloader and self.current_user_id:
            task = self.downloader.get_download_status(task_id)
            if task:
                self.user_auth.log_download(
                    self.current_user_id,
                    f"github.com/{task.owner}/{task.repo}",
                    task.repo,
                    os.path.join(task.output_path, task.repo),
                    task.files_downloaded,
                    task.size_bytes,
                    task.status.value
                )
                
                # Show notification
                if self.notification_manager:
                    self.notification_manager.notify_download_complete(
                        f"{task.owner}/{task.repo}", success
                    )
        
        if task_id in self.download_threads:
            del self.download_threads[task_id]
        
        self.refresh_downloads_table()
        self.load_history()
    
    def refresh_downloads_table(self):
        if not self.downloader:
            return
        
        self.downloads_table.setRowCount(0)
        
        for task in self.downloader.get_all_downloads():
            row = self.downloads_table.rowCount()
            self.downloads_table.insertRow(row)
            
            self.downloads_table.setItem(row, 0, QTableWidgetItem(f"{task.owner}/{task.repo}"))
            
            status_item = QTableWidgetItem(task.status.value)
            if task.status == DownloadStatus.COMPLETED:
                status_item.setBackground(QColor(100, 200, 100))
            elif task.status == DownloadStatus.FAILED:
                status_item.setBackground(QColor(200, 100, 100))
            elif task.status == DownloadStatus.IN_PROGRESS:
                status_item.setBackground(QColor(200, 200, 100))
            self.downloads_table.setItem(row, 1, status_item)
            
            progress_bar = QProgressBar()
            progress_bar.setValue(int(task.progress))
            self.downloads_table.setCellWidget(row, 2, progress_bar)
            
            self.downloads_table.setItem(row, 3, QTableWidgetItem(task.current_file))
            self.downloads_table.setItem(row, 4, QTableWidgetItem(
                f"{task.size_bytes / 1024 / 1024:.1f} MB" if task.size_bytes else "-"))
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(lambda checked, tid=task.id: self.cancel_download(tid))
            self.downloads_table.setCellWidget(row, 5, cancel_btn)
    
    def cancel_download(self, task_id):
        if self.downloader:
            self.downloader.cancel_download(task_id)
            self.refresh_downloads_table()
    
    def search_repos(self):
        query = self.search_query.text()
        if not query:
            return
        
        token = self.get_github_token()
        client = GitHubAPIClient(token)
        
        results = client.search_repos(query)
        
        self.search_results.setRowCount(0)
        for repo in results:
            row = self.search_results.rowCount()
            self.search_results.insertRow(row)
            
            self.search_results.setItem(row, 0, QTableWidgetItem(repo['name']))
            self.search_results.setItem(row, 1, QTableWidgetItem(repo['owner']['login']))
            self.search_results.setItem(row, 2, QTableWidgetItem(str(repo['stargazers_count'])))
            self.search_results.setItem(row, 3, QTableWidgetItem(repo.get('description', '')[:50]))
            
            download_btn = QPushButton("⬇️")
            download_btn.clicked.connect(lambda checked, r=repo: self.download_from_search(r))
            self.search_results.setCellWidget(row, 4, download_btn)
    
    def download_from_search(self, repo):
        self.repo_url.setText(repo['html_url'])
        self.tabs.setCurrentIndex(0)
    
    def load_user_repos(self):
        username = self.username_input.text()
        if not username and self.github_client:
            user_info = self.github_client.get_user()
            if user_info:
                username = user_info.get('login')
            else:
                QMessageBox.warning(self, "Error", "Please enter a username")
                return
        
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username")
            return
        
        token = self.get_github_token()
        client = GitHubAPIClient(token)
        
        repos = client.get_user_repos(username)
        self.cached_repos = repos
        
        self.repos_table.setRowCount(0)
        for repo in repos:
            row = self.repos_table.rowCount()
            self.repos_table.insertRow(row)
            
            self.repos_table.setItem(row, 0, QTableWidgetItem(repo['name']))
            self.repos_table.setItem(row, 1, QTableWidgetItem(repo.get('description', '')[:50]))
            self.repos_table.setItem(row, 2, QTableWidgetItem(repo.get('language', 'N/A')))
            self.repos_table.setItem(row, 3, QTableWidgetItem(repo.get('updated_at', '')[:10]))
            
            download_btn = QPushButton("⬇️")
            download_btn.clicked.connect(lambda checked, r=repo: self.download_from_repos(r))
            self.repos_table.setCellWidget(row, 4, download_btn)
        
        self.statusBar.showMessage(f"Loaded {len(repos)} repositories for {username}")
    
    def download_from_repos(self, repo):
        self.repo_url.setText(repo['html_url'])
        self.tabs.setCurrentIndex(0)
    
    def download_all_repos(self):
        if not self.cached_repos:
            QMessageBox.warning(self, "Error", "Please load repositories first")
            return
        
        output_path = self.all_repos_path.text()
        method = self.get_method_from_combo(self.all_repos_method)
        
        token = self.get_github_token()
        self.downloader = GitRepoDownloader(token)
        
        repo_count = len(self.cached_repos)
        confirm = QMessageBox.question(
            self, "Confirm Download All",
            f"Download ALL {repo_count} repositories?\nOutput: {output_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.No:
            return
        
        for repo in self.cached_repos:
            try:
                task = self.downloader.create_download_task(repo['html_url'], output_path, method)
                thread = DownloadThread(self.downloader, task.id)
                thread.progress_updated.connect(self.update_download_progress)
                thread.download_complete.connect(self.download_finished)
                thread.start()
                self.download_threads[task.id] = thread
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Invalid URL: {repo['html_url']}")
        
        self.refresh_downloads_table()
    
    def load_history(self):
        if not self.current_user_id:
            return
        
        history = self.user_auth.get_download_history(self.current_user_id)
        
        self.history_table.setRowCount(0)
        for item in history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(item[3]))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(item[5])[:10]))
            self.history_table.setItem(row, 2, QTableWidgetItem(item[4]))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(item[6])))
            self.history_table.setItem(row, 4, QTableWidgetItem(
                f"{item[7] / 1024 / 1024:.2f} MB" if item[7] else "N/A"))
            self.history_table.setItem(row, 5, QTableWidgetItem(item[8]))
            
            redownload_btn = QPushButton("⬇️")
            redownload_btn.clicked.connect(lambda checked, i=item: self.redownload_history(i))
            self.history_table.setCellWidget(row, 6, redownload_btn)
    
    def redownload_history(self, item):
        self.repo_url.setText(item[2])  # repo_url
        self.tabs.setCurrentIndex(0)
    
    def clear_history(self):
        QMessageBox.information(self, "Clear History", "History clearing not implemented in this version")
    
    def run_cli_mode(self):
        """Run in CLI mode"""
        cli = CLIMode(self.user_auth)
        sys.exit(cli.run())


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Check for CLI mode
    cli_mode = '--cli' in sys.argv or '-c' in sys.argv
    
    window = MainWindow(cli_mode=cli_mode)
    
    if not cli_mode:
        window.show()
        sys.exit(app.exec())
    else:
        return window


if __name__ == '__main__':
    main()
