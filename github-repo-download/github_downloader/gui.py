"""
Main GUI Application for GitHub Repo Downloader
Built with PyQt6
"""
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QTableWidget, QTableWidgetItem, QProgressBar,
                              QTabWidget, QFormLayout, QGroupBox, QComboBox,
                              QCheckBox, QSpinBox, QFileDialog, QMessageBox,
                              QStatusBar, QToolBar, QMenuBar, QMenu, QDialog,
                              QDialogButtonBox, QListWidget, QListWidgetItem,
                              QSplitter, QFrame, QScrollArea, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap, QColor, QPalette

from .user_auth import UserDatabase
from .github_api import GitHubAPIClient, GitHubOAuth, AuthType
from .downloader import GitRepoDownloader, DownloadTask, DownloadStatus, DownloadMethod


class LoginDialog(QDialog):
    """Login/Register dialog"""
    
    def __init__(self, user_auth, parent=None):
        super().__init__(parent)
        self.user_auth = user_auth
        self.authenticated_user_id = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("GitHub Downloader - Login")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
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


class GitHubAuthDialog(QDialog):
    """GitHub authentication dialog"""
    
    def __init__(self, user_auth, user_id, parent=None):
        super().__init__(parent)
        self.user_auth = user_auth
        self.user_id = user_id
        self.github_client = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("GitHub Authentication")
        self.setFixedSize(500, 350)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Tabs for different auth methods
        self.tabs = QTabWidget()
        
        # PAT Authentication
        pat_tab = QWidget()
        pat_layout = QFormLayout()
        
        self.pat_token = QLineEdit()
        self.pat_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.pat_token.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        
        pat_layout.addRow("Personal Access Token:", self.pat_token)
        
        self.test_pat_btn = QPushButton("Test & Save")
        self.test_pat_btn.clicked.connect(self.test_pat)
        pat_layout.addRow("", self.test_pat_btn)
        
        pat_info = QLabel("Create a token at: GitHub Settings → Developer settings → Personal access tokens\n"
                         "Required scopes: repo (full control of private repositories)")
        pat_info.setWordWrap(True)
        pat_layout.addRow("", pat_info)
        
        pat_tab.setLayout(pat_layout)
        self.tabs.addTab(pat_tab, "Personal Access Token")
        
        # OAuth Authentication
        oauth_tab = QWidget()
        oauth_layout = QVBoxLayout()
        
        oauth_info = QLabel("OAuth2 requires setting up a GitHub OAuth App.\n"
                          "For personal use, Personal Access Token is recommended.")
        oauth_info.setWordWrap(True)
        oauth_layout.addWidget(oauth_info)
        
        oauth_layout.addLayout(oauth_layout)
        
        self.oauth_client_id = QLineEdit()
        self.oauth_client_secret = QLineEdit()
        self.oauth_client_secret.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout = QFormLayout()
        form_layout.addRow("Client ID:", self.oauth_client_id)
        form_layout.addRow("Client Secret:", self.oauth_client_secret)
        oauth_layout.addLayout(form_layout)
        
        self.start_oauth_btn = QPushButton("Start OAuth Flow")
        self.start_oauth_btn.clicked.connect(self.start_oauth)
        oauth_layout.addWidget(self.start_oauth_btn)
        
        oauth_tab.setLayout(oauth_layout)
        self.tabs.addTab(oauth_tab, "OAuth2")
        
        layout.addWidget(self.tabs)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Load existing credentials
        self.load_existing_credentials()
    
    def load_existing_credentials(self):
        creds = self.user_auth.get_github_credentials(self.user_id)
        if creds:
            if creds['auth_type'] == 'pat':
                self.status_label.setText(f"Connected as: {creds.get('github_username', 'Unknown')}")
                self.tabs.setTabEnabled(1, False)
            elif creds['auth_type'] == 'oauth':
                self.status_label.setText(f"Connected as: {creds.get('github_username', 'Unknown')}")
                self.tabs.setTabEnabled(0, False)
    
    def test_pat(self):
        token = self.pat_token.text()
        if not token:
            self.status_label.setText("Please enter a token")
            return
        
        self.github_client = GitHubAPIClient(token, AuthType.PAT)
        valid, username, name = self.github_client.validate_token()
        
        if valid:
            self.user_auth.save_github_credentials(
                self.user_id, 'pat', token, username
            )
            self.status_label.setText(f"Connected as: {username} ({name})")
            QMessageBox.information(self, "Success", "Token validated and saved!")
        else:
            self.status_label.setText("Invalid token")
    
    def start_oauth(self):
        client_id = self.oauth_client_id.text()
        client_secret = self.oauth_client_secret.text()
        
        if not client_id or not client_secret:
            self.status_label.setText("Please enter OAuth credentials")
            return
        
        oauth = GitHubOAuth(client_id, client_secret)
        auth_url = oauth.get_authorization_url()
        
        import webbrowser
        webbrowser.open(auth_url)
        
        QMessageBox.information(
            self, "OAuth Started",
            "A browser window has opened for GitHub authorization.\n"
            "After authorizing, copy the code from the redirect URL."
        )
        
        self.status_label.setText("Check browser for authorization")


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, user_auth, user_id, parent=None):
        super().__init__(parent)
        self.user_auth = user_auth
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Download path
        path_group = QGroupBox("Download Location")
        path_layout = QHBoxLayout()
        
        self.download_path = QLineEdit()
        self.download_path.setText(os.path.expanduser("~\\Downloads"))
        path_layout.addWidget(self.download_path)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_btn)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # Default download method
        method_group = QGroupBox("Default Download Method")
        method_layout = QVBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Git Clone (recommended)", "Download ZIP", "Download TAR.gz"])
        method_layout.addWidget(self.method_combo)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # Rate limit settings
        rate_group = QGroupBox("Rate Limit Safety")
        rate_layout = QVBoxLayout()
        
        self.safety_check = QCheckBox("Use safety margin (80% of limit)")
        self.safety_check.setChecked(True)
        rate_layout.addWidget(self.safety_check)
        
        self.wait_check = QCheckBox("Automatically wait when approaching limit")
        self.wait_check.setChecked(True)
        rate_layout.addWidget(self.wait_check)
        
        rate_group.setLayout(rate_layout)
        layout.addWidget(rate_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory", 
                                                self.download_path.text())
        if path:
            self.download_path.setText(path)
    
    def save_settings(self):
        # Save settings to user database
        self.accept()


