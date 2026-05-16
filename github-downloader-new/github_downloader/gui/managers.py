import os
import json
import time
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QMainWindow, QApplication, QStyle, 
                             QSystemTrayIcon, QMessageBox)
from PyQt6.QtGui import QPalette, QColor, QAction, QIcon
from PyQt6.QtCore import Qt

class ThemeManager:
    """Manages light and dark themes"""
    
    DARK_PALETTE = """
    QWidget {
        background-color: #2d2d2d;
        color: #e0e0e0;
        font-family: Segoe UI, Arial;
        font-size: 14px;
    }
    QMainWindow, QDialog {
        background-color: #252525;
    }
    QGroupBox {
        border: 1px solid #444;
        border-radius: 5px;
        margin-top: 20px;
        padding-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }
    QLineEdit, QComboBox, QSpinBox, QDateTimeEdit {
        background-color: #3d3d3d;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 5px;
        color: white;
    }
    QPushButton {
        background-color: #4a4a4a;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 8px 15px;
        color: white;
    }
    QPushButton:hover {
        background-color: #5a5a5a;
    }
    QPushButton:pressed {
        background-color: #3a3a3a;
    }
    QTabWidget::pane {
        border: 1px solid #444;
    }
    QTabBar::tab {
        background-color: #333;
        padding: 10px 20px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #444;
        border-bottom: 2px solid #0078d7;
    }
    QTableWidget {
        background-color: #333;
        gridline-color: #444;
        border: 1px solid #444;
        color: #e0e0e0;
    }
    QHeaderView::section {
        background-color: #444;
        padding: 4px;
        border: 1px solid #555;
        color: white;
    }
    QProgressBar {
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
        background-color: #333;
    }
    QProgressBar::chunk {
        background-color: #0078d7;
        width: 10px;
    }
    QStatusBar {
        background-color: #252525;
        color: #aaa;
    }
    """
    
    LIGHT_PALETTE = """
    QTableWidget, QTreeWidget {
        background-color: white;
        gridline-color: #ddd;
        border: 1px solid #ccc;
    }
    """
    
    def __init__(self):
        self.is_dark = False

    def apply_theme(self, app, dark=True):
        if dark:
            app.setStyleSheet(self.DARK_PALETTE)
            self.is_dark = True
        else:
            app.setStyleSheet(self.LIGHT_PALETTE)
            self.is_dark = False

    def toggle_theme(self, app):
        self.apply_theme(app, not self.is_dark)
        return self.is_dark

