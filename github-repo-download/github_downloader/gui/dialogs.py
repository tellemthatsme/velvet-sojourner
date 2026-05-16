import os
import webbrowser
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTabWidget, QFormLayout, 
                             QComboBox, QCheckBox, QDialogButtonBox, 
                             QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from ..github_api import GitHubAPIClient, GitHubOAuth, AuthType

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

from PyQt6.QtWidgets import QWidget # Needed for tab pages

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
        pat_info = QLabel("Create a token at: GitHub Settings → Developer settings → Personal access tokens")
        pat_info.setWordWrap(True)
        pat_layout.addRow("", pat_info)
        pat_tab.setLayout(pat_layout)
        self.tabs.addTab(pat_tab, "Personal Access Token")
        
        # OAuth Authentication
        oauth_tab = QWidget()
        oauth_layout = QVBoxLayout()
        oauth_info = QLabel("OAuth2 requires setting up a GitHub OAuth App.")
        oauth_info.setWordWrap(True)
        oauth_layout.addWidget(oauth_info)
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
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.load_existing_credentials()
    
    def load_existing_credentials(self):
        creds = self.user_auth.get_github_credentials(self.user_id)
        if creds:
            self.status_label.setText(f"Connected as: {creds.get('github_username', 'Unknown')}")
    
    def test_pat(self):
        token = self.pat_token.text()
        if not token:
            self.status_label.setText("Please enter a token")
            return
        self.github_client = GitHubAPIClient(token, AuthType.PAT)
        valid, username, name = self.github_client.validate_token()
        if valid:
            self.user_auth.save_github_credentials(self.user_id, 'pat', token, username)
            self.status_label.setText(f"Connected as: {username}")
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
        webbrowser.open(auth_url)
        QMessageBox.information(self, "OAuth Started", "Check your browser.")

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
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", self.download_path.text())
        if path: self.download_path.setText(path)
    
    def save_settings(self):
        self.accept()

class SelectiveDownloadDialog(QDialog):
    """Dialog for selecting specific files/folders to download"""
    
    def __init__(self, github_client, owner, repo, branch="main", parent=None):
        super().__init__(parent)
        self.github_client = github_client
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.selected_paths = set()
        self.init_ui()
        self.load_repo_tree()
    
    def init_ui(self):
        self.setWindowTitle(f"Select Files - {self.owner}/{self.repo}")
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size"])
        self.tree.setColumnWidth(0, 300)
        self.tree.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.tree)
        self.info_label = QLabel("Select files/folders to download")
        layout.addWidget(self.info_label)
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        download_btn = QPushButton("Download Selected")
        download_btn.clicked.connect(self.accept)
        button_layout.addWidget(download_btn)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_repo_tree(self):
        self.tree.clear()
        if not self.github_client: return
        tree_data = self.github_client.get_repo_tree(self.owner, self.repo, recursive=True)
        if tree_data and 'tree' in tree_data:
            self.build_tree(tree_data['tree'])
    
    def build_tree(self, items):
        self.tree_items = {}
        for item in items:
            path = item['path']
            parts = path.split('/')
            parent = self.tree_items.get('/'.join(parts[:-1]))
            tree_item = QTreeWidgetItem([parts[-1], item['type'], str(item.get('size', '-'))])
            tree_item.setData(0, Qt.ItemDataRole.UserRole, path)
            tree_item.setCheckState(0, Qt.CheckState.Unchecked)
            if parent: parent.addChild(tree_item)
            else: self.tree.addTopLevelItem(tree_item)
            self.tree_items[path] = tree_item
    
    def on_item_changed(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if item.checkState(0) == Qt.CheckState.Checked: self.selected_paths.add(path)
        else: self.selected_paths.discard(path)
        self.info_label.setText(f"Selected: {len(self.selected_paths)} items")

    def select_all(self):
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setCheckState(0, Qt.CheckState.Checked)

    def get_selected_paths(self):
        return list(self.selected_paths)

class ScheduledDownloadDialog(QDialog):
    """Dialog for scheduling downloads"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("Schedule Download")
        layout = QFormLayout()
        self.repo_url = QLineEdit()
        layout.addRow("Repo URL:", self.repo_url)
        self.schedule_type = QComboBox()
        self.schedule_type.addItems(["Hourly", "Daily", "Weekly"])
        layout.addRow("Schedule:", self.schedule_type)
        self.time_input = QLineEdit()
        layout.addRow("Time (HH:MM):", self.time_input)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow("", button_box)
        self.setLayout(layout)
    def get_schedule(self):
        return {
            'repo_url': self.repo_url.text(),
            'type': self.schedule_type.currentText().lower(),
            'time_spec': self.time_input.text()
        }

from PyQt6.QtWidgets import QGroupBox # Needed for SettingsDialog