class DownloadThread(QThread):
    """Thread for downloading repositories"""
    
    progress_updated = pyqtSignal(object)
    download_complete = pyqtSignal(str, bool)
    
    def __init__(self, downloader, task_id):
        super().__init__()
        self.downloader = downloader
        self.task_id = task_id
    
    def run(self):
        def progress_callback(task):
            self.progress_updated.emit(task)
        
        self.downloader.progress_callback = progress_callback
        success = self.downloader.start_download(self.task_id)
        self.download_complete.emit(self.task_id, success)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.user_auth = UserDatabase()
        self.current_user_id = None
        self.github_client = None
        self.downloader = None
        self.download_threads = {}
        self.cached_repos = []
        
        self.init_ui()
        self.show_login()
    
    def init_ui(self):
        self.setWindowTitle("GitHub Repo Downloader")
        self.setMinimumSize(1000, 700)
        
        # Menu bar
        self.create_menu_bar()
        
        # Tool bar
        self.create_toolbar()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Single Download Tab
        self.download_tab = self.create_download_tab()
        self.tabs.addTab(self.download_tab, "Single Download")
        
        # Batch Download Tab
        self.batch_tab = self.create_batch_tab()
        self.tabs.addTab(self.batch_tab, "Batch Download")
        
        # Search Tab
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, "Search")
        
        # My Repos Tab
        self.my_repos_tab = self.create_my_repos_tab()
        self.tabs.addTab(self.my_repos_tab, "My Repositories")
        
        # History Tab
        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, "History")
        
        layout.addWidget(self.tabs)
        
        # Active downloads
        self.active_downloads_group = QGroupBox("Active Downloads")
        downloads_layout = QVBoxLayout()
        
        self.downloads_table = QTableWidget()
        self.downloads_table.setColumnCount(6)
        self.downloads_table.setHorizontalHeaderLabels(
            ["Repository", "Status", "Progress", "Current File", "Speed", "Actions"]
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
        self.rate_timer.start(60000)  # Every minute
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Account menu
        account_menu = menubar.addMenu("Account")
        
        login_action = QAction("Login", self)
        login_action.triggered.connect(self.show_login)
        account_menu.addAction(login_action)
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        account_menu.addAction(logout_action)
        
        account_menu.addSeparator()
        
        github_auth_action = QAction("GitHub Authentication", self)
        github_auth_action.triggered.connect(self.show_github_auth)
        account_menu.addAction(github_auth_action)
        
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
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.show_login)
        toolbar.addWidget(login_btn)
        
        auth_btn = QPushButton("GitHub Auth")
        auth_btn.clicked.connect(self.show_github_auth)
        toolbar.addWidget(auth_btn)
        
        settings_btn = QPushButton("Settings")
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
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_download_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.download_path)
        path_layout.addWidget(self.browse_btn)
        options_layout.addRow("Download to:", path_layout)
        
        self.download_method = QComboBox()
        self.download_method.addItems(["Git Clone", "Download ZIP", "Download TAR.gz"])
        options_layout.addRow("Method:", self.download_method)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Download button
        self.download_btn = QPushButton("Download Repository")
        self.download_btn.setMinimumHeight(40)
        self.download_btn.clicked.connect(self.start_single_download)
        layout.addWidget(self.download_btn)
        
        # Spacer
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_batch_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Input file or list
        input_group = QGroupBox("Repository List")
        input_layout = QVBoxLayout()
        
        self.batch_list = QListWidget()
        self.batch_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        input_layout.addWidget(self.batch_list)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add URL")
        add_btn.clicked.connect(self.add_batch_url)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_batch_urls)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.batch_list.clear)
        btn_layout.addWidget(clear_btn)
        
        input_layout.addLayout(btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Batch options
        batch_options = QGroupBox("Batch Options")
        options_layout = QFormLayout()
        
        self.batch_output_path = QLineEdit()
        self.batch_output_path.setText(os.path.expanduser("~\\Downloads"))
        self.batch_browse_btn = QPushButton("Browse")
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
        self.batch_download_btn = QPushButton("Start Batch Download")
        self.batch_download_btn.setMinimumHeight(40)
        self.batch_download_btn.clicked.connect(self.start_batch_download)
        layout.addWidget(self.batch_download_btn)
        
        tab.setLayout(layout)
        return tab
    
    def create_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Search input
        search_group = QGroupBox("Search Repositories")
        search_layout = QHBoxLayout()
        
        self.search_query = QLineEdit()
        self.search_query.setPlaceholderText("Search GitHub...")
        self.search_query.returnPressed.connect(self.search_repos)
        search_layout.addWidget(self.search_query)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_repos)
        search_layout.addWidget(self.search_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Results
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()
        
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(5)
        self.search_results.setHorizontalHeaderLabels(
            ["Name", "Owner", "Stars", "Description", "Actions"]
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
        
        # User input
        user_group = QGroupBox("User Repositories")
        user_layout = QHBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("GitHub username or leave empty for authenticated user")
        user_layout.addWidget(self.username_input)
        
        self.load_repos_btn = QPushButton("Load Repositories")
        self.load_repos_btn.clicked.connect(self.load_user_repos)
        user_layout.addWidget(self.load_repos_btn)
        
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # Download all options
        all_repos_group = QGroupBox("Download All Repositories")
        all_repos_layout = QVBoxLayout()
        
        all_repos_top_layout = QHBoxLayout()
        
        self.all_repos_path = QLineEdit()
        self.all_repos_path.setText(os.path.expanduser("~\\Downloads"))
        all_repos_top_layout.addWidget(self.all_repos_path)
        
        self.all_repos_browse_btn = QPushButton("Browse")
        self.all_repos_browse_btn.clicked.connect(self.browse_all_repos_path)
        all_repos_top_layout.addWidget(self.all_repos_browse_btn)
        
        all_repos_layout.addLayout(all_repos_top_layout)
        
        all_repos_bottom_layout = QHBoxLayout()
        
        self.all_repos_method = QComboBox()
        self.all_repos_method.addItems(["Git Clone", "Download ZIP", "Download TAR.gz"])
        all_repos_bottom_layout.addWidget(self.all_repos_method)
        
        self.download_all_btn = QPushButton("Download ALL Repositories")
        self.download_all_btn.setMinimumHeight(40)
        self.download_all_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.download_all_btn.clicked.connect(self.download_all_repos)
        all_repos_bottom_layout.addWidget(self.download_all_btn)
        
        self.all_repos_parallel_check = QCheckBox("Parallel (max 3)")
        self.all_repos_parallel_check.setChecked(True)
        all_repos_bottom_layout.addWidget(self.all_repos_parallel_check)
        
        all_repos_layout.addLayout(all_repos_bottom_layout)
        all_repos_group.setLayout(all_repos_layout)
        layout.addWidget(all_repos_group)
        
        # Repos list
        repos_group = QGroupBox("Repositories")
        repos_layout = QVBoxLayout()
        
        self.repos_table = QTableWidget()
        self.repos_table.setColumnCount(5)
        self.repos_table.setHorizontalHeaderLabels(
            ["Name", "Description", "Language", "Updated", "Actions"]
        )
        self.repos_table.horizontalHeader().setStretchLastSection(True)
        repos_layout.addWidget(self.repos_table)
        
        repos_group.setLayout(repos_layout)
        layout.addWidget(repos_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["Repository", "Date", "Path", "Files", "Size", "Status"]
        )
        self.history_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.history_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh History")
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        tab.setLayout(layout)
        return tab
    
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
        from PyQt6.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, "Add Repository", 
                                        "Enter repository URL:")
        if ok and url:
            self.batch_list.addItem(url)
    
    def remove_batch_urls(self):
        for item in self.batch_list.selectedItems():
            self.batch_list.takeItem(self.batch_list.row(item))
    
    def show_login(self):
        dialog = LoginDialog(self.user_auth, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_user_id = dialog.authenticated_user_id
            user = self.user_auth.get_user(self.current_user_id)
            self.statusBar.showMessage(f"Logged in as: {user['username']}")
            self.update_github_status()
            self.load_history()
    
    def logout(self):
        self.current_user_id = None
        self.github_client = None
        self.statusBar.showMessage("Logged out")
    
    def show_github_auth(self):
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "Please login first")
            return
        
        dialog = GitHubAuthDialog(self.user_auth, self.current_user_id, self)
        dialog.exec()
        self.update_github_status()
    
    def show_settings(self):
        dialog = SettingsDialog(self.user_auth, self.current_user_id, self)
        dialog.exec()
    
    def show_about(self):
        QMessageBox.about(self, "About GitHub Repo Downloader",
                         "GitHub Repo Downloader v1.0\n\n"
                         "A Windows application to download and clone "
                         "GitHub repositories with user authentication.\n\n"
                         "Features:\n"
                         "• User account system\n"
                         "• GitHub authentication (PAT/OAuth)\n"
                         "• Single and batch downloads\n"
                         "• Rate limit compliance\n"
                         "• Progress tracking")
    
    def show_terms(self):
        QMessageBox.information(self, "GitHub Terms Compliance",
                               "This application complies with GitHub's Terms of Service:\n\n"
                               "• Uses official GitHub API\n"
                               "• Implements rate limiting (80% safety margin)\n"
                               "• Respects 'Retry-After' headers\n"
                               "• Only accesses authorized repositories\n"
                               "• Does not scrape data\n"
                               "• Does not violate rate limits\n\n"
                               "For private repos, you must have proper authorization.")
    
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
    
    def get_github_token(self) -> str:
        """Get GitHub token from user credentials"""
        if self.current_user_id:
            creds = self.user_auth.get_github_credentials(self.current_user_id)
            if creds:
                return creds['access_token']
        return None
    
    def get_method_from_combo(self, combo: QComboBox) -> DownloadMethod:
        """Convert combo index to DownloadMethod"""
        index = combo.currentIndex()
        if index == 0:
            return DownloadMethod.GIT_CLONE
        elif index == 1:
            return DownloadMethod.DOWNLOAD_ZIP
        else:
            return DownloadMethod.DOWNLOAD_TAR
    
    def start_single_download(self):
        repo_url = self.repo_url.text()
        if not repo_url:
            QMessageBox.warning(self, "Error", "Please enter a repository URL")
            return
        
        output_path = self.download_path.text()
        if not output_path:
            output_path = os.path.expanduser("~\\Downloads")
        
        method = self.get_method_from_combo(self.download_method)
        branch = self.repo_branch.text() if self.repo_branch.text() else "main"
        
        token = self.get_github_token()
        
        self.downloader = GitRepoDownloader(token)
        try:
            task = self.downloader.create_download_task(
                repo_url, output_path, method, branch
            )
            
            # Start download thread
            thread = DownloadThread(self.downloader, task.id)
            thread.progress_updated.connect(self.update_download_progress)
            thread.download_complete.connect(self.download_finished)
            thread.start()
            
            self.download_threads[task.id] = thread
            self.refresh_downloads_table()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
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
    
    def update_download_progress(self, task: DownloadTask):
        self.refresh_downloads_table()
    
    def download_finished(self, task_id: str, success: bool):
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
            
            # Repository
            self.downloads_table.setItem(row, 0, QTableWidgetItem(
                f"{task.owner}/{task.repo}"))
            
            # Status
            status_item = QTableWidgetItem(task.status.value)
            if task.status == DownloadStatus.COMPLETED:
                status_item.setBackground(QColor(200, 255, 200))
            elif task.status == DownloadStatus.FAILED:
                status_item.setBackground(QColor(255, 200, 200))
            elif task.status == DownloadStatus.IN_PROGRESS:
                status_item.setBackground(QColor(255, 255, 200))
            self.downloads_table.setItem(row, 1, status_item)
            
            # Progress
            progress_bar = QProgressBar()
            progress_bar.setValue(int(task.progress))
            self.downloads_table.setCellWidget(row, 2, progress_bar)
            
            # Current file
            self.downloads_table.setItem(row, 3, QTableWidgetItem(task.current_file))
            
            # Actions
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(lambda checked, tid=task.id: self.cancel_download(tid))
            self.downloads_table.setCellWidget(row, 5, cancel_btn)
    
    def cancel_download(self, task_id: str):
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
            self.search_results.setItem(row, 3, QTableWidgetItem(
                repo.get('description', '')[:50]))
            
            download_btn = QPushButton("Download")
            download_btn.clicked.connect(lambda checked, r=repo: self.download_from_search(r))
            self.search_results.setCellWidget(row, 4, download_btn)
    
    def download_from_search(self, repo):
        url = repo['html_url']
        self.repo_url.setText(url)
        self.tabs.setCurrentIndex(0)
    
    def load_user_repos(self):
        username = self.username_input.text()
        if not username:
            # Use authenticated user info
            if self.github_client:
                user_info = self.github_client.get_user()
                if user_info:
                    username = user_info.get('login')
                else:
                    QMessageBox.warning(self, "Error", "Please enter a username or authenticate first")
                    return
            else:
                QMessageBox.warning(self, "Error", "Please enter a username or authenticate with GitHub")
                return
        
        token = self.get_github_token()
        client = GitHubAPIClient(token)
        
        repos = client.get_user_repos(username)
        self.cached_repos = repos  # Cache for download all
        
        self.repos_table.setRowCount(0)
        for repo in repos:
            row = self.repos_table.rowCount()
            self.repos_table.insertRow(row)
            
            self.repos_table.setItem(row, 0, QTableWidgetItem(repo['name']))
            self.repos_table.setItem(row, 1, QTableWidgetItem(
                repo.get('description', '')[:50]))
            self.repos_table.setItem(row, 2, QTableWidgetItem(
                repo.get('language', 'N/A')))
            self.repos_table.setItem(row, 3, QTableWidgetItem(
                repo.get('updated_at', '')[:10]))
            
            download_btn = QPushButton("Download")
            download_btn.clicked.connect(lambda checked, r=repo: self.download_from_repos(r))
            self.repos_table.setCellWidget(row, 4, download_btn)
        
        self.statusBar.showMessage(f"Loaded {len(repos)} repositories for {username}")
    
    def download_all_repos(self):
        """Download ALL repositories for the user"""
        if not hasattr(self, 'cached_repos') or not self.cached_repos:
            QMessageBox.warning(self, "Error", "Please load repositories first")
            return
        
        output_path = self.all_repos_path.text()
        if not output_path:
            output_path = os.path.expanduser("~\\Downloads")
        
        method = self.get_method_from_combo(self.all_repos_method)
        
        token = self.get_github_token()
        self.downloader = GitRepoDownloader(token)
        
        repo_count = len(self.cached_repos)
        confirm = QMessageBox.question(
            self, "Confirm Download All",
            f"Are you sure you want to download ALL {repo_count} repositories?\n\n"
            f"Output folder: {output_path}\n"
            f"Method: {method.value}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.No:
            return
        
        # Show warning about rate limits
        if repo_count > 50 and not token:
            QMessageBox.warning(
                self, "Rate Limit Warning",
                f"You are about to download {repo_count} repos without authentication.\n"
                f"This may hit rate limits. Consider adding a GitHub token."
            )
        
        total_repos = len(self.cached_repos)
        self.statusBar.showMessage(f"Starting download of {total_repos} repositories...")
        
        for i, repo in enumerate(self.cached_repos):
            try:
                task = self.downloader.create_download_task(
                    repo['html_url'], output_path, method
                )
                
                thread = DownloadThread(self.downloader, task.id)
                thread.progress_updated.connect(self.update_download_progress)
                thread.download_complete.connect(self.download_finished)
                thread.start()
                
                self.download_threads[task.id] = thread
                
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Invalid URL: {repo['html_url']}")
        
        self.refresh_downloads_table()
    
    def download_from_repos(self, repo):
        url = repo['html_url']
        self.repo_url.setText(url)
        self.tabs.setCurrentIndex(0)
    
    def load_history(self):
        if not self.current_user_id:
            return
        
        history = self.user_auth.get_download_history(self.current_user_id)
        
        self.history_table.setRowCount(0)
        for item in history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(item[3]))  # repo_name
            self.history_table.setItem(row, 1, QTableWidgetItem(str(item[5])[:10]))  # date
            self.history_table.setItem(row, 2, QTableWidgetItem(item[4]))  # path
            self.history_table.setItem(row, 3, QTableWidgetItem(str(item[6])))  # files
            self.history_table.setItem(row, 4, QTableWidgetItem(
                f"{item[7] / 1024 / 1024:.2f} MB" if item[7] else "N/A"))
            self.history_table.setItem(row, 5, QTableWidgetItem(item[8]))  # status


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