class NotificationManager:
    """System tray notifications"""
    
    def __init__(self, window):
        self.window = window
        self.tray_icon = QSystemTrayIcon(window)
        
        # Set tray icon (using a standard icon for now)
        icon = window.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.show()

    def show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show a system tray notification"""
        self.tray_icon.showMessage(title, message, icon, 5000)

    def notify_download_complete(self, repo_name, success=True):
        if success:
            self.show_notification("Download Complete", 
                                  f"Successfully downloaded {repo_name}",
                                  QSystemTrayIcon.MessageIcon.Information)
        else:
            self.show_notification("Download Failed", 
                                  f"Failed to download {repo_name}",
                                  QSystemTrayIcon.MessageIcon.Critical)

from ..incremental_sync import IncrementalDownloader, SyncStrategy

class SyncManager:
    """Manages repository synchronization"""
    
    def __init__(self, user_auth, github_client, output_base=None):
        self.user_auth = user_auth
        self.github_client = github_client
        self.output_base = output_base or os.path.expanduser("~\\Downloads")
        self.incremental_downloader = IncrementalDownloader(self.output_base)
        self.scheduled_syncs = []

    def add_scheduled_sync(self, repo_url, schedule_type, time_spec):
        """Add a scheduled sync"""
        next_sync = self.calculate_next_sync(schedule_type, time_spec)
        sync = {
            'repo_url': repo_url,
            'type': schedule_type,
            'time_spec': time_spec,
            'next_sync': next_sync
        }
        self.scheduled_syncs.append(sync)
        return sync

    def calculate_next_sync(self, schedule_type, time_spec):
        """Calculate next sync time"""
        now = datetime.now()
        if schedule_type == 'hourly':
            return now + timedelta(hours=1)
        elif schedule_type == 'daily':
            try:
                h, m = map(int, time_spec.split(':'))
                next_sync = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if next_sync <= now:
                    next_sync += timedelta(days=1)
                return next_sync
            except:
                return now + timedelta(days=1)
        elif schedule_type == 'weekly':
            return now + timedelta(days=7)
        return now + timedelta(hours=24)

    def process_scheduled_syncs(self):
        """Check and execute scheduled syncs"""
        now = datetime.now()
        results = []
        for sync in self.scheduled_syncs:
            if now >= sync['next_sync']:
                res = self.execute_sync(sync['repo_url'])
                results.append(res)
                sync['next_sync'] = self.calculate_next_sync(sync['type'], sync['time_spec'])
        return results

    def execute_sync(self, repo_url, strategy=SyncStrategy.SMART):
        """Execute a sync for a repository"""
        token = self.github_client.token if self.github_client else None
        result = self.incremental_downloader.sync_repository(
            repo_url, 
            token=token,
            strategy=strategy
        )
        return result

    def sync_local_repos(self, repos_path=None):
        """Sync all local repositories found in the path"""
        target_path = repos_path or self.output_base
        results = []
        if not os.path.exists(target_path):
            return results
        
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            if os.path.isdir(os.path.join(item_path, '.git')):
                # Attempt to find the origin URL
                try:
                    import subprocess
                    url_res = subprocess.run(
                        ['git', 'remote', 'get-url', 'origin'],
                        cwd=item_path, 
                        capture_output=True, 
                        text=True
                    )
                    if url_res.returncode == 0:
                        repo_url = url_res.stdout.strip()
                        sync_res = self.execute_sync(repo_url)
                        results.append({'repo': item, 'result': sync_res})
                except Exception as e:
                    results.append({'repo': item, 'error': str(e)})
        return results

class BookmarksManager:
    """Manages repository bookmarks"""
    
    def __init__(self, user_auth, user_id):
        self.user_auth = user_auth
        self.user_id = user_id
        self.bookmarks = self.load_bookmarks()

    def load_bookmarks(self):
        # In a real app, this would be in the database
        bookmarks_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', f'bookmarks_{self.user_id}.json'
        )
        if os.path.exists(bookmarks_file):
            try:
                with open(bookmarks_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_bookmarks(self):
        bookmarks_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', f'bookmarks_{self.user_id}.json'
        )
        os.makedirs(os.path.dirname(bookmarks_file), exist_ok=True)
        with open(bookmarks_file, 'w') as f:
            json.dump(self.bookmarks, f)

    def add_bookmark(self, repo_url, name=None, tags=None):
        if not name:
            name = repo_url.split('/')[-1]
        
        # Check if already exists
        self.bookmarks = [b for b in self.bookmarks if b['url'] != repo_url]
        
        self.bookmarks.append({
            'url': repo_url,
            'name': name,
            'tags': tags or [],
            'added_at': datetime.now().isoformat()
        })
        self.save_bookmarks()

    def remove_bookmark(self, repo_url):
        self.bookmarks = [b for b in self.bookmarks if b['url'] != repo_url]
        self.save_bookmarks()

    def get_bookmarks(self):
        return self.bookmarks

    def search_bookmarks(self, query):
        query = query.lower()
        return [b for b in self.bookmarks if query in b['name'].lower() or query in b['url'].lower()]

class MultiAccountManager:
    """Manages multiple GitHub accounts"""
    
    def __init__(self, user_auth):
        self.user_auth = user_auth
        self.active_account = None
        self.accounts = self.load_accounts()

    def load_accounts(self):
        """Load saved accounts"""
        # This would ideally come from the database
        accounts_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', 'accounts.json'
        )
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_accounts(self):
        accounts_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', 'accounts.json'
        )
        os.makedirs(os.path.dirname(accounts_file), exist_ok=True)
        with open(accounts_file, 'w') as f:
            json.dump(self.accounts, f)

    def add_account(self, name, token, username):
        """Add a new account"""
        self.accounts = [a for a in self.accounts if a['username'] != username]
        self.accounts.append({
            'name': name,
            'token': token,
            'username': username,
            'added_at': datetime.now().isoformat()
        })
        self.save_accounts()

    def switch_account(self, account_index):
        if 0 <= account_index < len(self.accounts):
            self.active_account = self.accounts[account_index]
            return True
        return False

    def get_active_account(self):
        return self.active_account

    def remove_account(self, account_index):
        if 0 <= account_index < len(self.accounts):
            self.accounts.pop(account_index)
            self.save_accounts()
