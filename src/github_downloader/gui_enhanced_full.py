# GitHub Repo Downloader v3.3.0 - Enhanced GUI
"""
Self-contained Enhanced GUI with Rate Limit, Multi-Account, Git Operations,
Matrix Background Effect & Full Repo Management.

Features:
- GitHub API Rate Limit Management (compliant with GitHub policies)
- Multiple Account Support with Easy Switching
- Token Validation (async, thread-safe) + OAuth Device Flow
- Download ALL user repos from ALL accounts (public + private)
- Download Starred repos with topic display
- Drag & Drop for repos
- System Tray with proper quit
- Download Queue with real git cloning
- Update existing repos (git pull)
- Push Changes (stage, commit, push)
- Search GitHub repos by keyword & topics
- Branch/tag selection & shallow clone
- Repo info preview (stars, description, language, license, topics)
- Dark/Light mode toggle + Matrix background effect
- Settings persistence to %APPDATA%
- Keyboard shortcuts
- User-Agent & API versioning headers for GitHub compliance
- GitHub Enterprise Support
- Scheduled Downloads
- Check All Repos for Updates
"""

import sys
import os
import json
import time
import subprocess
import zipfile
import tarfile
import platform
from datetime import datetime, timedelta


def debug_log(message: str):
    """Write debug message to log file."""
    try:
        log_dir = os.path.join(os.path.expandvars("%APPDATA%"), "GitHubDownloader")
        log_file = os.path.join(log_dir, "debug.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except Exception:
        pass  # Ignore logging errors


CREATE_NO_WINDOW = 0x08000000 if platform.system() == "Windows" else 0
from typing import Optional, Tuple, Dict, List
import re

from github_downloader.backup_worker import BackupWorker

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QLineEdit,
    QProgressBar,
    QTextEdit,
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QListWidgetItem,
    QComboBox,
    QTabWidget,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStyle,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QInputDialog,
    QScrollArea,
)
from PyQt6.QtGui import (
    QAction,
    QDragEnterEvent,
    QDropEvent,
    QIcon,
    QKeySequence,
    QShortcut,
    QColor,
    QFont,
    QPainter,
    QPen,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl, QRect

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
APP_NAME = "GitHubDownloader"
VERSION = "3.3.0"
APPDATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
SETTINGS_FILE = os.path.join(APPDATA_DIR, "settings.json")
ACCOUNTS_FILE = os.path.join(APPDATA_DIR, "accounts.json")
os.makedirs(APPDATA_DIR, exist_ok=True)

GITHUB_API_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

APP_USER_AGENT = f"{APP_NAME}/{VERSION} (Windows; +https://github.com)"


def github_headers(token: Optional[str] = None) -> dict:
    headers = dict(GITHUB_API_HEADERS)
    headers["User-Agent"] = APP_USER_AGENT
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def get_api_base_url(enterprise_url: str = "") -> str:
    """Get the API base URL - either GitHub Enterprise or standard GitHub"""
    if enterprise_url:
        return enterprise_url.rstrip("/")
    return "https://api.github.com"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------
class DownloadTask:
    def __init__(
        self,
        repo_url: str,
        output_dir: str = None,
        account_id: str = None,
        branch: str = None,
        shallow: bool = False,
        submodules: bool = False,
        clone_type: int = 0,
        account_token: str = None,
    ):
        self.repo_url = repo_url
        self.output_dir = output_dir or os.path.join(
            os.path.expanduser("~"), "Downloads", "GitHubRepos"
        )
        self.account_id = account_id
        self.account_token = account_token
        self.branch = branch
        self.shallow = shallow
        self.submodules = submodules
        self.clone_type = clone_type
        self.status = "pending"
        self.progress = 0
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.retry_count = 0
        self.max_retries = 3


# ---------------------------------------------------------------------------
# Rate Limit Manager (GitHub-compliant)
# ---------------------------------------------------------------------------
class RateLimitManager:
    REMAINING_WARNING = 10
    REMAINING_CRITICAL = 5

    def __init__(self):
        self.accounts: Dict[str, dict] = {}
        self.current_account: Optional[str] = None
        self.cooldown_until: Optional[float] = None

    def add_account(self, account_id: str, token: str, username: str = ""):
        self.accounts[account_id] = {
            "token": token,
            "remaining": 5000,
            "reset": time.time() + 3600,
            "name": username or account_id,
        }
        if not self.current_account:
            self.current_account = account_id

    def remove_account(self, account_id: str):
        self.accounts.pop(account_id, None)
        if self.current_account == account_id:
            self.current_account = next(iter(self.accounts), None)

    def switch_account(self, account_id: str) -> bool:
        if account_id in self.accounts:
            self.current_account = account_id
            return True
        return False

    def get_current_token(self) -> Optional[str]:
        if self.current_account and self.current_account in self.accounts:
            return self.accounts[self.current_account]["token"]
        return None

    def can_make_request(self) -> Tuple[bool, str]:
        if not self.current_account:
            return False, "No account configured"
        account = self.accounts.get(self.current_account)
        if not account:
            return False, "Account not found"
        if self.cooldown_until and time.time() < self.cooldown_until:
            return (
                False,
                f"In cooldown: {int(self.cooldown_until - time.time())}s remaining",
            )
        if account["remaining"] <= 0:
            reset_time = datetime.fromtimestamp(account["reset"])
            return False, f"Rate limited until {reset_time.strftime('%H:%M:%S')}"
        if account["remaining"] < self.REMAINING_WARNING:
            return True, f"Low rate limit: {account['remaining']} remaining"
        return True, "OK"

    def record_request(self, used: int = 1):
        if self.current_account and self.current_account in self.accounts:
            self.accounts[self.current_account]["remaining"] -= used

    def update_rate_limit(self, remaining: int, reset: int):
        if self.current_account and self.current_account in self.accounts:
            self.accounts[self.current_account]["remaining"] = remaining
            self.accounts[self.current_account]["reset"] = reset

    def handle_rate_limit_response(self, resp):
        if resp.status_code == 403 or resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                self.cooldown_until = time.time() + int(retry_after)
            reset_epoch = resp.headers.get("X-RateLimit-Reset")
            if reset_epoch:
                self.update_rate_limit(0, int(reset_epoch))
            remaining = resp.headers.get("X-RateLimit-Remaining")
            if remaining:
                self.update_rate_limit(
                    int(remaining), int(reset_epoch or time.time() + 3600)
                )

    def auto_switch_to_available(self) -> bool:
        for acc_id, acc in self.accounts.items():
            if acc["remaining"] > 0 and acc_id != self.current_account:
                self.current_account = acc_id
                return True
        return False

    def get_status(self) -> dict:
        status = {"current": self.current_account, "accounts": {}}
        for acc_id, acc in self.accounts.items():
            remaining = acc["remaining"]
            reset_time = datetime.fromtimestamp(acc["reset"])
            status["accounts"][acc_id] = {
                "remaining": remaining,
                "reset": reset_time.strftime("%H:%M:%S"),
                "is_current": acc_id == self.current_account,
                "name": acc.get("name", acc_id),
                "status": (
                    "OK"
                    if remaining > 50
                    else ("Low" if remaining > 10 else "Critical")
                ),
            }
        return status


# ---------------------------------------------------------------------------
# Account Manager
# ---------------------------------------------------------------------------
class AccountManager:
    def __init__(self):
        self.accounts: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, "r") as f:
                    self.accounts = json.load(f)
            except Exception:
                self.accounts = {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(ACCOUNTS_FILE), exist_ok=True)
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(self.accounts, f, indent=2)
        except Exception as e:
            print(f"[AccountManager] ERROR saving accounts: {e}")

    def add_account(self, account_id: str, token: str, username: str = ""):
        self.accounts[account_id] = {
            "token": token,
            "username": username,
            "added_at": datetime.now().isoformat(),
        }
        self._save()

    def remove_account(self, account_id: str):
        self.accounts.pop(account_id, None)
        self._save()

    def get_token(self, account_id: str) -> Optional[str]:
        return self.accounts.get(account_id, {}).get("token")

    def list_accounts(self) -> List[dict]:
        return [
            {"id": aid, "username": acc.get("username", aid), **acc}
            for aid, acc in self.accounts.items()
        ]


# ---------------------------------------------------------------------------
# Token Validation (thread-safe via Qt signals)
# ---------------------------------------------------------------------------
class TokenValidator(QThread):
    result_ready = pyqtSignal(str, bool, dict)
    error_occurred = pyqtSignal(str)
    results_ready = pyqtSignal(list)

    def __init__(
        self,
        token: str,
        account_id: str = "",
        api_url: str = "",
        repo_type: str = "all",
    ):
        super().__init__()
        self.token = token
        self.account_id = account_id
        self.api_url = api_url or get_api_base_url()
        self.repo_type = repo_type

    def _check_token_scopes(self) -> Tuple[bool, str, List[str]]:
        """Check token scopes and return (has_repo_scope, message, scopes_list)"""
        if not HAS_REQUESTS:
            return False, "requests library not available", []
        try:
            headers = github_headers(self.token)
            resp = requests.get(f"{self.api_url}/user", headers=headers, timeout=10)
            
            # Get scopes from response headers
            scopes_header = resp.headers.get("X-OAuth-Scopes", "")
            scopes = [s.strip() for s in scopes_header.split(",") if s.strip()]
            
            if resp.status_code != 200:
                return False, f"Token validation failed: HTTP {resp.status_code}", scopes
            
            has_repo_scope = "repo" in scopes or "repo:status" in scopes
            
            if not scopes:
                return False, "Token has NO scopes assigned! Please regenerate with 'repo' scope.", []
            
            if not has_repo_scope:
                return False, f"Token missing 'repo' scope! Current scopes: {', '.join(scopes)}. Please regenerate with 'repo' scope for private repository access.", scopes
            
            return True, f"Token valid with scopes: {', '.join(scopes)}", scopes
            
        except Exception as e:
            return False, f"Scope check failed: {str(e)}", []

    def run(self):
        if not HAS_REQUESTS:
            self.error_occurred.emit("requests library not available")
            return
        try:
            # First check token scopes
            is_valid, scope_msg, scopes = self._check_token_scopes()
            debug_log(f"TokenValidator [{self.account_id}]: {scope_msg}")
            
            if not is_valid:
                self.error_occurred.emit(f"TOKEN SCOPE ERROR: {scope_msg}\n\nTo fix:\n1. Go to github.com/settings/tokens\n2. Generate new Classic token\n3. Check 'repo' scope\n4. Update in app")
                return

            headers = github_headers(self.token)
            
            # Get authenticated user info
            user_resp = requests.get(f"{self.api_url}/user", headers=headers, timeout=10)
            user_info = user_resp.json() if user_resp.status_code == 200 else {}
            username = user_info.get("login", self.account_id)
            total_private_repos = user_info.get("total_private_repos", 0)
            total_public_repos = user_info.get("public_repos", 0)
            
            debug_log(f"TokenValidator [{self.account_id}]: User {username} - Public: {total_public_repos}, Private: {total_private_repos}")
            
            if self.repo_type == "starred":
                url = f"{self.api_url}/user/starred"
                params = {"per_page": 100, "sort": "created"}
            else:
                url = f"{self.api_url}/user/repos"
                params = {"per_page": 100, "sort": "updated", "type": self.repo_type}

            all_repos = []
            page = 1
            private_count = 0
            public_count = 0
            
            while True:
                params["page"] = page
                response = requests.get(url, headers=headers, params=params, timeout=15)
                if response.status_code != 200:
                    self.error_occurred.emit(f"API error: {response.status_code}")
                    return
                items = response.json()
                if not items:
                    break
                for item in items:
                    is_private = item.get("private", False)
                    if is_private:
                        private_count += 1
                    else:
                        public_count += 1
                    
                    all_repos.append(
                        {
                            "full_name": item.get("full_name", ""),
                            "clone_url": item.get("clone_url", ""),
                            "ssh_url": item.get("ssh_url", ""),
                            "description": item.get("description", "") or "",
                            "stars": item.get("stargazers_count", 0),
                            "language": item.get("language", "") or "",
                            "default_branch": item.get("default_branch", "main"),
                            "private": is_private,
                            "fork": item.get("fork", False),
                            "topics": item.get("topics", []),
                            "html_url": item.get("html_url", ""),
                            "size_kb": item.get("size", 0),
                        }
                    )
                if len(items) < 100:
                    break
                page += 1

            debug_log(f"TokenValidator [{self.account_id}]: Fetched {len(all_repos)} repos (Public: {public_count}, Private: {private_count})")
            
            # Warn if private repos expected but none found
            if total_private_repos > 0 and private_count == 0:
                debug_log(f"WARNING [{self.account_id}]: User has {total_private_repos} private repos but none were fetched. Token may lack 'repo' scope.")

            self.result_ready.emit(self.account_id, True, {
                "repos": all_repos,
                "username": username,
                "public_count": public_count,
                "private_count": private_count,
                "scopes": scopes
            })
            self.results_ready.emit(all_repos)
        except requests.exceptions.Timeout:
            self.error_occurred.emit("Connection timeout")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Network error - check connection")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")


# ---------------------------------------------------------------------------
# OAuth Device Flow Worker (thread-safe)
# ---------------------------------------------------------------------------
class OAuthDeviceFlowWorker(QThread):
    code_ready = pyqtSignal(str, str)  # (user_code, verification_uri)
    token_ready = pyqtSignal(str, str)  # (token, username)
    error_occurred = pyqtSignal(str)

    CLIENT_ID = "Ov23li5f0GprGH2YQlGJ"  # Public app placeholder - user should replace

    def __init__(self, client_id: str = ""):
        super().__init__()
        self.client_id = client_id or self.CLIENT_ID
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        if not HAS_REQUESTS:
            self.error_occurred.emit("requests library not available")
            return
        try:
            resp = requests.post(
                "https://github.com/login/device/code",
                data={"client_id": self.client_id, "scope": "repo read:user"},
                headers={"Accept": "application/json"},
                timeout=15,
            )
            if resp.status_code != 200:
                self.error_occurred.emit(f"Device flow init failed: {resp.status_code}")
                return
            data = resp.json()
            device_code = data.get("device_code", "")
            user_code = data.get("user_code", "")
            verify_uri = data.get("verification_uri", "")
            interval = data.get("interval", 5)

            self.code_ready.emit(user_code, verify_uri)

            import time as _t

            while not self._cancelled:
                _t.sleep(interval)
                poll_resp = requests.post(
                    "https://github.com/login/oauth/access_token",
                    data={
                        "client_id": self.client_id,
                        "device_code": device_code,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    },
                    headers={"Accept": "application/json"},
                    timeout=15,
                )
                poll_data = poll_resp.json()
                if "access_token" in poll_data:
                    token = poll_data["access_token"]
                    headers = github_headers(token)
                    user_resp = requests.get(
                        "https://api.github.com/user", headers=headers, timeout=10
                    )
                    username = "oauth_user"
                    if user_resp.status_code == 200:
                        username = user_resp.json().get("login", "oauth_user")
                    self.token_ready.emit(token, username)
                    return
                elif poll_data.get("error") == "authorization_pending":
                    continue
                elif poll_data.get("error") == "slow_down":
                    interval += 5
                elif poll_data.get("error") == "expired_token":
                    self.error_occurred.emit("Device code expired. Please try again.")
                    return
                else:
                    self.error_occurred.emit(
                        f"OAuth error: {poll_data.get('error_description', poll_data.get('error', 'unknown'))}"
                    )
                    return
            self.error_occurred.emit("Cancelled")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")


# ---------------------------------------------------------------------------
# List Repos Worker (thread-safe)
# ---------------------------------------------------------------------------
class ListReposWorker(QThread):
    results_ready = pyqtSignal(list, str)  # repos, authenticated_user_login
    error_occurred = pyqtSignal(str)

    def __init__(self, token: str, repo_type: str = "owner", api_url: str = ""):
        super().__init__()
        self.token = token
        self.repo_type = repo_type
        self.api_url = api_url or "https://api.github.com"

    def run(self):
        if not HAS_REQUESTS:
            self.error_occurred.emit("requests library not available")
            return

        headers = github_headers(self.token)

        # First, get the authenticated user's login
        authenticated_user = None
        try:
            resp = requests.get(f"{self.api_url}/user", headers=headers, timeout=10)
            if resp.status_code == 200:
                authenticated_user = resp.json().get("login")
                debug_log(f"ListReposWorker: Authenticated user: {authenticated_user}")
        except Exception as e:
            debug_log(f"ListReposWorker: Failed to get authenticated user: {e}")

        repos = []
        page = 1
        per_page = 100

        debug_log(
            f"ListReposWorker: Fetching {self.repo_type} repos for {authenticated_user}"
        )

        while True:
            try:
                # Build params - visibility=all incompatible with type param
                # type=all includes all repos (owner, collaborator, org member)
                params = {
                    "page": page,
                    "per_page": per_page,
                    "type": self.repo_type,
                    "sort": "full_name",
                    "direction": "asc",
                }
                url = f"{self.api_url}/users/{authenticated_user}/repos"
                debug_log(f"ListReposWorker: Fetching page {page}...")
                resp = requests.get(url, headers=headers, params=params, timeout=30)

                # Log rate limit info from headers
                rate_limit = resp.headers.get("X-RateLimit-Remaining", "N/A")
                rate_limit_total = resp.headers.get("X-RateLimit-Limit", "N/A")
                debug_log(
                    f"ListReposWorker: Rate limit - {rate_limit}/{rate_limit_total} remaining"
                )

                if resp.status_code == 401:
                    self.error_occurred.emit("Invalid or expired token")
                    return
                if resp.status_code == 403:
                    self.error_occurred.emit("Rate limit exceeded")
                    return
                if resp.status_code != 200:
                    self.error_occurred.emit(f"API error: {resp.status_code}")
                    return

                data = resp.json()
                debug_log(
                    f"ListReposWorker: Page {page} returned {len(data)} repos (total so far: {len(repos) + len(data)})"
                )
                if not data:
                    debug_log(f"ListReposWorker: No more data on page {page}, stopping")
                    break

                repos.extend(data)
                page += 1

                # Safety limit to prevent infinite loops
                if page > 20:
                    debug_log(f"ListReposWorker: Reached page limit (20), stopping")
                    break

            except Exception as e:
                self.error_occurred.emit(f"Error fetching repos: {str(e)}")
                return

        print(
            f"DEBUG: ListReposWorker finished - total repos: {len(repos)}",
            file=sys.stderr,
        )

        # Emit repos with the authenticated user's login for proper filtering
        self.results_ready.emit(repos, authenticated_user or "")


# ---------------------------------------------------------------------------
class DownloadWorker(QThread):
    progress_updated = pyqtSignal(str, int, str)
    download_finished = pyqtSignal(str, bool, str)

    def __init__(
        self,
        task: DownloadTask,
        token: Optional[str] = None,
        mode: str = "clone",
        speed_limit_kb: int = 0,
        clone_type: int = 0,
    ):
        super().__init__()
        self.task = task
        self.token = token
        self.mode = mode  # "clone", "pull", "update"
        self._cancelled = False
        self.speed_limit_kb = speed_limit_kb  # 0 = unlimited
        self.clone_type = clone_type  # 0=regular, 1=bare, 2=mirror

    def cancel(self):
        self._cancelled = True

    def run(self):
        url = self.task.repo_url.strip()
        if not url.startswith("http") and "/" in url:
            url = f"https://github.com/{url}"
        url = re.sub(r"[\s;|&`$()]", "", url)
        if url.endswith(".git"):
            clean_url = url[:-4]
        else:
            clean_url = url

        output_dir = self.task.output_dir
        os.makedirs(output_dir, exist_ok=True)
        repo_name = clean_url.rstrip("/").split("/")[-1]
        target_dir = os.path.join(output_dir, repo_name)

        if self.mode == "pull" or (
            self.mode == "clone" and os.path.isdir(os.path.join(target_dir, ".git"))
        ):
            self._git_pull(url, target_dir)
        else:
            self._download(url, clean_url, target_dir, output_dir)

    @staticmethod
    def _create_askpass_script(token: str) -> str:
        import tempfile

        script_path = os.path.join(tempfile.gettempdir(), "gh_askpass.bat")
        with open(script_path, "w") as f:
            f.write("@echo off\necho %s\n" % token)
        return script_path

    def _git_pull(self, url: str, target_dir: str):
        self.progress_updated.emit(url, 10, "Updating repository...")
        try:
            cmd = ["git", "-C", target_dir, "pull"]
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            askpass_path = None
            if self.token and "github.com" in url:
                repo_path = url.split("github.com/")[-1].rstrip("/")
                repo_path = repo_path[:-4] if repo_path.endswith(".git") else repo_path
                auth_url = f"https://x-access-token@github.com/{repo_path}"
                askpass_path = self._create_askpass_script(self.token)
                env["GIT_ASKPASS"] = askpass_path
                cmd = ["git", "-C", target_dir, "pull", auth_url]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=target_dir,
                env=env,
                creationflags=CREATE_NO_WINDOW,
            )
            while True:
                if self._cancelled:
                    process.kill()
                    self.download_finished.emit(url, False, "Cancelled")
                    if askpass_path:
                        try:
                            os.remove(askpass_path)
                        except OSError:
                            pass
                    return
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
            rc = process.wait()
            if askpass_path:
                try:
                    os.remove(askpass_path)
                except OSError:
                    pass
            if rc == 0:
                self.progress_updated.emit(url, 100, "Updated")
                self.download_finished.emit(url, True, target_dir)
            else:
                self.download_finished.emit(
                    url, False, f"git pull failed (exit code {rc})"
                )
        except FileNotFoundError:
            self.download_finished.emit(url, False, "git not found on PATH")
        except Exception as e:
            self.download_finished.emit(url, False, str(e))

    def _download(self, url: str, clean_url: str, target_dir: str, output_dir: str):
        self.progress_updated.emit(url, 5, "Starting download...")
        if os.path.isdir(target_dir):
            self._git_pull(url, target_dir)
            return

        # Handle clone type (regular, bare, mirror)
        git_cmd = ["git", "clone", "--progress"]
        if self.clone_type == 1:  # Bare clone
            git_cmd.append("--bare")
        elif self.clone_type == 2:  # Mirror clone
            git_cmd.append("--mirror")

        if (
            self.task.shallow and self.clone_type == 0
        ):  # Shallow only for regular clones
            git_cmd.extend(["--depth", "1"])
        if self.task.branch:
            git_cmd.extend(["--branch", self.task.branch])
        if self.task.submodules and self.clone_type == 0:
            git_cmd.append("--recurse-submodules")

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        askpass_path = None
        if self.token and "github.com" in url:
            repo_path = url.split("github.com/")[-1].rstrip("/")
            repo_path = repo_path[:-4] if repo_path.endswith(".git") else repo_path
            auth_url = f"https://x-access-token@github.com/{repo_path}"
            askpass_path = self._create_askpass_script(self.token)
            env["GIT_ASKPASS"] = askpass_path
            git_cmd.append(auth_url)
        else:
            git_cmd.append(url)
        git_cmd.append(target_dir)

        try:
            self.progress_updated.emit(url, 15, "Cloning repository...")
            process = subprocess.Popen(
                git_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=output_dir,
                env=env,
                creationflags=CREATE_NO_WINDOW,
            )
            while True:
                if self._cancelled:
                    process.kill()
                    self.download_finished.emit(url, False, "Cancelled")
                    if askpass_path:
                        try:
                            os.remove(askpass_path)
                        except OSError:
                            pass
                    return
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                line_str = line.decode("utf-8", errors="replace")
                if "%" in line_str:
                    try:
                        pct = int(line_str.split("%")[0].strip().split()[-1])
                        self.progress_updated.emit(
                            url, 15 + int(pct * 0.75), line_str.strip()
                        )
                    except (ValueError, IndexError):
                        pass

            returncode = process.wait()
            if askpass_path:
                try:
                    os.remove(askpass_path)
                except OSError:
                    pass
            if returncode == 0:
                self.progress_updated.emit(url, 100, "Complete")
                self.download_finished.emit(url, True, target_dir)
            elif not self._cancelled:
                self._download_zip(clean_url, target_dir, output_dir)
        except FileNotFoundError:
            self._download_zip(clean_url, target_dir, output_dir)
        except Exception as e:
            self.download_finished.emit(url, False, str(e))

    def _download_zip(self, url: str, target_dir: str, output_dir: str):
        if not HAS_REQUESTS:
            self.download_finished.emit(
                url, False, "git not found and requests unavailable"
            )
            return

        branch = self.task.branch or "main"
        zip_url = f"{url}/archive/refs/heads/{branch}.zip"
        repo_name = url.rstrip("/").split("/")[-1]
        zip_path = os.path.join(output_dir, f"{repo_name}.zip")

        self.progress_updated.emit(url, 30, "Downloading zip archive...")
        try:
            headers = github_headers(self.token)
            response = requests.get(zip_url, headers=headers, stream=True, timeout=60)
            if response.status_code == 404:
                zip_url = f"{url}/archive/refs/heads/master.zip"
                response = requests.get(
                    zip_url, headers=headers, stream=True, timeout=60
                )
            if response.status_code != 200:
                self.download_finished.emit(
                    url, False, f"HTTP {response.status_code}: {response.reason}"
                )
                return

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 8192
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self._cancelled:
                        self.download_finished.emit(url, False, "Cancelled")
                        return
                    f.write(chunk)
                    downloaded += len(chunk)
                    if self.speed_limit_kb > 0:
                        elapsed_expected = len(chunk) / (self.speed_limit_kb * 1024)
                        time.sleep(max(0, elapsed_expected))
                    if total_size:
                        pct = int((downloaded / total_size) * 100)
                        self.progress_updated.emit(
                            url, 30 + int(pct * 0.5), f"Downloading {pct}%"
                        )

            self.progress_updated.emit(url, 85, "Extracting...")
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(output_dir)
            os.remove(zip_path)

            self.progress_updated.emit(url, 100, "Complete")
            self.download_finished.emit(url, True, output_dir)
        except Exception as e:
            self.download_finished.emit(url, False, str(e))


# ---------------------------------------------------------------------------
# Push Worker (thread-safe)
# ---------------------------------------------------------------------------
class PushWorker(QThread):
    progress_updated = pyqtSignal(str)
    push_finished = pyqtSignal(bool, str)

    def __init__(
        self,
        repo_dir: str,
        commit_msg: str,
        token: Optional[str] = None,
        files: list = None,
    ):
        super().__init__()
        self.repo_dir = repo_dir
        self.commit_msg = commit_msg
        self.token = token
        self.files = files  # None = stage all
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        if not os.path.isdir(self.repo_dir):
            self.push_finished.emit(False, f"Directory not found: {self.repo_dir}")
            return
        if not os.path.isdir(os.path.join(self.repo_dir, ".git")):
            self.push_finished.emit(False, "Not a git repository")
            return

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"

        try:
            self.progress_updated.emit("Staging files...")
            if self.files:
                cmd = ["git", "add"] + self.files
            else:
                cmd = ["git", "add", "-A"]
            result = subprocess.run(
                cmd, cwd=self.repo_dir, capture_output=True, text=True, env=env
            )
            if result.returncode != 0:
                self.push_finished.emit(False, f"git add failed: {result.stderr[:200]}")
                return

            self.progress_updated.emit("Committing...")
            result = subprocess.run(
                ["git", "commit", "-m", self.commit_msg],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                env=env,
            )
            if result.returncode != 0 and "nothing to commit" not in result.stdout:
                self.push_finished.emit(
                    False, f"git commit failed: {result.stderr[:200]}"
                )
                return

            self.progress_updated.emit("Pushing to remote...")
            if self.token:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.repo_dir,
                    capture_output=True,
                    text=True,
                )
                remote_url = result.stdout.strip()
                if "github.com" in remote_url:
                    auth_url = remote_url.replace("https://", f"https://{self.token}@")
                    result = subprocess.run(
                        ["git", "remote", "set-url", "origin", auth_url],
                        cwd=self.repo_dir,
                        capture_output=True,
                        text=True,
                    )
            result = subprocess.run(
                ["git", "push", "origin"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                env=env,
                timeout=120,
            )
            if self.token and "github.com" in remote_url:
                subprocess.run(
                    ["git", "remote", "set-url", "origin", remote_url],
                    cwd=self.repo_dir,
                    capture_output=True,
                    text=True,
                )
            if result.returncode == 0:
                self.push_finished.emit(True, "Pushed successfully")
            else:
                self.push_finished.emit(
                    False, f"git push failed: {result.stderr[:300]}"
                )
        except subprocess.TimeoutExpired:
            self.push_finished.emit(False, "Push timed out (120s)")
        except Exception as e:
            self.push_finished.emit(False, str(e))


# ---------------------------------------------------------------------------
# Matrix Background Widget
# ---------------------------------------------------------------------------
class MatrixRainWidget(QWidget):
    columns: List[dict]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.columns = []
        self.setColumnCount(60)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(50)
        self._char_alpha = 0.35

    def setColumnCount(self, count: int):
        import random

        chars = "01AIUEOKKKKKSSSSSTTTTTNNNNKHHHHHMMMMMYYYRRRRRWN"
        self.columns = []
        for _ in range(count):
            self.columns.append(
                {
                    "chars": [random.choice(chars) for _ in range(30)],
                    "y": random.randint(-30, 0),
                }
            )

    def _advance(self):
        import random

        chars = "01AIUEOKKKKKSSSSSTTTTTNNNNKHHHHHMMMMMYYYRRRRRWN"
        char_h = 16
        widget_height = self.height() if self.height() > 0 else 600
        for col in self.columns:
            col["y"] += 1
            if col["y"] * char_h > widget_height:
                col["y"] = -len(col["chars"])
                col["chars"] = [random.choice(chars) for _ in range(30)]
            if random.random() < 0.05:
                col["chars"][random.randint(0, len(col["chars"]) - 1)] = random.choice(
                    chars
                )
        self.update()

    def setOpacity(self, opacity: float):
        self._char_alpha = opacity
        self.update()

    def paintEvent(self, event):
        if not self.columns:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont("Consolas", 10)
        painter.setFont(font)
        char_h = 16
        char_w = 12
        base_alpha = int(self._char_alpha * 255)
        for i, col in enumerate(self.columns):
            x = i * char_w
            for j, ch in enumerate(col["chars"]):
                y = (col["y"] + j) * char_h
                if y < 0 or y > self.height():
                    continue
                trail_fade = max(0.0, 1.0 - j / 25.0)
                if j == 0:
                    alpha = min(255, base_alpha + 80)
                    if (
                        hasattr(self.parent(), "matrix_color_override")
                        and self.parent().matrix_color_override
                    ):
                        parts = self.parent().matrix_color_override.split(",")
                        color = QColor(
                            int(parts[0]), int(parts[1]), int(parts[2]), alpha
                        )
                    else:
                        color = QColor(180, 255, 180, alpha)
                else:
                    alpha = max(20, int(base_alpha * trail_fade))
                    if (
                        hasattr(self.parent(), "matrix_color_override")
                        and self.parent().matrix_color_override
                    ):
                        parts = self.parent().matrix_color_override.split(",")
                        color = QColor(
                            int(parts[0]), int(parts[1]), int(parts[2]), alpha
                        )
                    else:
                        color = QColor(0, 255, 0, alpha)
                painter.setPen(QPen(color))
                painter.drawText(x, y, ch)
        painter.end()


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class GitHubDownloaderEnhanced(QMainWindow):
    VERSION = VERSION

    def __init__(self):
        super().__init__()
        self.rate_manager = RateLimitManager()
        self.account_manager = AccountManager()
        self.active_workers: Dict[str, DownloadWorker] = {}
        self.download_queue: List[DownloadTask] = []
        self.recent_downloads: List[str] = []
        self.is_dark_mode = False
        self._validator: Optional[TokenValidator] = None
        self._search_worker: Optional[SearchWorker] = None
        self._info_worker: Optional[RepoInfoWorker] = None
        self._push_worker: Optional[PushWorker] = None
        self.matrix_enabled = True
        self.matrix_color_override = None  # For themed matrix colors

        # Multi-account repo fetching state
        self._all_accounts_repos = []
        self._accounts_to_fetch = []
        self._all_accounts_fetch_complete = (
            False  # Guard to prevent double-call of _on_all_accounts_repos_fetched
        )
        self._account_usernames = {}  # Cache for actual GitHub usernames

        # Set default window size - wider for better visibility
        self.resize(1200, 800)

        self._load_accounts()
        self._init_ui()
        self._init_tray()
        self._init_shortcuts()
        self._load_settings()
        self._start_rate_monitor()
        # Update account dropdown after UI is initialized
        self._update_account_selector()
        # Tab navigation guard state
        self._last_tab_index = 0

    def _load_accounts(self):
        for account in self.account_manager.list_accounts():
            token = self.account_manager.get_token(account["id"])
            if token:
                username = account.get("username", account["id"])
                self.rate_manager.add_account(account["id"], token, username)
                # Store original username for now
                self._account_usernames[account["id"]] = username

        # Fetch actual GitHub usernames after loading accounts
        self._fetch_all_usernames()

    def _fetch_all_usernames(self):
        """Fetch actual GitHub usernames for all accounts"""
        print(
            f"DEBUG: _fetch_all_usernames ENTER, accounts: {list(self.rate_manager.accounts.keys())}",
            file=sys.stderr,
        )
        for acc_id, account in self.rate_manager.accounts.items():
            token = account.get("token", "")
            if not token:
                print(f"DEBUG: No token for account {acc_id}", file=sys.stderr)
                continue
            try:
                headers = github_headers(token)
                resp = requests.get(
                    f"{self._get_api_url()}/user", headers=headers, timeout=10
                )
                if resp.status_code == 200:
                    user_info = resp.json()
                    actual_login = user_info.get("login", acc_id)
                    self._account_usernames[acc_id] = actual_login
                    print(
                        f"DEBUG: Account {acc_id} -> actual user: {actual_login}",
                        file=sys.stderr,
                    )
                else:
                    print(
                        f"DEBUG: /user failed for {acc_id}: {resp.status_code}",
                        file=sys.stderr,
                    )
            except Exception as e:
                print(
                    f"DEBUG: Exception fetching username for {acc_id}: {e}",
                    file=sys.stderr,
                )
        print(
            f"DEBUG: _account_usernames after fetch: {self._account_usernames}",
            file=sys.stderr,
        )

    def _init_ui(self):
        self.setWindowTitle(f"GitHub Repo Downloader v{self.VERSION}")
        self.setGeometry(100, 100, 1050, 800)
        self.setAcceptDrops(True)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.matrix_bg = MatrixRainWidget(central)
        self.matrix_bg.setGeometry(0, 0, self.width(), self.height())

        content = QWidget()
        content.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)

        tabs = QTabWidget()
        # keep a reference for navigation guards
        self.tabs = tabs
        self._last_tab_index = getattr(self, "_last_tab_index", 0)
        tabs.currentChanged.connect(self._handle_tab_change)

        # ===== DOWNLOAD TAB =====
        download_tab = QWidget()
        dl_layout = QVBoxLayout(download_tab)

        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("Account:"))
        self.account_selector = QComboBox()
        self.account_selector.currentIndexChanged.connect(self._on_account_changed)
        account_layout.addWidget(self.account_selector)
        self.add_account_btn = QPushButton("+ Add Account")
        self.add_account_btn.setToolTip(
            "Add a new GitHub account using a Personal Access Token (PAT)"
        )
        self.add_account_btn.clicked.connect(self._show_add_account_dialog)
        account_layout.addWidget(self.add_account_btn)
        self.rate_status_label = QLabel("Rate Limit: --")
        account_layout.addWidget(self.rate_status_label)
        account_layout.addStretch()
        dl_layout.addLayout(account_layout)

        # Batch URL input section
        batch_group = QGroupBox("Batch Download (one URL per line)")
        batch_layout = QVBoxLayout()
        self.batch_input = QTextEdit()
        self.batch_input.setPlaceholderText(
            "https://github.com/owner/repo1\nhttps://github.com/owner/repo2\nowner/repo3"
        )
        self.batch_input.setMaximumHeight(80)
        batch_layout.addWidget(self.batch_input)
        batch_btn_row = QHBoxLayout()
        self.batch_download_btn = QPushButton("[v] Download All")
        self.batch_download_btn.setToolTip(
            "Download all repos listed in the batch text area above"
        )
        self.batch_download_btn.clicked.connect(self._start_batch_download)
        batch_btn_row.addWidget(self.batch_download_btn)
        # Download from all accounts button
        self.download_all_accounts_btn = QPushButton("[v] All Accounts")
        self.download_all_accounts_btn.setToolTip(
            "Download repos from ALL accounts (including private)"
        )
        self.download_all_accounts_btn.clicked.connect(self._download_all_accounts)
        batch_btn_row.addWidget(self.download_all_accounts_btn)
        # Selective download button
        self.selective_download_btn = QPushButton("[x] Selective")
        self.selective_download_btn.setToolTip("Select specific repos to download")
        self.selective_download_btn.clicked.connect(self._show_selective_download)
        batch_btn_row.addWidget(self.selective_download_btn)
        batch_clear_btn = QPushButton("Clear")
        batch_clear_btn.setToolTip("Clear all URLs from the batch text area")
        batch_clear_btn.clicked.connect(self.batch_input.clear)
        batch_btn_row.addWidget(batch_clear_btn)
        batch_btn_row.addStretch()
        batch_layout.addLayout(batch_btn_row)
        batch_group.setLayout(batch_layout)
        dl_layout.addWidget(batch_group)

        # Single URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Repo:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("owner/repo or full URL")
        url_layout.addWidget(self.url_input)
        self.download_btn = QPushButton("[v] Download")
        self.download_btn.setToolTip("Download the specified repository")
        self.download_btn.clicked.connect(self._start_download)
        url_layout.addWidget(self.download_btn)
        self.update_btn = QPushButton("[R] Update")
        self.update_btn.setToolTip("Update an already downloaded repository")
        self.update_btn.clicked.connect(self._start_update)
        url_layout.addWidget(self.update_btn)
        # Preview button
        self.preview_btn = QPushButton("[i] Preview")
        self.preview_btn.setToolTip(
            "Show repository info (stars, description, language, etc.)"
        )
        self.preview_btn.clicked.connect(self._preview_repo)
        url_layout.addWidget(self.preview_btn)
        dl_layout.addLayout(url_layout)

        # Branch/Tag selector
        branch_layout = QHBoxLayout()
        branch_layout.addWidget(QLabel("Branch/Tag:"))
        self.branch_combo = QComboBox()
        self.branch_combo.setEditable(True)
        self.branch_combo.setPlaceholderText("Select branch or tag...")
        self.branch_combo.setMinimumWidth(200)
        self.branch_combo.currentTextChanged.connect(self._on_branch_changed)
        branch_layout.addWidget(self.branch_combo)
        self.refresh_branches_btn = QPushButton("[R]")
        self.refresh_branches_btn.setToolTip("Refresh branches/tags")
        self.refresh_branches_btn.clicked.connect(self._fetch_branches_tags)
        branch_layout.addWidget(self.refresh_branches_btn)
        branch_layout.addStretch()
        branch_layout.addWidget(QLabel("Options:"))
        self.shallow_check = QCheckBox("Shallow (--depth 1)")
        branch_layout.addWidget(self.shallow_check)
        self.submodules_check = QCheckBox("Submodules")
        self.submodules_check.setToolTip("Include git submodules when cloning")
        branch_layout.addWidget(self.submodules_check)
        branch_layout.addStretch()
        dl_layout.addLayout(branch_layout)

        # Recent downloads section
        recent_group = QGroupBox("Recent Downloads (Premium)")
        recent_layout = QVBoxLayout()
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(100)
        self.recent_list.itemDoubleClicked.connect(self._recent_item_clicked)
        recent_layout.addWidget(self.recent_list)
        recent_btn_layout = QHBoxLayout()
        redownload_btn = QPushButton("[R] Redownload")
        redownload_btn.setToolTip("Redownload the selected recent repository")
        redownload_btn.clicked.connect(self._redownload_selected)
        recent_btn_layout.addWidget(redownload_btn)
        clear_recent_btn = QPushButton("Clear Recent")
        clear_recent_btn.setToolTip("Clear the recent downloads history")
        clear_recent_btn.clicked.connect(self._clear_recent)
        recent_btn_layout.addWidget(clear_recent_btn)
        recent_btn_layout.addStretch()
        recent_layout.addLayout(recent_btn_layout)
        recent_group.setLayout(recent_layout)
        dl_layout.addWidget(recent_group)

        # Download Status section
        status_group = QGroupBox("Download Status")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Repos queued: 0 | Completed: 0")
        self.status_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_btn_layout = QHBoxLayout()
        refresh_status_btn = QPushButton("[R] Refresh")
        refresh_status_btn.setToolTip("Refresh the download status display")
        refresh_status_btn.clicked.connect(self._refresh_download_status)
        status_btn_layout.addWidget(refresh_status_btn)
        show_completed_btn = QPushButton("Show Completed")
        show_completed_btn.setToolTip("Show list of completed downloads")
        show_completed_btn.clicked.connect(self._show_completed_repos)
        status_btn_layout.addWidget(show_completed_btn)
        account_breakdown_btn = QPushButton("Account Breakdown")
        account_breakdown_btn.setToolTip("Show detailed breakdown of repos per account")
        account_breakdown_btn.clicked.connect(self._show_account_breakdown)
        status_btn_layout.addWidget(account_breakdown_btn)
        show_all_repos_btn = QPushButton("Show ALL Repos")
        show_all_repos_btn.setToolTip(
            "Show ALL repos including owned, forks, private, and starred repos from all accounts"
        )
        show_all_repos_btn.clicked.connect(self._show_all_repos_including_forks)
        status_btn_layout.addWidget(show_all_repos_btn)
        status_btn_layout.addStretch()
        status_layout.addLayout(status_btn_layout)
        status_group.setLayout(status_layout)
        dl_layout.addWidget(status_group)

        # Track download stats
        self.repos_queued_count = 0
        self.last_queue_time = None

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Save to:"))
        self.download_dir_input = QLineEdit()
        self.download_dir_input.setText(
            os.path.join(os.path.expanduser("~"), "Downloads", "GitHubRepos")
        )
        self.download_dir_input.setReadOnly(True)
        dir_layout.addWidget(self.download_dir_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.setToolTip("Choose where to save downloaded repositories")
        browse_btn.clicked.connect(self._select_download_directory)
        dir_layout.addWidget(browse_btn)
        open_dir_btn = QPushButton("Open Folder")
        open_dir_btn.setToolTip("Open the download folder in Windows Explorer")
        open_dir_btn.clicked.connect(self._open_download_folder)
        dir_layout.addWidget(open_dir_btn)
        dl_layout.addLayout(dir_layout)

        self.repo_info_label = QLabel("")
        self.repo_info_label.setWordWrap(True)
        self.repo_info_label.setStyleSheet("color: #888; font-size: 11px;")
        dl_layout.addWidget(self.repo_info_label)

        # Current download status
        self.current_download_label = QLabel("Ready to download")
        self.current_download_label.setStyleSheet(
            "color: #58a6ff; font-size: 12px; font-weight: bold;"
        )
        dl_layout.addWidget(self.current_download_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        dl_layout.addWidget(self.progress_bar)

        progress_info = QHBoxLayout()
        self.eta_label = QLabel("")
        progress_info.addWidget(self.eta_label)
        progress_info.addStretch()
        self.rate_remaining_label = QLabel("API Remaining: --")
        progress_info.addWidget(self.rate_remaining_label)
        dl_layout.addLayout(progress_info)

        dl_layout.addWidget(QLabel("Download Queue:"))
        self.queue_list = QListWidget()
        dl_layout.addWidget(self.queue_list)

        queue_btn_layout = QHBoxLayout()
        queue_btn = QPushButton("Add to Queue")
        queue_btn.setToolTip("Add the current repository to the download queue")
        queue_btn.clicked.connect(self._add_to_queue)
        queue_btn_layout.addWidget(queue_btn)
        self.start_queue_btn = QPushButton("Start Queue")
        self.start_queue_btn.setToolTip("Start processing the download queue")
        self.start_queue_btn.clicked.connect(self._process_queue)
        queue_btn_layout.addWidget(self.start_queue_btn)
        # Check all repos for updates button
        self.check_all_updates_btn = QPushButton("[R] Check All Updates")
        self.check_all_updates_btn.setToolTip("Check all downloaded repos for updates")
        self.check_all_updates_btn.clicked.connect(self._check_all_updates)
        queue_btn_layout.addWidget(self.check_all_updates_btn)
        clear_btn = QPushButton("Clear Done")
        clear_btn.setToolTip("Remove completed items from the queue")
        clear_btn.clicked.connect(self._clear_completed)
        queue_btn_layout.addWidget(clear_btn)
        dl_layout.addLayout(queue_btn_layout)

        tabs.addTab(download_tab, "[v] Downloads")

        # ===== SEARCH TAB =====
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)

        search_bar = QHBoxLayout()
        search_bar.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g. python web framework")
        search_bar.addWidget(self.search_input)
        search_btn = QPushButton("Search")
        search_btn.setToolTip("Search GitHub for repositories matching your query")
        search_btn.clicked.connect(self._do_search)
        search_bar.addWidget(search_btn)
        search_layout.addLayout(search_bar)

        self.search_results = QListWidget()
        self.search_results.itemDoubleClicked.connect(self._search_result_clicked)
        search_layout.addWidget(self.search_results)

        self.search_status = QLabel("Search GitHub repositories")
        self.search_status.setStyleSheet("color: #888;")
        search_layout.addWidget(self.search_status)

        tabs.addTab(search_tab, "[Search] Search")

        # ===== PUSH TAB =====
        push_tab = QWidget()
        push_layout = QVBoxLayout(push_tab)

        push_layout.addWidget(QLabel("Push Changes to GitHub"))
        push_layout.addWidget(QLabel("Local repository:"))
        self.push_dir_input = QLineEdit()
        self.push_dir_input.setPlaceholderText("Select a local git repo directory")
        push_layout.addWidget(self.push_dir_input)
        push_browse_btn = QPushButton("Browse...")
        push_browse_btn.setToolTip("Select local repository directory to push from")
        push_browse_btn.clicked.connect(self._select_push_directory)
        push_layout.addWidget(push_browse_btn)

        push_layout.addWidget(QLabel("Commit message:"))
        self.commit_msg_input = QLineEdit()
        self.commit_msg_input.setPlaceholderText("Describe your changes...")
        push_layout.addWidget(self.commit_msg_input)

        self.push_progress = QLabel("")
        push_layout.addWidget(self.push_progress)

        push_btn_layout = QHBoxLayout()
        stage_commit_btn = QPushButton("Stage All & Commit")
        stage_commit_btn.setToolTip("Stage all changes and commit with your message")
        stage_commit_btn.clicked.connect(self._stage_and_commit)
        push_btn_layout.addWidget(stage_commit_btn)
        push_push_btn = QPushButton("Push to GitHub")
        push_push_btn.setToolTip("Push committed changes to GitHub")
        push_push_btn.clicked.connect(self._push_to_github)
        push_btn_layout.addWidget(push_push_btn)
        push_layout.addLayout(push_btn_layout)

        push_layout.addStretch()
        tabs.addTab(push_tab, "[Up] Push")

        # ===== ACCOUNTS TAB =====
        accounts_tab = QWidget()
        accounts_layout = QVBoxLayout(accounts_tab)
        accounts_layout.addWidget(QLabel("Configured GitHub Accounts:"))

        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels(
            ["Account", "Username", "Status", "Rate Limit"]
        )
        self.accounts_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        accounts_layout.addWidget(self.accounts_table)

        acc_btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Accounts")
        refresh_btn.setToolTip("Refresh the accounts list display")
        refresh_btn.clicked.connect(self._refresh_accounts_list)
        acc_btn_layout.addWidget(refresh_btn)
        check_limits_btn = QPushButton("Check Rate Limits")
        check_limits_btn.setToolTip("Check API rate limits for all accounts")
        check_limits_btn.clicked.connect(self._check_rate_limits)
        acc_btn_layout.addWidget(check_limits_btn)
        download_selected_btn = QPushButton("[v] Download Selected")
        download_selected_btn.setToolTip("Download repos from selected account")
        download_selected_btn.clicked.connect(self._download_from_selected_account)
        acc_btn_layout.addWidget(download_selected_btn)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setToolTip("Remove selected account from configuration")
        remove_btn.clicked.connect(self._remove_selected_account)
        acc_btn_layout.addWidget(remove_btn)
        accounts_layout.addLayout(acc_btn_layout)
        tabs.addTab(accounts_tab, "[User] Accounts")

        # ===== SYNC/DIFF TAB =====
        sync_tab = QWidget()
        sync_layout = QVBoxLayout(sync_tab)
        sync_layout.addWidget(QLabel("Compare Local vs Remote Repository"))
        sync_dir_layout = QHBoxLayout()
        sync_dir_layout.addWidget(QLabel("Local Repo:"))
        self.sync_dir_input = QLineEdit()
        self.sync_dir_input.setPlaceholderText("Select a local git repo")
        sync_dir_layout.addWidget(self.sync_dir_input)
        sync_browse_btn = QPushButton("Browse...")
        sync_browse_btn.setToolTip("Select local repository to compare")
        sync_browse_btn.clicked.connect(self._select_sync_directory)
        sync_dir_layout.addWidget(sync_browse_btn)
        sync_layout.addLayout(sync_dir_layout)
        self.diff_output = QTextEdit()
        self.diff_output.setReadOnly(True)
        sync_layout.addWidget(self.diff_output)
        sync_btn_layout = QHBoxLayout()
        diff_btn = QPushButton("Show Diff (Local vs Remote)")
        diff_btn.setToolTip("Show differences between local and remote repository")
        diff_btn.clicked.connect(self._show_repo_diff)
        sync_btn_layout.addWidget(diff_btn)
        fetch_btn = QPushButton("Fetch Remote Info")
        fetch_btn.setToolTip("Fetch information from remote repository")
        fetch_btn.clicked.connect(self._fetch_remote_info)
        sync_btn_layout.addWidget(fetch_btn)
        sync_btn_layout.addStretch()
        sync_layout.addLayout(sync_btn_layout)
        tabs.addTab(sync_tab, "[Sync] Sync")

        # ===== COMMITS TAB =====
        commits_tab = QWidget()
        commits_layout = QVBoxLayout(commits_tab)
        commits_layout.addWidget(QLabel("Browse Repository Commit History"))
        commits_repo_layout = QHBoxLayout()
        commits_repo_layout.addWidget(QLabel("Repo:"))
        self.commits_repo_input = QLineEdit()
        self.commits_repo_input.setPlaceholderText(
            "owner/repo (requires authentication)"
        )
        commits_repo_layout.addWidget(self.commits_repo_input)
        commits_fetch_btn = QPushButton("Fetch Commits")
        commits_fetch_btn.setToolTip("Fetch commit history for the repository")
        commits_fetch_btn.clicked.connect(self._fetch_commits)
        commits_repo_layout.addWidget(commits_fetch_btn)
        commits_layout.addLayout(commits_repo_layout)
        self.commits_list = QListWidget()
        commits_layout.addWidget(self.commits_list)
        self.commits_info = QLabel("")
        self.commits_info.setStyleSheet("color: #888; font-size: 11px;")
        commits_layout.addWidget(self.commits_info)
        tabs.addTab(commits_tab, "[Commits] Commits")

        # ===== GISTS TAB =====
        gists_tab = QWidget()
        gists_layout = QVBoxLayout(gists_tab)
        gists_layout.addWidget(QLabel("GitHub Gists"))
        gists_layout.addWidget(QLabel("Download and create gists:"))
        self.gists_list = QListWidget()
        gists_layout.addWidget(self.gists_list)
        gists_btn_layout = QHBoxLayout()
        fetch_gists_btn = QPushButton("Fetch My Gists")
        fetch_gists_btn.setToolTip("Fetch your GitHub Gists")
        fetch_gists_btn.clicked.connect(self._fetch_gists)
        gists_btn_layout.addWidget(fetch_gists_btn)
        download_gist_btn = QPushButton("Download Selected")
        download_gist_btn.setToolTip("Download the selected gist")
        download_gist_btn.clicked.connect(self._download_selected_gist)
        gists_btn_layout.addWidget(download_gist_btn)
        create_gist_btn = QPushButton("Create Gist")
        create_gist_btn.setToolTip("Create a new GitHub Gist")
        create_gist_btn.clicked.connect(self._show_create_gist_dialog)
        gists_btn_layout.addWidget(create_gist_btn)
        gists_btn_layout.addStretch()
        gists_layout.addLayout(gists_btn_layout)
        tabs.addTab(gists_tab, "[Gists] Gists")

        # ===== FILE BROWSER TAB =====
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        files_layout.addWidget(QLabel("Browse Repository Files (via API)"))
        files_repo_layout = QHBoxLayout()
        files_repo_layout.addWidget(QLabel("Repo:"))
        self.files_repo_input = QLineEdit()
        self.files_repo_input.setPlaceholderText("owner/repo")
        files_repo_layout.addWidget(self.files_repo_input)
        files_path_layout = QHBoxLayout()
        files_path_layout.addWidget(QLabel("Path:"))
        self.files_path_input = QLineEdit()
        self.files_path_input.setText("/")
        files_path_layout.addWidget(self.files_path_input)
        files_btn_layout = QHBoxLayout()
        browse_files_btn = QPushButton("Browse")
        browse_files_btn.setToolTip("Browse repository files via GitHub API")
        browse_files_btn.clicked.connect(self._browse_repo_files)
        files_btn_layout.addWidget(browse_files_btn)
        download_file_repo_btn = QPushButton("Clone This Repo")
        download_file_repo_btn.setToolTip(
            "Clone the repository shown in the file browser"
        )
        download_file_repo_btn.clicked.connect(self._clone_from_file_browser)
        files_btn_layout.addWidget(download_file_repo_btn)
        files_btn_layout.addStretch()
        files_layout.addLayout(files_repo_layout)
        files_layout.addLayout(files_path_layout)
        files_layout.addLayout(files_btn_layout)
        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabels(["Name", "Type", "Size"])
        self.files_tree.itemDoubleClicked.connect(self._file_tree_double_click)
        files_layout.addWidget(self.files_tree)
        tabs.addTab(files_tab, "[Files] Files")

        # ===== PULL REQUESTS TAB =====
        pr_tab = QWidget()
        pr_layout = QVBoxLayout(pr_tab)
        pr_layout.addWidget(QLabel("Checkout Pull Requests"))
        pr_repo_layout = QHBoxLayout()
        pr_repo_layout.addWidget(QLabel("Repo:"))
        self.pr_repo_input = QLineEdit()
        self.pr_repo_input.setPlaceholderText("owner/repo")
        pr_repo_layout.addWidget(self.pr_repo_input)
        pr_repo_layout.addWidget(QLabel("PR #:"))
        self.pr_number_input = QSpinBox()
        self.pr_number_input.setMinimum(1)
        self.pr_number_input.setMaximum(99999)
        pr_repo_layout.addWidget(self.pr_number_input)
        pr_fetch_btn = QPushButton("Fetch PR")
        pr_fetch_btn.setToolTip("Fetch information about a specific pull request")
        pr_fetch_btn.clicked.connect(self._fetch_pr_info)
        pr_repo_layout.addWidget(pr_fetch_btn)
        pr_layout.addLayout(pr_repo_layout)
        self.pr_info = QTextEdit()
        self.pr_info.setReadOnly(True)
        pr_layout.addWidget(self.pr_info)
        pr_btn_layout = QHBoxLayout()
        checkout_pr_btn = QPushButton("Checkout PR (git fetch ref)")
        checkout_pr_btn.setToolTip("Fetch and checkout a pull request locally")
        checkout_pr_btn.clicked.connect(self._checkout_pr)
        pr_btn_layout.addWidget(checkout_pr_btn)
        pr_btn_layout.addStretch()
        pr_layout.addLayout(pr_btn_layout)
        tabs.addTab(pr_tab, "[PRs] PRs")

        # ===== SCHEDULE TAB =====
        schedule_tab = QWidget()
        schedule_layout = QVBoxLayout(schedule_tab)
        schedule_layout.addWidget(QLabel("Automatic Repository Updates"))
        schedule_repos_layout = QHBoxLayout()
        schedule_repos_layout.addWidget(QLabel("Repos (one per line):"))
        self.schedule_repos_input = QTextEdit()
        self.schedule_repos_input.setPlaceholderText("owner/repo\nowner2/repo2")
        self.schedule_repos_input.setMaximumHeight(80)
        schedule_repos_layout.addWidget(self.schedule_repos_input)
        schedule_layout.addLayout(schedule_repos_layout)
        schedule_interval_layout = QHBoxLayout()
        schedule_interval_layout.addWidget(QLabel("Update interval:"))
        self.schedule_interval = QComboBox()
        self.schedule_interval.addItems(
            ["Every 30 minutes", "Every hour", "Every 6 hours", "Every 24 hours"]
        )
        self.schedule_interval.setCurrentIndex(1)
        schedule_interval_layout.addWidget(self.schedule_interval)
        schedule_interval_layout.addStretch()
        schedule_layout.addLayout(schedule_interval_layout)
        schedule_btn_layout = QHBoxLayout()
        self.schedule_toggle_btn = QPushButton("Start Scheduler")
        self.schedule_toggle_btn.setToolTip(
            "Start or stop automatic repository updates"
        )
        self.schedule_toggle_btn.clicked.connect(self._toggle_scheduler)
        schedule_btn_layout.addWidget(self.schedule_toggle_btn)
        self.schedule_status = QLabel("Scheduler: stopped")
        schedule_btn_layout.addWidget(self.schedule_status)
        schedule_btn_layout.addStretch()
        schedule_layout.addLayout(schedule_btn_layout)
        self.schedule_log = QTextEdit()
        self.schedule_log.setReadOnly(True)
        self.schedule_log.setMaximumHeight(100)
        schedule_layout.addWidget(self.schedule_log)
        tabs.addTab(schedule_tab, "[Schedule] Schedule")

        # ===== RELEASES TAB (Premium) =====
        releases_tab = QWidget()
        releases_layout = QVBoxLayout(releases_tab)

        releases_header = QLabel("[Releases] Release Downloader (Premium Feature)")
        releases_header.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        releases_layout.addWidget(releases_header)

        releases_desc = QLabel(
            "Download the latest releases (zip/tar.gz) from any public or private repository."
        )
        releases_desc.setStyleSheet("color: #888;")
        releases_layout.addWidget(releases_desc)

        releases_input_layout = QHBoxLayout()
        releases_input_layout.addWidget(QLabel("Repository:"))
        self.releases_repo_input = QLineEdit()
        self.releases_repo_input.setPlaceholderText(
            "owner/repo (e.g., microsoft/vscode)"
        )
        releases_input_layout.addWidget(self.releases_repo_input)
        releases_layout.addLayout(releases_input_layout)

        releases_btn_layout = QHBoxLayout()
        self.fetch_releases_btn = QPushButton("Fetch Releases")
        self.fetch_releases_btn.setToolTip("Fetch all releases for the repository")
        self.fetch_releases_btn.clicked.connect(self._fetch_releases)
        releases_btn_layout.addWidget(self.fetch_releases_btn)

        self.releases_refresh_btn = QPushButton("Get Latest")
        self.releases_refresh_btn.setToolTip(
            "Download the latest release automatically"
        )
        self.releases_refresh_btn.clicked.connect(self._download_latest_release)
        releases_btn_layout.addWidget(self.releases_refresh_btn)
        releases_layout.addLayout(releases_btn_layout)

        self.releases_list = QListWidget()
        releases_layout.addWidget(QLabel("Available Releases:"))
        releases_layout.addWidget(self.releases_list)

        self.release_download_dir = QLineEdit()
        self.release_download_dir.setPlaceholderText(
            "Download location (default: Downloads folder)"
        )
        releases_layout.addWidget(self.release_download_dir)

        tabs.addTab(releases_tab, "[Releases] Releases (Premium)")

        # ===== ANALYTICS TAB (Premium) =====
        analytics_tab = QWidget()
        analytics_layout = QVBoxLayout(analytics_tab)

        analytics_header = QLabel("[Analytics] Repository Analytics (Premium Feature)")
        analytics_header.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        analytics_layout.addWidget(analytics_header)

        analytics_desc = QLabel(
            "View detailed statistics and insights about repositories you follow or have downloaded."
        )
        analytics_desc.setStyleSheet("color: #888;")
        analytics_layout.addWidget(analytics_desc)

        analytics_input_layout = QHBoxLayout()
        analytics_input_layout.addWidget(QLabel("Repository:"))
        self.analytics_repo_input = QLineEdit()
        self.analytics_repo_input.setPlaceholderText("owner/repo")
        analytics_input_layout.addWidget(self.analytics_repo_input)
        fetch_analytics_btn = QPushButton("Get Analytics")
        fetch_analytics_btn.setToolTip("Fetch repository analytics and statistics")
        fetch_analytics_btn.clicked.connect(self._fetch_analytics)
        analytics_input_layout.addWidget(fetch_analytics_btn)
        analytics_layout.addLayout(analytics_input_layout)

        self.analytics_output = QTextEdit()
        self.analytics_output.setReadOnly(True)
        self.analytics_output.setMaximumHeight(200)
        analytics_layout.addWidget(self.analytics_output)

        analytics_layout.addWidget(QLabel("Your Downloaded Repos Summary:"))
        self.analytics_summary = QTextEdit()
        self.analytics_summary.setReadOnly(True)
        self.analytics_summary.setMaximumHeight(150)
        analytics_layout.addWidget(self.analytics_summary)
        self._update_analytics_summary()

        tabs.addTab(analytics_tab, "[Analytics] Analytics (Premium)")

        # ===== TEMPLATES TAB (Premium) =====
        templates_tab = QWidget()
        templates_layout = QVBoxLayout(templates_tab)

        templates_header = QLabel("[Templates] Repository Templates (Premium Feature)")
        templates_header.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        templates_layout.addWidget(templates_header)

        templates_desc = QLabel(
            "Create reusable download templates for your favorite repositories."
        )
        templates_desc.setStyleSheet("color: #888;")
        templates_layout.addWidget(templates_desc)

        templates_btn_layout = QHBoxLayout()
        self.save_template_btn = QPushButton("Save Current as Template")
        self.save_template_btn.setToolTip(
            "Save current download settings as a reusable template"
        )
        self.save_template_btn.clicked.connect(self._save_template)
        templates_btn_layout.addWidget(self.save_template_btn)

        self.load_template_btn = QPushButton("Load Template")
        self.load_template_btn.setToolTip("Load a previously saved template")
        self.load_template_btn.clicked.connect(self._load_template)
        templates_btn_layout.addWidget(self.load_template_btn)

        templates_layout.addLayout(templates_btn_layout)

        self.templates_list = QListWidget()
        templates_layout.addWidget(QLabel("Saved Templates:"))
        templates_layout.addWidget(self.templates_list)
        self._load_templates_list()

        templates_layout.addStretch()
        tabs.addTab(templates_tab, "[Templates] Templates (Premium)")

        # ===== IMPORT/EXPORT TAB (Premium) =====
        import_export_tab = QWidget()
        ie_layout = QVBoxLayout(import_export_tab)

        ie_header = QLabel("[Import/Export] Import/Export Data (Premium Feature)")
        ie_header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        ie_layout.addWidget(ie_header)

        ie_desc = QLabel(
            "Backup and restore your data, or transfer to another machine."
        )
        ie_desc.setStyleSheet("color: #888;")
        ie_layout.addWidget(ie_desc)

        ie_btn_layout = QHBoxLayout()
        export_btn = QPushButton("Export All Data")
        export_btn.setToolTip(
            "Export all accounts, settings, and download history to a file"
        )
        export_btn.clicked.connect(self._export_data)
        ie_btn_layout.addWidget(export_btn)

        import_btn = QPushButton("Import Data")
        import_btn.setToolTip(
            "Import accounts and settings from a previously exported file"
        )
        import_btn.clicked.connect(self._import_data)
        ie_btn_layout.addWidget(import_btn)

        ie_layout.addLayout(ie_btn_layout)

        ie_layout.addWidget(
            QLabel("Export includes: accounts, settings, download history, templates")
        )

        ie_layout.addStretch()
        tabs.addTab(import_export_tab, "[Import/Export] Import/Export (Premium)")

        # ===== BACKUP TAB (Premium) =====
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)

        backup_header = QLabel("[Backup] Auto-Backup Settings (Premium Feature)")
        backup_header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        backup_layout.addWidget(backup_header)

        backup_desc = QLabel(
            "Automatically backup your downloaded repositories to a specified location."
        )
        backup_desc.setStyleSheet("color: #888;")
        backup_layout.addWidget(backup_desc)

        backup_enable_layout = QHBoxLayout()
        self.backup_enabled = QCheckBox("Enable Auto-Backup")
        backup_enable_layout.addWidget(self.backup_enabled)
        backup_layout.addLayout(backup_enable_layout)

        backup_dir_layout = QHBoxLayout()
        backup_dir_layout.addWidget(QLabel("Backup Location:"))
        self.backup_dir_input = QLineEdit()
        self.backup_dir_input.setPlaceholderText("Select backup directory")
        backup_dir_layout.addWidget(self.backup_dir_input)
        backup_browse_btn = QPushButton("Browse")
        backup_browse_btn.setToolTip("Select backup destination folder")
        backup_browse_btn.clicked.connect(self._select_backup_dir)
        backup_dir_layout.addWidget(backup_browse_btn)
        backup_layout.addLayout(backup_dir_layout)

        backup_interval_layout = QHBoxLayout()
        backup_interval_layout.addWidget(QLabel("Backup Interval:"))
        self.backup_interval_combo = QComboBox()
        self.backup_interval_combo.addItems(["Daily", "Weekly", "Monthly"])
        backup_interval_layout.addWidget(self.backup_interval_combo)
        backup_layout.addLayout(backup_interval_layout)

        backup_now_btn = QPushButton("Backup Now")
        backup_now_btn.setToolTip(
            "Start backup immediately of all downloaded repositories"
        )
        backup_now_btn.clicked.connect(self._run_backup)
        backup_layout.addWidget(backup_now_btn)

        backup_compress_layout = QHBoxLayout()
        self.backup_compress_check = QCheckBox("Compress backups (ZIP)")
        self.backup_compress_check.setToolTip(
            "Create compressed ZIP archives of backups"
        )
        backup_compress_layout.addWidget(self.backup_compress_check)
        backup_layout.addLayout(backup_compress_layout)

        self.backup_log = QTextEdit()
        self.backup_log.setReadOnly(True)
        self.backup_log.setMaximumHeight(100)
        backup_layout.addWidget(QLabel("Backup Log:"))
        backup_layout.addWidget(self.backup_log)

        tabs.addTab(backup_tab, "[Backup] Backup (Premium)")

        # ===== SETTINGS TAB =====
        settings_tab = QWidget()
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        settings_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        settings_inner = QWidget()
        settings_inner.setStyleSheet("background-color: transparent;")
        settings_layout = QVBoxLayout(settings_inner)
        settings_layout.setSpacing(15)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_scroll.setWidget(settings_inner)
        settings_tab_layout = QVBoxLayout(settings_tab)
        settings_tab_layout.setContentsMargins(0, 0, 0, 0)
        settings_tab_layout.addWidget(settings_scroll)

        rate_group = QGroupBox("Rate Limit Settings")
        rate_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QLabel {
                font-size: 13px;
            }
        """)
        rate_inner = QVBoxLayout()
        rate_inner.setSpacing(8)
        rate_inner.addWidget(QLabel("Max Concurrent Downloads:"))
        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setMinimum(1)
        self.max_concurrent_spin.setMaximum(5)
        self.max_concurrent_spin.setValue(3)
        self.max_concurrent_spin.setToolTip("Maximum number of simultaneous downloads")
        self.max_concurrent_spin.setStyleSheet("padding: 5px; font-size: 13px;")
        rate_inner.addWidget(self.max_concurrent_spin)
        self.auto_switch_check = QCheckBox("Auto-switch accounts when rate limited")
        self.auto_switch_check.setChecked(True)
        self.auto_switch_check.setToolTip(
            "Automatically use another account when one hits rate limit"
        )
        self.auto_switch_check.setStyleSheet("font-size: 13px;")
        rate_inner.addWidget(self.auto_switch_check)
        rate_group.setLayout(rate_inner)
        settings_layout.addWidget(rate_group)

        speed_group = QGroupBox("Speed Limiting")
        speed_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QLabel {
                font-size: 13px;
            }
        """)
        speed_inner = QVBoxLayout()
        speed_inner.setSpacing(8)
        dl_speed_layout = QHBoxLayout()
        dl_speed_layout.addWidget(QLabel("Download Speed Limit:"))
        self.dl_speed_spin = QSpinBox()
        self.dl_speed_spin.setMinimum(0)
        self.dl_speed_spin.setMaximum(100000)
        self.dl_speed_spin.setSingleStep(100)
        self.dl_speed_spin.setValue(0)
        self.dl_speed_spin.setSuffix(" KB/s")
        self.dl_speed_spin.setToolTip("0 = unlimited")
        self.dl_speed_spin.setStyleSheet("padding: 5px; font-size: 13px;")
        self.dl_speed_spin.valueChanged.connect(self._update_speed_label)
        dl_speed_layout.addWidget(self.dl_speed_spin)
        speed_hint = QLabel("(0 = unlimited)")
        speed_hint.setStyleSheet("color: #888; font-size: 12px;")
        dl_speed_layout.addWidget(speed_hint)
        dl_speed_layout.addStretch()
        speed_inner.addLayout(dl_speed_layout)
        self.dl_speed_label = QLabel("Downloads: unlimited")
        self.dl_speed_label.setStyleSheet(
            "color: #888; font-size: 12px; padding-left: 5px;"
        )
        speed_inner.addWidget(self.dl_speed_label)
        speed_group.setLayout(speed_inner)
        settings_layout.addWidget(speed_group)

        # Premium Gate (open now; gating will be added later)
        premium_group = QGroupBox("Premium Gate")
        premium_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        premium_gate_layout = QVBoxLayout()
        premium_gate_layout.setSpacing(8)
        premium_banner = QLabel(
            "Premium features are currently Open. A login/licensing gate will be added later."
        )
        premium_banner.setStyleSheet("color: #888; font-size: 12px;")
        premium_gate_layout.addWidget(premium_banner)
        self.premium_gate_check = QCheckBox("Enable Premium Gate (login/licensing)")
        self.premium_gate_check.setStyleSheet("font-size: 13px;")
        premium_gate_layout.addWidget(self.premium_gate_check)
        premium_group.setLayout(premium_gate_layout)
        settings_layout.addWidget(premium_group)

        # GitHub Enterprise Support
        gh_enterprise_group = QGroupBox("GitHub Enterprise Support")
        gh_enterprise_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        gh_enterprise_layout = QVBoxLayout()
        gh_enterprise_layout.setSpacing(8)
        self.github_enterprise_check = QCheckBox("Enable GitHub Enterprise")
        self.github_enterprise_check.setToolTip("Use custom GitHub Enterprise instance")
        self.github_enterprise_check.setStyleSheet("font-size: 13px;")
        gh_enterprise_layout.addWidget(self.github_enterprise_check)
        gh_enterprise_url_layout = QHBoxLayout()
        gh_enterprise_url_layout.addWidget(QLabel("Enterprise API URL:"))
        self.github_enterprise_url = QLineEdit()
        self.github_enterprise_url.setPlaceholderText(
            "https://github.mycompany.com/api/v3"
        )
        self.github_enterprise_url.setEnabled(False)
        self.github_enterprise_url.setToolTip("Your GitHub Enterprise API URL")
        self.github_enterprise_url.setStyleSheet("padding: 5px; font-size: 12px;")
        gh_enterprise_url_layout.addWidget(self.github_enterprise_url)
        gh_enterprise_layout.addLayout(gh_enterprise_url_layout)
        self.github_enterprise_check.stateChanged.connect(
            lambda state: self.github_enterprise_url.setEnabled(
                state == Qt.CheckState.Checked
            )
        )
        gh_enterprise_group.setLayout(gh_enterprise_layout)
        settings_layout.addWidget(gh_enterprise_group)

        # Backup Options (Premium Features)
        backup_opts_group = QGroupBox("Backup Options")
        backup_opts_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        backup_opts_layout = QVBoxLayout()
        backup_opts_layout.setSpacing(10)

        # Clone type options
        clone_type_row = QHBoxLayout()
        clone_type_row.addWidget(QLabel("Clone Type:"))
        self.clone_type_combo = QComboBox()
        self.clone_type_combo.addItems(["Regular Clone", "Bare Clone", "Mirror Clone"])
        self.clone_type_combo.setToolTip(
            "Bare clones are faster; Mirror includes all refs"
        )
        self.clone_type_combo.setStyleSheet("padding: 5px; font-size: 12px;")
        clone_type_row.addWidget(self.clone_type_combo)
        clone_type_row.addStretch()
        backup_opts_layout.addLayout(clone_type_row)

        # Data to include - two columns
        data_include_label = QLabel("Include in Backup:")
        data_include_label.setStyleSheet(
            "font-weight: bold; font-size: 13px; margin-top: 5px;"
        )
        backup_opts_layout.addWidget(data_include_label)

        check_left = QVBoxLayout()
        check_left.setSpacing(6)
        check_right = QVBoxLayout()
        check_right.setSpacing(6)

        checkbox_style = "font-size: 13px;"

        self.include_issues_check = QCheckBox("Issues (as JSON)")
        self.include_issues_check.setToolTip("Export issues to JSON files")
        self.include_issues_check.setChecked(True)
        self.include_issues_check.setStyleSheet(checkbox_style)
        check_left.addWidget(self.include_issues_check)

        self.include_prs_check = QCheckBox("Pull Requests (as JSON)")
        self.include_prs_check.setToolTip("Export pull requests to JSON files")
        self.include_prs_check.setChecked(True)
        self.include_prs_check.setStyleSheet(checkbox_style)
        check_left.addWidget(self.include_prs_check)

        self.include_releases_check = QCheckBox("Releases & Assets")
        self.include_releases_check.setToolTip("Download releases and their assets")
        self.include_releases_check.setChecked(True)
        self.include_releases_check.setStyleSheet(checkbox_style)
        check_left.addWidget(self.include_releases_check)

        self.include_wiki_check = QCheckBox("Wiki")
        self.include_wiki_check.setToolTip("Clone repository wikis (if available)")
        self.include_wiki_check.setStyleSheet(checkbox_style)
        check_right.addWidget(self.include_wiki_check)

        self.include_gists_check = QCheckBox("Gists")
        self.include_gists_check.setToolTip("Backup user's gists")
        self.include_gists_check.setStyleSheet(checkbox_style)
        check_right.addWidget(self.include_gists_check)

        self.include_starred_check = QCheckBox("Starred Repositories")
        self.include_starred_check.setToolTip("Download starred repos list")
        self.include_starred_check.setStyleSheet(checkbox_style)
        check_right.addWidget(self.include_starred_check)

        self.include_lfs_check = QCheckBox("Git LFS")
        self.include_lfs_check.setToolTip("Download large files via Git LFS")
        self.include_lfs_check.setStyleSheet(checkbox_style)
        check_right.addWidget(self.include_lfs_check)

        checks_grid = QHBoxLayout()
        checks_grid.addLayout(check_left)
        checks_grid.addLayout(check_right)
        backup_opts_layout.addLayout(checks_grid)

        backup_opts_group.setLayout(backup_opts_layout)
        settings_layout.addWidget(backup_opts_group)

        # Scheduled Downloads
        schedule_group = QGroupBox("Scheduled Downloads")
        schedule_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        schedule_layout = QVBoxLayout()
        schedule_layout.setSpacing(8)
        self.scheduled_enabled_check = QCheckBox("Enable Scheduled Downloads")
        self.scheduled_enabled_check.setToolTip(
            "Automatically download queued repos at scheduled time"
        )
        self.scheduled_enabled_check.setStyleSheet("font-size: 13px;")
        schedule_layout.addWidget(self.scheduled_enabled_check)
        schedule_time_layout = QHBoxLayout()
        schedule_time_layout.addWidget(QLabel("Run at:"))
        from PyQt6.QtWidgets import QTimeEdit
        from PyQt6.QtCore import QTime

        self.schedule_time_edit = QTimeEdit()
        self.schedule_time_edit.setDisplayFormat("HH:mm")
        self.schedule_time_edit.setTime(QTime(0, 0))
        self.schedule_time_edit.setEnabled(False)
        self.schedule_time_edit.setStyleSheet("padding: 5px; font-size: 13px;")
        schedule_time_layout.addWidget(self.schedule_time_edit)
        schedule_time_layout.addWidget(QLabel("(24-hour format)"))
        schedule_time_layout.addStretch()
        schedule_layout.addLayout(schedule_time_layout)
        schedule_days_layout = QHBoxLayout()
        schedule_days_layout.addWidget(QLabel("Days:"))
        self.schedule_days = {}
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            cb = QCheckBox(day)
            cb.setEnabled(False)
            cb.setStyleSheet("font-size: 12px;")
            self.schedule_days[day] = cb
            schedule_days_layout.addWidget(cb)
        schedule_days_layout.addStretch()
        schedule_layout.addLayout(schedule_days_layout)
        self.scheduled_enabled_check.stateChanged.connect(
            self._on_schedule_enabled_changed
        )
        schedule_info = QLabel("Download will run if queue has items at scheduled time")
        schedule_info.setStyleSheet("color: #888; font-size: 12px;")
        schedule_layout.addWidget(schedule_info)
        schedule_group.setLayout(schedule_layout)
        settings_layout.addWidget(schedule_group)

        theme_group = QGroupBox("Appearance")
        theme_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        theme_inner = QVBoxLayout()
        theme_inner.setSpacing(8)
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(
            [
                "Dark (Default)",
                "Light",
                "Flame",
                "Lightning",
                "Neon",
                "Cyberpunk",
                "Ocean",
                "Forest",
                "Midnight",
                "Sunset",
            ]
        )
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.setToolTip("Select color theme for the application")
        self.theme_combo.setStyleSheet("padding: 5px; font-size: 12px;")
        self.theme_combo.currentIndexChanged.connect(self._apply_theme)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        theme_inner.addLayout(theme_row)
        self.matrix_check = QCheckBox("Matrix Background Effect")
        self.matrix_check.setChecked(True)
        self.matrix_check.setToolTip("Show animated matrix rain in the background")
        self.matrix_check.setStyleSheet("font-size: 13px;")
        self.matrix_check.stateChanged.connect(self._toggle_matrix)
        theme_inner.addWidget(self.matrix_check)
        theme_group.setLayout(theme_inner)
        settings_layout.addWidget(theme_group)

        compliance_group = QGroupBox("GitHub Policy Compliance")
        compliance_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        compliance_inner = QVBoxLayout()
        compliance_inner.setSpacing(5)
        compliance_label = QLabel(
            "This app complies with GitHub's API policies:\n"
            "- Uses proper User-Agent headers\n"
            "- Respects X-RateLimit-Remaining and Retry-After\n"
            "- Uses API versioning (2022-11-28)\n"
            "- Only requests minimum token scopes (repo, read:user)\n"
            "- Auto-switches accounts before hitting limits"
        )
        compliance_label.setWordWrap(True)
        compliance_label.setStyleSheet(
            "color: #888; font-size: 12px; line-height: 1.4;"
        )
        compliance_inner.addWidget(compliance_label)
        compliance_group.setLayout(compliance_inner)
        settings_layout.addWidget(compliance_group)

        proxy_group = QGroupBox("Proxy Settings")
        proxy_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        proxy_inner = QVBoxLayout()
        proxy_inner.setSpacing(8)
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(QLabel("HTTP Proxy:"))
        self.proxy_http = QLineEdit()
        self.proxy_http.setPlaceholderText(
            "http://host:port (leave empty for no proxy)"
        )
        self.proxy_http.setStyleSheet("padding: 5px; font-size: 12px;")
        proxy_layout.addWidget(self.proxy_http)
        proxy_inner.addLayout(proxy_layout)
        proxy_layout2 = QHBoxLayout()
        proxy_layout2.addWidget(QLabel("SOCKS Proxy:"))
        self.proxy_socks = QLineEdit()
        self.proxy_socks.setPlaceholderText(
            "socks5://host:port (leave empty for no proxy)"
        )
        self.proxy_socks.setStyleSheet("padding: 5px; font-size: 12px;")
        proxy_layout2.addWidget(self.proxy_socks)
        proxy_inner.addLayout(proxy_layout2)
        proxy_group.setLayout(proxy_inner)
        settings_layout.addWidget(proxy_group)

        download_wallet_group = QGroupBox("Download Statistics")
        download_wallet_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        wallet_inner = QHBoxLayout()
        self.total_downloaded_label = QLabel("Total Downloaded: 0 MB")
        self.total_downloaded_label.setStyleSheet("font-size: 13px;")
        wallet_inner.addWidget(self.total_downloaded_label)
        self.reset_wallet_btn = QPushButton("Reset")
        self.reset_wallet_btn.setToolTip("Reset download statistics counter")
        self.reset_wallet_btn.setStyleSheet("padding: 5px 15px; font-size: 12px;")
        self.reset_wallet_btn.clicked.connect(self._reset_download_wallet)
        wallet_inner.addWidget(self.reset_wallet_btn)
        wallet_inner.addStretch()
        download_wallet_group.setLayout(wallet_inner)
        settings_layout.addWidget(download_wallet_group)

        settings_layout.addStretch()
        tabs.addTab(settings_tab, "[Settings] Settings")

        content_layout.addWidget(tabs)

        save_btn = QPushButton("Save Settings")
        save_btn.setToolTip("Save all current settings and preferences")
        save_btn.clicked.connect(self._save_settings)
        content_layout.addWidget(save_btn)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)
        self.status_output.setMaximumHeight(200)
        content_layout.addWidget(self.status_output)

        layout.addWidget(content)
        self.matrix_bg.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.matrix_bg.setGeometry(0, 0, self.width(), self.height())
        self.matrix_bg.raise_()

    def _init_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon_path = None
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
            for c in [
                os.path.join(base, "icons", "app.ico"),
                os.path.join(base, "src", "icons", "app.ico"),
                os.path.join(os.path.dirname(sys.executable), "icons", "app.ico"),
            ]:
                if os.path.exists(c):
                    icon_path = c
                    break
        else:
            icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "..",
                "icons",
                "app.ico",
            )
        if icon_path and os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
            self.setWindowIcon(QIcon(icon_path))
        else:
            default_icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_ComputerIcon
            )
            self.tray.setIcon(default_icon)
            self.setWindowIcon(default_icon)

        # Enhanced tray menu
        menu = QMenu()
        self.tray_show_action = menu.addAction("Show Window", self.show)
        menu.addSeparator()

        # Download status submenu
        self.tray_status_menu = menu.addMenu("[DL] Download Status")
        self.tray_status_menu.addAction("No active downloads")

        menu.addSeparator()
        menu.addAction("Check Rate Limits", self._check_rate_limits)
        menu.addSeparator()

        # Recent downloads submenu
        self.tray_recent_menu = menu.addMenu("[Templates] Recent Downloads")
        self.tray_recent_menu.addAction("No recent downloads")

        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._quit_app)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip(f"GitHub Downloader v{self.VERSION}")
        self.tray.show()

    def _init_shortcuts(self):
        # Existing shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._new_download)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self._process_queue)
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self._toggle_theme)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self._quit_app)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._focus_search)
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(
            self._show_account_breakdown
        )  # Account Breakdown

        # New shortcuts
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(
            self._start_download
        )  # Download
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(
            self._preview_repo
        )  # Preview
        QShortcut(QKeySequence("Ctrl+Shift+B"), self).activated.connect(
            self._start_batch_download
        )  # Batch
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(
            self._start_update
        )  # Update
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(
            lambda: self.download_dir_input.setFocus()
        )  # Focus download dir
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(
            lambda: self.refresh_branches_btn.click()
        )  # Refresh branches

    # --- Drag & Drop ---

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        text = event.mimeData().text()
        if text:
            self.url_input.setText(text.strip())
            self._log(f"Dropped: {text.strip()}")
            self._fetch_repo_info(text.strip())
        event.acceptProposedAction()

    # --- Search ---

    def _do_search(self):
        query = self.search_input.text().strip()
        if not query:
            self._log("Enter a search query")
            return
        self.search_status.setText("Searching...")
        api_url = self._get_api_url()
        self._search_worker = SearchWorker(
            query, self.rate_manager.get_current_token(), api_url
        )
        self._search_worker.results_ready.connect(self._on_search_results)
        self._search_worker.error_occurred.connect(self._on_search_error)
        self._search_worker.start()

    def _on_search_results(self, results: list, authenticated_user: str = ""):
        # Handle both old format (list) and new format (list, str)
        if isinstance(results, tuple):
            results, authenticated_user = results
        self.search_results.clear()
        if not results:
            self.search_status.setText("No results found")
            return
        for r in results:
            stars = r.get("stars", 0)
            lang = r.get("language", "")
            desc = r.get("description", "")[:60]
            topics = r.get("topics", [])
            fork_flag = " [fork]" if r.get("fork") else ""
            priv_flag = " [private]" if r.get("private") else ""
            topic_str = f" [Tag]{' '.join(topics[:3])}" if topics else ""
            text = f"{'*' if stars > 100 else '*'} {r['full_name']}{priv_flag}{fork_flag} ({stars}*) {lang}{topic_str}\n   {desc}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, r)
            self.search_results.addItem(item)
        self.search_status.setText(f"Found {len(results)} results")

    def _on_search_error(self, err: str):
        self.search_status.setText(f"Error: {err}")
        self._log(f"Search error: {err}")

    def _search_result_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.url_input.setText(data.get("clone_url", data.get("full_name", "")))
            self._fetch_repo_info(data.get("full_name", ""))
            self._log(f"Selected: {data.get('full_name', '')}")

    # --- Repo Info ---

    def _get_api_url(self) -> str:
        """Get the current API URL based on settings"""
        if (
            hasattr(self, "github_enterprise_check")
            and self.github_enterprise_check.isChecked()
        ):
            url = self.github_enterprise_url.text().strip()
            if url:
                return get_api_base_url(url)
        return get_api_base_url()

    def _fetch_repo_info(self, owner_repo: str):
        url = owner_repo.strip()
        if url.startswith("http"):
            parts = url.rstrip("/").split("/")
            if len(parts) >= 2:
                owner_repo = f"{parts[-2]}/{parts[-1]}"
        if "/" not in owner_repo:
            return
        self.repo_info_label.setText("Loading repo info...")
        api_url = self._get_api_url()
        self._info_worker = RepoInfoWorker(
            owner_repo, self.rate_manager.get_current_token(), api_url
        )
        self._info_worker.info_ready.connect(self._on_repo_info)
        self._info_worker.error_occurred.connect(self._on_repo_info_error)
        self._info_worker.start()

    def _on_repo_info(self, info: dict):
        topics = info.get("topics", [])
        topic_str = f" | [Tag] {' '.join(topics[:5])}" if topics else ""
        self.repo_info_label.setText(
            f"* {info.get('stars', 0)} stars | "
            f"[Fork] {info.get('forks', 0)} forks | "
            f"[Lang] {info.get('language', 'N/A')} | "
            f"[Templates] {info.get('license', 'None')} | "
            f"[Branch] {info.get('default_branch', 'main')}{topic_str}\n"
            f"{info.get('description', 'No description')}"
        )

    def _on_repo_info_error(self, err: str):
        self.repo_info_label.setText("")

    def _preview_repo(self):
        """Show repository preview with full details"""
        url = self.url_input.text().strip()
        if not url:
            self._log("Enter a repository URL to preview")
            return
        # Extract owner/repo from URL
        if url.startswith("http"):
            parts = url.rstrip("/").split("/")
            if len(parts) >= 2:
                owner_repo = f"{parts[-2]}/{parts[-1]}"
            else:
                return
        else:
            owner_repo = url.rstrip("/")

        self._fetch_repo_info(owner_repo)
        # Also fetch branches/tags
        self._fetch_branches_tags()

    def _fetch_branches_tags(self):
        """Fetch branches and tags for current repo"""
        url = self.url_input.text().strip()
        if not url:
            return

        # Extract owner/repo
        if url.startswith("http"):
            parts = url.rstrip("/").split("/")
            if len(parts) >= 2:
                owner_repo = f"{parts[-2]}/{parts[-1]}"
            else:
                return
        else:
            owner_repo = url.rstrip("/")

        token = self.rate_manager.get_current_token()
        if not token:
            return

        api_url = self._get_api_url()
        self._branches_worker = BranchesWorker(owner_repo, token, api_url)
        self._branches_worker.branches_ready.connect(self._on_branches_ready)
        self._branches_worker.error_occurred.connect(self._on_branches_error)
        self._branches_worker.start()

    def _on_branches_ready(self, branches: list, tags: list):
        """Handle branches/tags loaded"""
        self.branch_combo.blockSignals(True)
        self.branch_combo.clear()

        # Add branches section
        for branch in branches:
            self.branch_combo.addItem(
                f"Branch: {branch}", {"type": "branch", "name": branch}
            )

        # Add tags section
        for tag in tags:
            self.branch_combo.addItem(f"Tag: {tag}", {"type": "tag", "name": tag})

        self.branch_combo.blockSignals(False)
        self._log(f"Loaded {len(branches)} branches and {len(tags)} tags")

    def _on_branches_error(self, err: str):
        self._log(f"Branches error: {err}")

    def _on_branch_changed(self, text: str):
        """Handle branch/tag selection"""
        pass  # Currently just stores the selection

    # --- Recent Downloads ---
    def _add_recent_download(self, url: str):
        """Add a URL to the recent downloads list"""
        # Get existing recent list
        recent = getattr(self, "recent_downloads", [])

        # Remove if already exists (to move to top)
        if url in recent:
            recent.remove(url)

        # Add to front
        recent.insert(0, url)

        # Keep max 20
        if len(recent) > 20:
            recent = recent[:20]

        self.recent_downloads = recent

        # Update UI
        self._update_recent_list()

        # Save to settings
        self._save_settings()

    def _update_recent_list(self):
        """Update the recent downloads list widget"""
        self.recent_list.clear()
        recent = getattr(self, "recent_downloads", [])
        for url in recent:
            # Extract repo name
            if "/" in url:
                name = url.rstrip("/").split("/")[-1]
                if name.endswith(".git"):
                    name = name[:-4]
            else:
                name = url
            self.recent_list.addItem(f"[Files] {name}  ({url})")

    def _run_backup_extras(self, task, repo_dir: str):
        """Run additional backup operations after repo download"""
        if not hasattr(self, "include_issues_check"):
            return

        if not any(
            [
                self.include_issues_check.isChecked(),
                self.include_prs_check.isChecked(),
                self.include_releases_check.isChecked(),
                self.include_wiki_check.isChecked(),
                self.include_gists_check.isChecked(),
                self.include_starred_check.isChecked(),
            ]
        ):
            return

        self._log(f"Running backup extras for {task.repo_url}...")

        # Parse owner/repo from URL
        url = task.repo_url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]
        parts = url.rsplit("/", 2)
        if len(parts) >= 2:
            owner = parts[-2]
            repo_name = parts[-1]
        else:
            return

        # Get token from task or use current
        token = (
            getattr(task, "account_token", None)
            or self.rate_manager.get_current_token()
        )

        # Create API instance
        api_url = self._get_api_url()
        from .github_api import GitHubAPIClient, AuthType

        api = GitHubAPIClient(token, auth_type=AuthType.PAT if token else AuthType.NONE)

        # Create backup worker
        backup = BackupWorker(api, token, repo_dir)
        backup.set_progress_callback(lambda m: self._log(f"  {m}"))

        # Run backups
        if self.include_issues_check.isChecked():
            backup.backup_issues(owner, repo_name, repo_dir)
        if self.include_prs_check.isChecked():
            backup.backup_pull_requests(owner, repo_name, repo_dir)
        if self.include_releases_check.isChecked():
            backup.backup_releases(owner, repo_name, repo_dir, download_assets=True)
        if self.include_wiki_check.isChecked():
            backup.backup_wiki(owner, repo_name, repo_dir)

        # Account-level backups (gists, starred)
        username = self._account_usernames.get(task.account_id, owner)
        if self.include_gists_check.isChecked():
            backup.backup_gists(username, repo_dir)
        if self.include_starred_check.isChecked():
            backup.backup_starred(username, repo_dir)

        # Handle LFS
        if self.include_lfs_check.isChecked():
            self._log("  Git LFS: Use 'git lfs install' and 'git lfs pull' in repo")

        self._log(f"Backup extras completed for {repo_name}")

    def _recent_item_clicked(self, item):
        """Handle click on recent download"""
        text = item.text()
        # Extract URL from the item text
        if "(" in text and ")" in text:
            url = text.split("(")[-1].rstrip(")")
            self.url_input.setText(url)
            self._preview_repo()
            self._log(f"Loaded: {url}")

    def _redownload_selected(self):
        """Redownload the selected recent item"""
        current = self.recent_list.currentItem()
        if current:
            self._recent_item_clicked(current)
            # Auto-start download
            self._start_download()

    def _clear_recent(self):
        """Clear recent downloads list"""
        self.recent_downloads = []
        self._update_recent_list()
        self._save_settings()
        self._log("Recent downloads cleared")

    # --- Download Status Tracking ---

    def _refresh_download_status(self):
        """Refresh the download status display"""
        # Count items in queue
        queued = 0
        completed = 0
        downloading = 0

        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            text = item.text()
            if text.startswith("[Wait]"):
                queued += 1
            elif text.startswith("[Done]"):
                completed += 1
            elif text.startswith("[Sync]") or text.startswith("[DL]"):
                downloading += 1

        # Also count recent downloads as completed
        recent_completed = len(getattr(self, "recent_downloads", []))
        total_completed = completed + recent_completed

        self.status_label.setText(
            f"Queued: {queued} | Downloading: {downloading} | Completed: {total_completed}"
        )
        self._log(
            f"Status: {queued} queued, {downloading} downloading, {total_completed} completed"
        )

    def _show_completed_repos(self):
        """Show a dialog with all completed repos"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Completed Downloads")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)

        # Get completed repos from queue
        completed_repos = []
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            text = item.text()
            if text.startswith("[Done]"):
                # Extract repo name from text like "[Done] https://github.com/owner/repo - Completed"
                if " - Completed" in text:
                    repo_url = (
                        text.replace("[Done] ", "").replace(" - Completed", "").strip()
                    )
                    completed_repos.append(repo_url)

        # Add from recent downloads
        recent = getattr(self, "recent_downloads", [])
        for url in recent:
            if url not in completed_repos:
                completed_repos.append(url)

        # Create list widget
        list_widget = QListWidget()
        for repo in completed_repos:
            list_widget.addItem(f"[Done] {repo}")
        layout.addWidget(QLabel(f"Total completed: {len(completed_repos)} repos"))
        layout.addWidget(list_widget)

        close_btn = QPushButton("Close")
        close_btn.setToolTip("Close this dialog")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def _track_queued_download(self):
        """Track when repos are queued for download"""
        self.repos_queued_count = 0
        self.last_queue_time = datetime.now()
        # Will be updated when repos are added to queue

    # --- Account Repo Breakdown ---

    def _show_account_breakdown(self):
        """Show breakdown of repos per account - what's queued, completed, total"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Account Repository Breakdown")
        dialog.setMinimumSize(700, 500)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("<b>Checking repos from GitHub API... please wait</b>"))
        dialog.show()
        QApplication.processEvents()

        # Get accounts
        accounts = self.rate_manager.accounts
        if not accounts:
            QMessageBox.warning(self, "No Accounts", "No accounts configured")
            dialog.close()
            return

        # Get completed repos from recent_downloads
        completed_repos = set()
        recent = getattr(self, "recent_downloads", [])
        for url in recent:
            # Extract owner/repo from URL
            if "github.com" in url:
                parts = (
                    url.rstrip("/")
                    .replace("https://github.com/", "")
                    .replace("http://github.com/", "")
                    .split("/")
                )
                if len(parts) >= 2:
                    completed_repos.add(f"{parts[0]}/{parts[1]}")

        # Get repos in current queue
        queued_repos = set()
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            text = item.text()
            if text.startswith("[Wait]"):
                # Extract repo name from text like "[Wait] owner/repo"
                repo_name = text.replace("[Wait] ", "").strip()
                queued_repos.add(repo_name)

        # Check each account
        results = []
        total_all_repos = 0

        for acc_id, acc_data in accounts.items():
            username = acc_data.get("username", acc_id)
            token = acc_data.get("token", "")

            # Fetch repos from GitHub API for this account (type=owner to get user's repos)
            try:
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": f"GitHubDownloader/{VERSION}",
                }

                # Paginate through all repos
                all_repos = []
                page = 1
                while page <= 10:  # Max 10 pages = 1000 repos
                    resp = requests.get(
                        f"https://api.github.com/user/repos?per_page=100&page={page}&type=owner&sort=updated",
                        headers=headers,
                        timeout=30,
                    )
                    if resp.status_code != 200:
                        break
                    repos_page = resp.json()
                    if not repos_page:
                        break
                    all_repos.extend(repos_page)
                    page += 1

                if resp.status_code == 200:
                    # Get ALL repos (including forks) for total count
                    all_repos_count = len(all_repos)

                    # Count private vs public (among owned/non-fork repos)
                    private_count = sum(
                        1
                        for r in all_repos
                        if r.get("private", False) and not r.get("fork", False)
                    )
                    public_count = sum(
                        1
                        for r in all_repos
                        if not r.get("private", False) and not r.get("fork", False)
                    )

                    # Filter: repos owned (not forks) - these are eligible for download
                    owned_repos = [r for r in all_repos if not r.get("fork", False)]

                    # Count completed, queued, and build remaining list
                    acc_completed = 0
                    acc_queued = 0
                    remaining_list = []

                    for r in owned_repos:
                        full_name = r.get("full_name", "")
                        if full_name in completed_repos:
                            acc_completed += 1
                        elif full_name in queued_repos:
                            acc_queued += 1
                        else:
                            remaining_list.append(full_name)

                    results.append(
                        {
                            "username": username,
                            "total": all_repos_count,  # Show ALL repos (including forks) in total
                            "owned": len(owned_repos),  # Also show owned repos count
                            "private": private_count,  # Private repos owned
                            "public": public_count,  # Public repos owned
                            "completed": acc_completed,
                            "queued": acc_queued,
                            "remaining": len(remaining_list),
                            "remaining_list": remaining_list,
                        }
                    )
                    total_all_repos += all_repos_count
                else:
                    results.append(
                        {
                            "username": username,
                            "total": 0,
                            "completed": 0,
                            "queued": 0,
                            "remaining": 0,
                            "error": f"API error: {resp.status_code}",
                        }
                    )
            except Exception as e:
                results.append(
                    {
                        "username": username,
                        "total": 0,
                        "completed": 0,
                        "queued": 0,
                        "remaining": 0,
                        "error": str(e),
                    }
                )

        # Close the "please wait" message and show results
        dialog.close()

        # Create results dialog
        results_dialog = QDialog(self)
        results_dialog.setWindowTitle("Account Repository Breakdown")
        results_dialog.setMinimumSize(700, 500)
        results_layout = QVBoxLayout(results_dialog)

        # Summary
        total_completed = len(completed_repos)
        total_queued = len(queued_repos)
        results_layout.addWidget(
            QLabel(
                f"<b>Summary:</b> Total repos from all accounts: {total_all_repos} | "
                f"Downloaded: {total_completed} | Queued: {total_queued} | "
                f"Remaining: {total_all_repos - total_completed - total_queued}"
            )
        )

        results_layout.addWidget(QLabel(""))

        # Table
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(
            [
                "Account",
                "Total",
                "Owned",
                "Private",
                "Public",
                "DL'd",
                "Queued",
                "Remain",
            ]
        )
        table.setRowCount(len(results))
        table.horizontalHeader().setStretchLastSection(True)

        for i, r in enumerate(results):
            table.setItem(i, 0, QTableWidgetItem(r["username"]))
            table.setItem(i, 1, QTableWidgetItem(str(r["total"])))
            table.setItem(i, 2, QTableWidgetItem(str(r.get("owned", "-"))))
            table.setItem(i, 3, QTableWidgetItem(str(r.get("private", "-"))))
            table.setItem(i, 4, QTableWidgetItem(str(r.get("public", "-"))))
            table.setItem(i, 5, QTableWidgetItem(str(r["completed"])))
            table.setItem(i, 6, QTableWidgetItem(str(r["queued"])))
            table.setItem(i, 7, QTableWidgetItem(str(r.get("remaining", "-"))))

            # Highlight accounts with remaining repos
            if r.get("remaining", 0) > 0:
                for col in range(8):
                    table.item(i, col).setBackground(
                        QColor("#4a3000")
                    )  # Dark yellow for pending

            # Show error if any
            if r.get("error"):
                table.setItem(i, 7, QTableWidgetItem(f"ERROR: {r['error']}"))

        results_layout.addWidget(table)

        # Button to queue all remaining repos
        btn_layout = QHBoxLayout()
        queue_all_btn = QPushButton("Queue All Remaining Repos")
        queue_all_btn.setToolTip("Add all remaining repos to download queue")
        queue_all_btn.clicked.connect(
            lambda: self._queue_remaining_repos(results, completed_repos, queued_repos)
        )
        btn_layout.addWidget(queue_all_btn)
        btn_layout.addStretch()
        results_layout.addLayout(btn_layout)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(results_dialog.close)
        results_layout.addWidget(close_btn)

        # Store results for queue function
        self._current_breakdown_results = results

        results_dialog.exec()

    def _show_all_repos_including_forks(self):
        """Show ALL repos including forks, private repos, and starred repos from ALL accounts"""
        dialog = QDialog(self)
        dialog.setWindowTitle("All Repositories (Including Forks, Private & Starred)")
        dialog.setMinimumSize(950, 650)
        layout = QVBoxLayout(dialog)

        # Show loading message
        loading_label = QLabel(
            "<b>Fetching ALL repositories from GitHub API...<br>"
            "Including: owned repos, forks, private repos, and starred repos<br>"
            "This may take a moment for accounts with many repos.</b>"
        )
        loading_label.setStyleSheet("color: #58a6ff; padding: 20px;")
        layout.addWidget(loading_label)
        dialog.show()
        QApplication.processEvents()

        accounts = self.rate_manager.accounts
        if not accounts:
            QMessageBox.warning(self, "No Accounts", "No accounts configured")
            dialog.close()
            return

        # Fetch ALL repos from all accounts (including forks and private)
        all_repos_data = []  # List of dicts with repo info + account info
        starred_repos_data = []  # List of starred repos
        account_starred_sets = {}  # Track which accounts starred which repos

        for acc_id, acc_data in accounts.items():
            username = acc_data.get("username", acc_id)
            token = acc_data.get("token", "")
            api_url = self._get_api_url()

            try:
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": f"GitHubDownloader/{VERSION}",
                }

                # Fetch repos with pagination - include forks and private
                page = 1
                while page <= 10:  # Max 10 pages = 1000 repos per account
                    resp = requests.get(
                        f"{api_url}/user/repos?per_page=100&page={page}&sort=updated&affiliation=owner,collaborator,organization_member",
                        headers=headers,
                        timeout=30,
                    )
                    if resp.status_code != 200:
                        self._log(
                            f"Error fetching repos for {username}: {resp.status_code}"
                        )
                        break
                    repos_page = resp.json()
                    if not repos_page:
                        break

                    for r in repos_page:
                        r["_account_token"] = token
                        r["_account_username"] = username
                        r["_repo_source"] = "owned"
                        all_repos_data.append(r)

                    page += 1

                self._log(
                    f"Fetched {len([r for r in all_repos_data if r.get('_account_username') == username])} repos from {username}"
                )

                # Fetch STARRED repos for this account
                starred_page = 1
                starred_count = 0
                while starred_page <= 10:
                    starred_resp = requests.get(
                        f"{api_url}/user/starred?per_page=100&page={starred_page}",
                        headers=headers,
                        timeout=30,
                    )
                    if starred_resp.status_code != 200:
                        self._log(
                            f"Error fetching starred repos for {username}: {starred_resp.status_code}"
                        )
                        break
                    starred_page_data = starred_resp.json()
                    if not starred_page_data:
                        break

                    for r in starred_page_data:
                        r["_account_token"] = token
                        r["_account_username"] = username
                        r["_repo_source"] = "starred"
                        r["_starred_by"] = username
                        starred_repos_data.append(r)
                        starred_count += 1

                    starred_page += 1

                self._log(f"Fetched {starred_count} starred repos from {username}")
                account_starred_sets[username] = starred_count

            except Exception as e:
                self._log(f"Error fetching repos for {username}: {e}")

        # Close loading dialog
        dialog.close()

        if not all_repos_data and not starred_repos_data:
            QMessageBox.information(self, "No Repos", "No repositories found")
            return

        # Create results dialog
        results_dialog = QDialog(self)
        results_dialog.setWindowTitle(
            f"All Repositories ({len(all_repos_data) + len(starred_repos_data)} total)"
        )
        results_dialog.setMinimumSize(1000, 700)
        results_layout = QVBoxLayout(results_dialog)

        # Summary info
        total_owned = sum(1 for r in all_repos_data if not r.get("fork", False))
        total_forks = sum(1 for r in all_repos_data if r.get("fork", False))
        total_private = sum(1 for r in all_repos_data if r.get("private", False))
        total_public = sum(1 for r in all_repos_data if not r.get("private", False))
        total_starred = len(starred_repos_data)

        summary_label = QLabel(
            f"<b>Summary:</b> Total: {len(all_repos_data) + total_starred} | "
            f"Owned: {total_owned} | Forks: {total_forks} | "
            f"Private: {total_private} | Public: {total_public} | "
            f"<font color='#f0c040'>Starred: {total_starred}</font>"
        )
        results_layout.addWidget(summary_label)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        filter_input = QLineEdit()
        filter_input.setPlaceholderText("Search repos by name...")
        filter_input.textChanged.connect(lambda: None)  # Placeholder for refresh
        filter_layout.addWidget(filter_input)
        filter_layout.addStretch()

        include_forks_check = QCheckBox("Include Forks")
        include_forks_check.setChecked(True)
        include_forks_check.setToolTip("Show repositories you have forked")
        filter_layout.addWidget(include_forks_check)

        include_private_check = QCheckBox("Include Private")
        include_private_check.setChecked(True)
        include_private_check.setToolTip("Show private repositories")
        filter_layout.addWidget(include_private_check)

        include_starred_check = QCheckBox("Include Starred")
        include_starred_check.setChecked(True)
        include_starred_check.setToolTip("Show repositories you have starred")
        filter_layout.addWidget(include_starred_check)

        results_layout.addLayout(filter_layout)

        # Create table
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(
            [
                "Source",
                "Account",
                "Name",
                "Fork",
                "Private",
                "Stars",
                "Language",
                "Size",
                "Last Updated",
            ]
        )
        table.setRowCount(len(all_repos_data))
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)

        # Store all repos data for filtering
        table._all_repos = all_repos_data
        table._starred_repos = starred_repos_data
        table._filter_input = filter_input
        table._include_forks = include_forks_check
        table._include_private = include_private_check
        table._include_starred = include_starred_check

        def populate_table():
            """Populate table based on current filters"""
            filter_text = filter_input.text().lower()
            include_forks = include_forks_check.isChecked()
            include_private = include_private_check.isChecked()
            include_starred = include_starred_check.isChecked()

            filtered_repos = []

            # Add owned repos
            for r in all_repos_data:
                if (
                    (include_forks or not r.get("fork", False))
                    and (include_private or not r.get("private", False))
                    and (filter_text in r.get("full_name", "").lower())
                ):
                    filtered_repos.append(r)

            # Add starred repos (that aren't already in owned repos)
            owned_full_names = {r.get("full_name", "") for r in all_repos_data}
            for r in starred_repos_data:
                full_name = r.get("full_name", "")
                if (
                    (include_starred)
                    and (include_forks or not r.get("fork", False))
                    and (include_private or not r.get("private", False))
                    and (filter_text in full_name.lower())
                    and full_name not in owned_full_names
                ):
                    filtered_repos.append(r)

            table.setRowCount(len(filtered_repos))
            for i, r in enumerate(filtered_repos):
                # Source indicator
                repo_source = r.get("_repo_source", "owned")
                source_text = "*" if repo_source == "starred" else "[Files]"
                source_item = QTableWidgetItem(source_text)
                source_item.setToolTip(
                    "Starred by you"
                    if repo_source == "starred"
                    else "Owned/Forked repository"
                )
                table.setItem(i, 0, source_item)

                table.setItem(i, 1, QTableWidgetItem(r.get("_account_username", "")))
                name_item = QTableWidgetItem(r.get("full_name", ""))
                if r.get("fork", False):
                    name_item.setForeground(QColor("#888888"))  # Gray for forks
                if repo_source == "starred":
                    name_item.setForeground(QColor("#f0c040"))  # Gold for starred
                table.setItem(i, 2, name_item)
                table.setItem(i, 3, QTableWidgetItem("Yes" if r.get("fork") else "No"))
                table.setItem(
                    i, 4, QTableWidgetItem("Yes" if r.get("private") else "No")
                )
                table.setItem(i, 5, QTableWidgetItem(str(r.get("stargazers_count", 0))))
                table.setItem(i, 6, QTableWidgetItem(r.get("language") or "-"))
                table.setItem(i, 7, QTableWidgetItem(f"{r.get('size', 0)} KB"))
                table.setItem(
                    i,
                    8,
                    QTableWidgetItem(
                        r.get("updated_at", "")[:10] if r.get("updated_at") else "-"
                    ),
                )

                # Highlight starred repos in gold
                if repo_source == "starred":
                    for col in range(9):
                        table.item(i, col).setBackground(QColor("#3d3520"))  # Dark gold
                # Highlight forks
                elif r.get("fork", False):
                    for col in range(9):
                        table.item(i, col).setBackground(QColor("#2a2a2a"))  # Dark gray

        # Connect filter changes
        filter_input.textChanged.connect(lambda: populate_table())
        include_forks_check.stateChanged.connect(lambda: populate_table())
        include_private_check.stateChanged.connect(lambda: populate_table())
        include_starred_check.stateChanged.connect(lambda: populate_table())

        populate_table()
        table.resizeColumnsToContents()
        results_layout.addWidget(table)

        # Button row
        btn_layout = QHBoxLayout()

        download_selected_btn = QPushButton("[v] Download Selected")
        download_selected_btn.setToolTip("Download selected repositories")
        download_selected_btn.clicked.connect(
            lambda: self._download_selected_from_table(table, all_repos_data)
        )
        btn_layout.addWidget(download_selected_btn)

        add_to_queue_btn = QPushButton("Add to Queue")
        add_to_queue_btn.setToolTip("Add selected repos to download queue")
        add_to_queue_btn.clicked.connect(
            lambda: self._add_selected_to_queue_from_table(table, all_repos_data)
        )
        btn_layout.addWidget(add_to_queue_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setToolTip("Close this dialog")
        close_btn.clicked.connect(results_dialog.close)
        btn_layout.addWidget(close_btn)

        results_layout.addLayout(btn_layout)

        results_dialog.exec()

    def _download_selected_from_table(self, table, all_repos_data):
        """Download repos selected in the table"""
        selected_rows = set(item.row() for item in table.selectedItems())
        if not selected_rows:
            QMessageBox.information(
                self, "No Selection", "Please select repositories to download"
            )
            return

        # Get the filtered repos (need to reconstruct which repos are visible)
        filter_text = table._filter_input.text().lower()
        include_forks = table._include_forks.isChecked()
        include_private = table._include_private.isChecked()

        filtered_repos = [
            r
            for r in all_repos_data
            if (include_forks or not r.get("fork", False))
            and (include_private or not r.get("private", False))
            and (filter_text in r.get("full_name", "").lower())
        ]

        selected_repos = [
            filtered_repos[row] for row in selected_rows if row < len(filtered_repos)
        ]

        if not selected_repos:
            return

        count = 0
        for r in selected_repos:
            full_name = r.get("full_name", "")
            token = r.get("_account_token", "")
            username = r.get("_account_username", "")

            clone_url = f"https://github.com/{full_name}.git"
            task = DownloadTask(
                clone_url,
                output_dir=self.download_dir_input.text(),
                account_id=username,
                branch=None,
                submodules=self.submodules_check.isChecked(),
                shallow=self.shallow_check.isChecked(),
                clone_type=self.clone_type_combo.currentIndex(),
            )
            task.status = "queued"
            task.account_token = token

            item = QListWidgetItem(f"[Wait] {full_name}")
            item.setData(Qt.ItemDataRole.UserRole, {"task": task, "token": token})
            self.queue_list.addItem(item)
            count += 1

        self._log(f"Added {count} repos to queue")
        self._notify("Repos Queued", f"{count} repositories added to queue")
        QMessageBox.information(
            self, "Queued", f"{count} repositories added to download queue"
        )

        if not self.active_workers:
            QTimer.singleShot(500, self._process_queue)

    def _add_selected_to_queue_from_table(self, table, all_repos_data):
        """Add selected repos to queue without starting download"""
        self._download_selected_from_table(table, all_repos_data)

    def _queue_remaining_repos(self, results, completed_repos, queued_repos):
        """Queue all remaining repos for download"""
        count = 0

        for r in results:
            username = r.get("username", "")
            remaining_list = r.get("remaining_list", [])

            # Get token for this account
            token = ""
            for acc_id, acc_data in self.rate_manager.accounts.items():
                if acc_data.get("username") == username:
                    token = acc_data.get("token", "")
                    break

            if not token:
                continue

            for full_name in remaining_list:
                # Check if already downloaded or queued
                if full_name in completed_repos or full_name in queued_repos:
                    continue

                # Construct clone URL
                clone_url = f"https://github.com/{full_name}.git"

                task = DownloadTask(
                    clone_url,
                    output_dir=self.download_dir_input.text(),
                    account_id=username,
                    branch=None,
                    submodules=self.submodules_check.isChecked(),
                    shallow=self.shallow_check.isChecked(),
                )
                task.status = "queued"

                # Add to queue
                item = QListWidgetItem(f"[Wait] {full_name}")
                item.setData(Qt.ItemDataRole.UserRole, {"task": task, "token": token})
                self.queue_list.addItem(item)
                count += 1
                queued_repos.add(full_name)  # Prevent duplicates within this batch

        if count > 0:
            self._log(f"Queued {count} remaining repos for download")
            self._notify("Repos Queued", f"{count} repositories added to queue")
            if not self.active_workers:
                QTimer.singleShot(500, self._process_queue)

    def _show_selective_download(self):
        """Show dialog to select specific repos to download"""
        if not self.rate_manager.accounts:
            QMessageBox.warning(self, "No Accounts", "No accounts configured")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Selective Download - Choose Repos")
        dialog.setMinimumSize(600, 500)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("<b>Select repositories to download:</b>"))
        dialog.show()
        QApplication.processEvents()

        # Fetch all repos from all accounts
        all_repos = []
        for acc_id, acc_data in self.rate_manager.accounts.items():
            token = acc_data.get("token", "")
            username = acc_data.get("username", acc_id)
            api_url = self._get_api_url()
            try:
                from .github_api import GitHubAPIClient, AuthType

                api = GitHubAPIClient(
                    token,
                    auth_type=AuthType.PAT if token else AuthType.NONE,
                    api_url=api_url,
                )
                resp = api.session.get(
                    f"{api.BASE_URL}/users/{username}/repos",
                    params={"per_page": 100, "type": "owner"},
                )
                if resp.status_code == 200:
                    repos = resp.json()
                    # Filter out forks
                    for r in repos:
                        if not r.get("fork", False):
                            r["_account_token"] = token
                            r["_account_username"] = username
                            all_repos.append(r)
            except Exception as e:
                self._log(f"Error fetching repos for {username}: {e}")

        dialog.close()

        # Create selection dialog
        select_dialog = QDialog(self)
        select_dialog.setWindowTitle("Select Repos to Download")
        select_dialog.setMinimumSize(600, 500)
        select_layout = QVBoxLayout(select_dialog)

        # Show count
        select_layout.addWidget(
            QLabel(f"Found {len(all_repos)} owned repositories (excluding forks):")
        )

        # Create searchable list
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        search_input = QLineEdit()
        search_input.setPlaceholderText("Filter repos by name...")
        search_layout.addWidget(search_input)
        select_layout.addLayout(search_layout)

        # Table with checkboxes
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["", "Name", "Private", "Language", "Stars"])
        table.setRowCount(len(all_repos))

        for i, r in enumerate(all_repos):
            checkbox = QTableWidgetItem()
            checkbox.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            )
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(i, 0, checkbox)
            table.setItem(i, 1, QTableWidgetItem(r.get("full_name", "")))
            table.setItem(i, 2, QTableWidgetItem("[OK]" if r.get("private") else ""))
            table.setItem(i, 3, QTableWidgetItem(r.get("language", "-")))
            table.setItem(i, 4, QTableWidgetItem(str(r.get("stargazers_count", 0))))

        table.resizeColumnsToContents()
        select_layout.addWidget(table)

        # Filter function
        def filter_table(text):
            for row in range(table.rowCount()):
                name_item = table.item(row, 1)
                if name_item:
                    name = name_item.text().lower()
                    table.setRowHidden(row, text.lower() not in name)

        search_input.textChanged.connect(filter_table)

        # Buttons
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")

        def select_all():
            for row in range(table.rowCount()):
                table.item(row, 0).setCheckState(Qt.CheckState.Checked)

        select_all_btn.clicked.connect(select_all)
        btn_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")

        def deselect_all():
            for row in range(table.rowCount()):
                table.item(row, 0).setCheckState(Qt.CheckState.Unchecked)

        deselect_all_btn.clicked.connect(deselect_all)
        btn_layout.addWidget(deselect_all_btn)

        download_btn = QPushButton("Download Selected")
        download_btn.setDefault(True)

        def download_selected():
            count = 0
            for row in range(table.rowCount()):
                checkbox = table.item(row, 0)
                if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                    r = all_repos[row]
                    full_name = r.get("full_name", "")
                    clone_url = r.get(
                        "clone_url", f"https://github.com/{full_name}.git"
                    )
                    token = r.get("_account_token", "")
                    username = r.get("_account_username", "")

                    task = DownloadTask(
                        clone_url,
                        output_dir=self.download_dir_input.text(),
                        account_id=username,
                        branch=r.get("default_branch"),
                        submodules=self.submodules_check.isChecked(),
                        shallow=self.shallow_check.isChecked(),
                    )
                    task.status = "queued"

                    item = QListWidgetItem(f"[Wait] {full_name}")
                    item.setData(
                        Qt.ItemDataRole.UserRole, {"task": task, "token": token}
                    )
                    self.queue_list.addItem(item)
                    count += 1
                    # Store account token in task for backup extras
                    task.account_token = token

            if count > 0:
                self._log(f"Queued {count} selected repos for download")
                self._notify("Repos Queued", f"{count} repositories added to queue")
                if not self.active_workers:
                    QTimer.singleShot(500, self._process_queue)
            select_dialog.close()

        download_btn.clicked.connect(download_selected)
        btn_layout.addWidget(download_btn)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(select_dialog.close)
        btn_layout.addWidget(cancel_btn)

        select_layout.addLayout(btn_layout)
        select_dialog.exec()

    # --- Download Logic ---

    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self._log("Enter a repository URL")
            return
        self._queue_download(url)

    def _start_batch_download(self):
        text = self.batch_input.toPlainText().strip()
        if not text:
            self._log("Enter URLs in the batch input field")
            return

        urls = [line.strip() for line in text.split("\n") if line.strip()]
        if not urls:
            self._log("No valid URLs found")
            return

        self._log(f"Queueing {len(urls)} downloads...")
        for url in urls:
            self._queue_download(url)
            time.sleep(0.3)  # Small delay between queue additions

        self._log(f"Added {len(urls)} downloads to queue")
        # Clear the batch input
        self.batch_input.clear()

    def _queue_download(self, url: str):
        """Add a single download to the queue"""
        token = self.rate_manager.get_current_token()
        task = DownloadTask(
            url,
            output_dir=self.download_dir_input.text(),
            account_id=self.rate_manager.current_account,
            account_token=token,
            branch=self.branch_combo.currentText().strip() or None,
            shallow=self.shallow_check.isChecked(),
            submodules=self.submodules_check.isChecked(),
            clone_type=self.clone_type_combo.currentIndex(),
        )
        task.status = "queued"
        task.started_at = datetime.now()

        # Add to queue list widget
        item = QListWidgetItem(f"[Wait] {url}")
        item.setData(Qt.ItemDataRole.UserRole, {"task": task, "token": token})
        self.queue_list.addItem(item)

        # Auto-start if no active downloads
        if not self.active_workers:
            self._process_queue()

    def _start_update(self):
        url = self.url_input.text().strip()
        if not url:
            self._log("Enter a repository URL to update")
            return
        clean_url = url
        if clean_url.startswith("http"):
            clean_url = clean_url.rstrip("/")
            parts = clean_url.rsplit("/", 2)
            repo_name = parts[-1].replace(".git", "") if len(parts) >= 2 else "unknown"
        else:
            repo_name = clean_url.split("/")[-1].replace(".git", "")
        target_dir = os.path.join(self.download_dir_input.text(), repo_name)
        if not os.path.isdir(os.path.join(target_dir, ".git")):
            self._log(f"Not a git repo: {target_dir}. Use Download instead.")
            return
        token = self.rate_manager.get_current_token()
        task = DownloadTask(
            url,
            output_dir=self.download_dir_input.text(),
            account_id=self.rate_manager.current_account,
            account_token=token,
            clone_type=self.clone_type_combo.currentIndex(),
        )
        task.status = "updating"
        task.started_at = datetime.now()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        worker = DownloadWorker(
            task,
            token,
            mode="pull",
            speed_limit_kb=self.dl_speed_spin.value(),
            clone_type=self.clone_type_combo.currentIndex(),
        )
        worker.progress_updated.connect(self._on_download_progress)
        worker.download_finished.connect(self._on_download_finished)
        self.active_workers[url] = worker
        worker.start()
        self._log(f"Updating: {url}")

    def _check_all_updates(self):
        """Check all repos in download directory for updates"""
        download_dir = self.download_dir_input.text()
        if not os.path.isdir(download_dir):
            self._log(f"Download directory not found: {download_dir}")
            return

        repos_found = []
        for item in os.listdir(download_dir):
            full_path = os.path.join(download_dir, item)
            if os.path.isdir(full_path) and os.path.isdir(
                os.path.join(full_path, ".git")
            ):
                # Try to get the remote URL from .git/config
                git_config = os.path.join(full_path, ".git", "config")
                remote_url = None
                if os.path.isfile(git_config):
                    try:
                        with open(git_config, "r", encoding="utf-8") as f:
                            config = f.read()
                            # Look for [remote "origin"] and fetch URL
                            in_remote = False
                            for line in config.split("\n"):
                                line = line.strip()
                                if line.startswith("[") and "remote" in line:
                                    in_remote = "origin" in line or "remote" in line
                                if in_remote and line.startswith("url ="):
                                    remote_url = line.split("=", 1)[1].strip()
                                    break
                    except:
                        pass

                if remote_url:
                    repos_found.append((item, remote_url))
                else:
                    self._log(f"Skipping {item}: no remote URL found")

        if not repos_found:
            self._log("No downloaded repositories with remote URLs found")
            return

        self._log(f"Checking {len(repos_found)} repos for updates...")

        # Get current token
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account selected - cannot check for updates")
            return

        # Add each repo to queue for updating
        count = 0
        for repo_name, remote_url in sorted(repos_found):
            task = DownloadTask(
                remote_url,
                output_dir=download_dir,
                account_id=self.rate_manager.current_account,
            )
            task.status = "queued"

            # Add to queue with token
            item = QListWidgetItem(f"[R] {repo_name}")
            item.setData(Qt.ItemDataRole.UserRole, {"task": task, "token": token})
            self.queue_list.addItem(item)
            count += 1

        self._log(f"Added {count} repos to queue for update checking")
        self._notify("Update Check", f"Added {count} repos to queue for update check")

        # Automatically start processing the queue
        if not self.active_workers:
            self._process_queue()

    def _on_download_progress(self, url: str, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.eta_label.setText(msg)
        self.status_bar.showMessage(msg)
        # Extract repo name from URL and show in current download label
        if "/" in url:
            repo_name = url.rstrip("/").split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            self.current_download_label.setText(f"Downloading: {repo_name}")
        else:
            self.current_download_label.setText(f"Downloading: {url}")

    def _on_download_finished(self, url: str, success: bool, result: str):
        self.progress_bar.setVisible(False)
        self.eta_label.setText("")
        if url in self.active_workers:
            del self.active_workers[url]
        # Extract repo name for display
        if "/" in url:
            repo_name = url.rstrip("/").split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
        else:
            repo_name = url
        if success:
            self._log(f"Done: {repo_name} -> {result}")
            self._notify("Download Complete", f"{repo_name} saved to {result}")
            # Removed: self._open_folder(result) - Don't open explorer after download
            self.current_download_label.setText(f"Completed: {repo_name}")
        else:
            self._log(f"Failed: {url} - {result}")
            self._notify("Download Failed", result)
            self.current_download_label.setText(f"Failed: {repo_name} - {result}")
        self._update_queue_list()

    # --- Queue ---

    def _add_to_queue(self):
        url = self.url_input.text().strip()
        if not url:
            self._log("Enter a repository URL")
            return

        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account selected")
            return

        task = DownloadTask(
            url,
            output_dir=self.download_dir_input.text(),
            account_id=self.rate_manager.current_account,
            branch=self.branch_combo.currentText().strip() or None,
            shallow=self.shallow_check.isChecked(),
            submodules=self.submodules_check.isChecked(),
        )
        task.status = "queued"  # Set to queued so _process_queue can find it

        # Add to widget with token
        item = QListWidgetItem(f"[Wait] {url}")
        item.setData(Qt.ItemDataRole.UserRole, {"task": task, "token": token})
        self.queue_list.addItem(item)

        self._log(f"Queued: {url}")

    def _update_queue_list(self):
        """Sync queue list widget with download_queue list"""
        if not hasattr(self, "queue_list"):
            return

        # Only update if there are items in download_queue that aren't in the widget
        # This prevents overwriting items we just added directly to the widget
        existing_items = set()
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            if item:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data and data.get("task"):
                    existing_items.add(id(data.get("task")))

        # Add any tasks from download_queue that aren't in the widget
        for task in self.download_queue:
            if id(task) not in existing_items:
                item = QListWidgetItem(f"[Wait] {task.repo_url}")
                token = None
                if self.rate_manager.current_account:
                    token = self.rate_manager.get_current_token()
                item.setData(Qt.ItemDataRole.UserRole, {"task": task, "token": token})
                self.queue_list.addItem(item)

    def _process_queue(self):
        """Process items in the queue list widget"""
        debug_log("_process_queue ENTER")
        self._log_to_file("_process_queue called")
        try:
            # Check if there are any queued items (skip completed/failed)
            has_queued = False
            queued_count = 0
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                if item:
                    data = item.data(Qt.ItemDataRole.UserRole)
                    if data and data.get("task"):
                        status = data["task"].status
                        if status == "queued":
                            has_queued = True
                            queued_count += 1

            print(f"DEBUG: Found {queued_count} queued items", file=sys.stderr)
            self._log_to_file(f"Found {queued_count} queued items")

            if not has_queued:
                self._log("No queued items in queue")
                print("DEBUG: No queued items", file=sys.stderr)
                return

            token = self.rate_manager.get_current_token()
            print(
                f"DEBUG: Current token: {'present' if token else 'MISSING'}",
                file=sys.stderr,
            )
            self._log_to_file(f"Current token present: {bool(token)}")

            # If no token, try to find one from any account
            if not token and self.rate_manager.accounts:
                for acc_id, acc_data in self.rate_manager.accounts.items():
                    acc_token = acc_data.get("token", "")
                    if acc_token:
                        token = acc_token
                        print(
                            f"DEBUG: Using token from account {acc_id}", file=sys.stderr
                        )
                        self._log_to_file(f"Using token from account: {acc_id}")
                        break

            if not token:
                self._log("No account configured - add a GitHub account first")
                self._log_to_file("ERROR: No token available")
                print("DEBUG: No token available", file=sys.stderr)
                # Don't return - we can still try to clone public repos without token
                # But warn the user

            # Find the first queued item (skip completed/failed)
            found_item = False
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                if not item:
                    continue
                data = item.data(Qt.ItemDataRole.UserRole)
                if not data:
                    continue

                task = data.get("task")
                if not task:
                    continue

                # Skip items that are already completed, failed, or downloading
                if task.status not in ("queued",):
                    continue

                found_item = True
                print(f"DEBUG: Starting download for {task.repo_url}", file=sys.stderr)
                self._log_to_file(f"Starting download: {task.repo_url}")

                # Use token from data if available, otherwise use current token
                item_token = data.get("token") or token
                if not item_token:
                    print(
                        f"DEBUG: WARNING - No token for {task.repo_url} - will attempt anonymous clone",
                        file=sys.stderr,
                    )
                    self._log_to_file(f"WARNING: No token for {task.repo_url}")

                # Mark as downloading
                task.status = "downloading"
                item.setText(f"[v] {task.repo_url}")

                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)

                # Get speed limit
                speed_limit = self.dl_speed_spin.value()
                clone_type = self.clone_type_combo.currentIndex()

                print(f"DEBUG: Creating DownloadWorker", file=sys.stderr)
                worker = DownloadWorker(
                    task,
                    item_token,
                    mode="clone",
                    speed_limit_kb=speed_limit,
                    clone_type=clone_type,
                )
                print(f"DEBUG: Connecting signals", file=sys.stderr)
                worker.progress_updated.connect(self._on_download_progress)
                worker.download_finished.connect(self._on_queue_download_finished)
                self.active_workers[task.repo_url] = worker

                print(f"DEBUG: Starting worker thread", file=sys.stderr)
                worker.start()
                self.rate_manager.record_request()

                limit_kb = self.dl_speed_spin.value()
                speed_desc = f" (limit: {limit_kb} KB/s)" if limit_kb else ""
                self._log(f"Starting: {task.repo_url}{speed_desc}")
                print(f"DEBUG: Worker started successfully", file=sys.stderr)
                break

            if not found_item:
                print("DEBUG: No queued items found in loop", file=sys.stderr)
                self._log_to_file("No queued items found in loop")
        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            self._log(f"Error in _process_queue: {e}")
            self._log_to_file(f"ERROR in _process_queue: {e}\n{tb}")
            debug_log(f"_process_queue error: {e}\n{tb}")
        debug_log("_process_queue EXIT")

    def _on_queue_download_finished(self, url: str, success: bool, result: str):
        """Handle download finish from queue"""
        self.progress_bar.setVisible(False)

        # Update the queue item
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue

            task = data.get("task")
            if task and task.repo_url == url:
                if success:
                    item.setText(f"[Done] {url} - Completed")
                    task.status = (
                        "completed"  # Mark as completed so it won't be re-downloaded
                    )
                    self._log(f"[OK] Downloaded: {url}")
                    # Add to recent downloads
                    self._add_recent_download(url)
                    # Show desktop notification
                    self._show_notification(
                        "Download Complete", f"Successfully downloaded {url}"
                    )
                    # Refresh status display
                    self._refresh_download_status()
                    # Run backup extras if enabled
                    self._run_backup_extras(task, result)
                else:
                    item.setText(f"[Error] {url} - Failed: {result}")
                    self._log(f"[FAIL] Failed: {url} - {result}")
                break

        if url in self.active_workers:
            del self.active_workers[url]

        # Process next item in queue
        QTimer.singleShot(500, self._process_queue)

    def _clear_completed(self):
        """Remove completed/failed items from queue"""
        for i in range(self.queue_list.count() - 1, -1, -1):
            item = self.queue_list.item(i)
            text = item.text()
            if text.startswith("[Done]") or text.startswith("[Error]"):
                self.queue_list.takeItem(i)

    # --- Push ---

    def _select_push_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Git Repository", "")
        if folder:
            self.push_dir_input.setText(folder)

    def _stage_and_commit(self):
        repo_dir = self.push_dir_input.text().strip()
        msg = self.commit_msg_input.text().strip()
        if not repo_dir:
            self._log("Select a local repository first")
            return
        if not msg:
            self._log("Enter a commit message")
            return
        self._push_worker = PushWorker(
            repo_dir, msg, self.rate_manager.get_current_token()
        )
        self._push_worker.progress_updated.connect(
            lambda s: self.push_progress.setText(s)
        )
        self._push_worker.push_finished.connect(self._on_push_done)
        self._push_worker.start()

    def _push_to_github(self):
        repo_dir = self.push_dir_input.text().strip()
        msg = self.commit_msg_input.text().strip()
        if not repo_dir:
            self._log("Select a local repository first")
            return
        if not msg:
            self._log("Enter a commit message")
            return
        token = self.rate_manager.get_current_token()
        self._push_worker = PushWorker(repo_dir, msg, token)
        self._push_worker.progress_updated.connect(
            lambda s: self.push_progress.setText(s)
        )
        self._push_worker.push_finished.connect(self._on_push_done)
        self._push_worker.start()
        self._log("Pushing...")

    def _on_push_done(self, success: bool, message: str):
        self.push_progress.setText(message)
        if success:
            self._log(f"Push successful: {message}")
        else:
            self._log(f"Push failed: {message}")

    # --- Directory ---

    def _select_download_directory(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", self.download_dir_input.text()
        )
        if folder:
            self.download_dir_input.setText(folder)
            self._log(f"Download directory: {folder}")

    def _open_download_folder(self):
        folder = self.download_dir_input.text()
        if os.path.isdir(folder):
            os.startfile(folder)
        else:
            os.makedirs(folder, exist_ok=True)
            os.startfile(folder)

    # --- Account Management ---

    def _show_add_account_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add GitHub Account")
        dialog.setFixedSize(540, 380)
        layout = QVBoxLayout(dialog)

        auth_tabs = QTabWidget()
        # --- PAT Tab ---
        pat_tab = QWidget()
        pat_layout = QVBoxLayout(pat_tab)

        pat_layout.addWidget(QLabel("Personal Access Token:"))
        token_input = QLineEdit()
        token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        pat_layout.addWidget(token_input)

        info_label = QLabel(
            "Create a token at: github.com/settings/tokens\n"
            "Required scopes: repo, read:user\n"
            "This app complies with GitHub's API policies."
        )
        info_label.setStyleSheet("color: gray; font-size: 11px;")
        pat_layout.addWidget(info_label)

        self._token_status = QLabel("")
        pat_layout.addWidget(self._token_status)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Account")
        add_btn.setEnabled(False)
        add_btn.clicked.connect(lambda: self._add_account(token_input.text(), dialog))
        btn_layout.addWidget(add_btn)
        test_btn = QPushButton("Validate Token")
        btn_layout.addWidget(test_btn)
        pat_layout.addLayout(btn_layout)

        token_input.textChanged.connect(
            lambda text: add_btn.setEnabled(len(text.strip()) >= 10)
        )
        test_btn.clicked.connect(
            lambda: self._validate_token(token_input.text().strip())
        )
        auth_tabs.addTab(pat_tab, "[Key] Token (PAT)")

        # --- OAuth Device Flow Tab ---
        oauth_tab = QWidget()
        oauth_layout = QVBoxLayout(oauth_tab)

        oauth_info = QLabel(
            "OAuth Device Flow authenticates via GitHub's browser-based login.\n"
            "A code will be generated - enter it on github.com/login/device\n\n"
            "This grants the same permissions as a PAT (repo, read:user)\n"
            "but you never paste a token - more secure!"
        )
        oauth_info.setStyleSheet("color: gray; font-size: 11px;")
        oauth_info.setWordWrap(True)
        oauth_layout.addWidget(oauth_info)

        self._oauth_status = QLabel("Click 'Start OAuth Login' to begin")
        self._oauth_status.setStyleSheet("color: gray;")
        oauth_layout.addWidget(self._oauth_status)

        self._oauth_code_label = QLabel("")
        self._oauth_code_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #58a6ff; padding: 10px;"
        )
        self._oauth_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        oauth_layout.addWidget(self._oauth_code_label)

        oauth_btn = QPushButton("Start OAuth Login")
        oauth_btn.clicked.connect(self._start_oauth_flow)
        oauth_layout.addWidget(oauth_btn)

        auth_tabs.addTab(oauth_tab, "[Web] OAuth Device Flow")

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.close)
        layout.addWidget(auth_tabs)
        layout.addWidget(cancel_btn)

        dialog.exec()

    def _validate_token(self, token: str):
        if not token:
            self._token_status.setText("Enter a token first")
            self._token_status.setStyleSheet("color: orange;")
            return
        self._token_status.setText("Validating...")
        self._token_status.setStyleSheet("color: gray;")
        api_url = self._get_api_url()
        self._validator = TokenValidator(token, api_url=api_url)
        self._validator.result_ready.connect(self._on_token_validated)
        self._validator.start()

    def _on_token_validated(self, account_id: str, success: bool, info: dict):
        if success:
            scopes = info.get("scopes", "")
            self._token_status.setText(
                f"[OK] Valid token for: {info.get('login', 'Unknown')} | Scopes: {scopes or 'default'}"
            )
            self._token_status.setStyleSheet("color: green;")
        else:
            self._token_status.setText(f"[FAIL] {info.get('error', 'Invalid token')}")
            self._token_status.setStyleSheet("color: red;")

    def _start_oauth_flow(self):
        self._oauth_status.setText("Starting OAuth device flow...")
        self._oauth_code_label.setText("")
        self._oauth_worker = OAuthDeviceFlowWorker()
        self._oauth_worker.code_ready.connect(self._on_oauth_code)
        self._oauth_worker.token_ready.connect(self._on_oauth_token)
        self._oauth_worker.error_occurred.connect(self._on_oauth_error)
        self._oauth_worker.start()

    def _on_oauth_code(self, user_code: str, verify_uri: str):
        self._oauth_code_label.setText(user_code)
        self._oauth_status.setText(f"Go to {verify_uri} and enter the code above")
        self._oauth_status.setStyleSheet("color: #58a6ff;")

    def _on_oauth_token(self, token: str, username: str):
        self._oauth_status.setText(f"[OK] Authenticated as {username}")
        self._oauth_status.setStyleSheet("color: green;")
        self._oauth_code_label.setText("[OK] Success!")
        account_id = f"{username}_{int(time.time())}"
        self.rate_manager.add_account(account_id, token, username)
        self.rate_manager.accounts[account_id]["remaining"] = 5000
        self.account_manager.add_account(account_id, token, username)
        self._update_account_selector()
        self._refresh_accounts_list()
        self._save_settings()
        self._log(f"Added OAuth account: {username}")

    def _on_oauth_error(self, err: str):
        self._oauth_status.setText(f"[FAIL] {err}")
        self._oauth_status.setStyleSheet("color: red;")
        self._oauth_code_label.setText("")

    # --- Bulk Download ---

    def _download_all_repos(self, account_id: str = None):
        """Download repos from specific account or all accounts"""
        debug_log(f"_download_all_repos ENTER - account_id={account_id}")
        self._log_to_file(f"_download_all_repos: account_id={account_id}")

        if account_id:
            # Download from specific account
            account = self.rate_manager.accounts.get(account_id)
            if not account:
                self._log(f"Account not found: {account_id}")
                self._log_to_file(f"Account not found in rate_manager: {account_id}")
                debug_log(f"_download_all_repos: Account not found: {account_id}")
                return
            token = account["token"]
            account_name = account.get("name", account_id)
            self._log(f"Fetching repositories for {account_name}...")
            self._log_to_file(
                f"Fetching repos for {account_name} (token present: {bool(token)})"
            )
            debug_log(f"_download_all_repos: Creating ListReposWorker for {account_name} (token present: {bool(token)})")

            # Fetch ORG repos in addition to user repos for complete coverage
            orgs_repos = []
            if "orgs" in account:
                for org_login in account["orgs"]:
                    orgs_repos.extend(self._fetch_org_repos(org_login, token))
            
            api_url = self._get_api_url()
            self._repos_worker = ListReposWorker(
                token, repo_type="all", api_url=api_url
            )
            # Use functools.partial for cleaner signal connection
            from functools import partial

            self._repos_worker.results_ready.connect(
                partial(
                    self._on_repos_listed,
                    account_id=account_id,
                    account_name=account_name,
                )
            )
            self._repos_worker.error_occurred.connect(self._on_repos_error)
            print(f"DEBUG: Starting worker thread for {account_name}", file=sys.stderr)
            self._repos_worker.start()
            print(f"DEBUG: Worker started", file=sys.stderr)
        else:
            # Download from ALL accounts
            self._download_all_accounts()

    def _download_all_accounts(self):
        """Download repos from all accounts"""
        print("DEBUG: _download_all_accounts ENTER", file=sys.stderr)
        self._log_to_file("=" * 60)
        self._log_to_file("_download_all_accounts CALLED")
        self._log_to_file(f"Accounts: {list(self.rate_manager.accounts.keys())}")

        if not self.rate_manager.accounts:
            self._log("No accounts configured")
            self._log_to_file("No accounts - returning early")
            return

        self._log(f"Fetching repos from {len(self.rate_manager.accounts)} accounts...")
        self._all_accounts_repos = []
        self._accounts_to_fetch = list(self.rate_manager.accounts.keys())
        self._all_accounts_fetch_complete = False  # Guard to prevent double-call

        self._log_to_file(
            f"Starting multi-account fetch with {len(self._accounts_to_fetch)} accounts"
        )

        try:
            self._fetch_next_account_repos()
        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            self._log(f"Error: {type(e).__name__}: {e}")
            self._log_to_file(f"EXCEPTION in _download_all_accounts: {e}\n{tb}")
        print("DEBUG: _download_all_accounts EXIT", file=sys.stderr)

    def _fetch_next_account_repos(self):
        """Fetch repos from next account in queue - gets all public + private repos created by user"""
        self._log_to_file(
            f"_fetch_next_account_repos: accounts remaining = {len(self._accounts_to_fetch)}"
        )
        print(
            f"DEBUG: _fetch_next_account_repos ENTER, accounts left: {len(self._accounts_to_fetch)}",
            file=sys.stderr,
        )
        try:
            QCoreApplication.processEvents()
        except Exception as e:
            print(f"DEBUG: processEvents error: {e}", file=sys.stderr)

        if not self._accounts_to_fetch:
            self._log_to_file("All accounts processed - calling final handler")
            print("DEBUG: No more accounts to fetch", file=sys.stderr)
            if self._all_accounts_fetch_complete:
                print("DEBUG: Already complete, skipping", file=sys.stderr)
                return
            self._all_accounts_fetch_complete = True
            print("DEBUG: Calling _on_all_accounts_repos_fetched", file=sys.stderr)
            self._on_all_accounts_repos_fetched()
            return

        acc_id = self._accounts_to_fetch.pop(0)
        self._log_to_file(
            f"Processing account: {acc_id} ({len(self._accounts_to_fetch)} remaining)"
        )
        print(
            f"DEBUG: Popped account {acc_id}, {len(self._accounts_to_fetch)} left",
            file=sys.stderr,
        )
        account = self.rate_manager.accounts.get(acc_id)
        if not account:
            self._log_to_file(f"Account not found: {acc_id} - skipping")
            print(f"DEBUG: Account {acc_id} not found", file=sys.stderr)
            QTimer.singleShot(0, self._fetch_next_account_repos)
            return

        token = account["token"]
        account_name = account.get("name", acc_id)
        print(f"DEBUG: Creating worker for {account_name}", file=sys.stderr)

        # Store current account info for signal handlers
        self._current_fetch_account_id = acc_id
        self._current_fetch_account_name = account_name

        # Create worker
        worker = ListReposWorker(token, repo_type="all", api_url=self._get_api_url())
        self._current_repos_worker = worker

        # FIX: Pass account info directly via closure to avoid race condition
        # (Using instance variables causes issues when workers overlap)
        from functools import partial

        def on_repos_ready(repos, auth_user, acc_id, acc_name):
            """Wrapper to pass account info directly"""
            self._on_repos_fetched(repos, auth_user, acc_id, acc_name)

        def on_fetch_err(err, acc_id, acc_name):
            """Wrapper to pass account info directly"""
            self._on_fetch_error(err, acc_id, acc_name)

        worker.results_ready.connect(
            partial(on_repos_ready, acc_id=acc_id, acc_name=account_name)
        )
        worker.error_occurred.connect(
            partial(on_fetch_err, acc_id=acc_id, acc_name=account_name)
        )

        # Comprehensive logging
        self._log_to_file(f"[{account_name}] Starting worker to fetch repos...")
        print(f"DEBUG: Starting worker thread for {account_name}", file=sys.stderr)
        worker.start()
        print(f"DEBUG: Worker started, returning", file=sys.stderr)

    def _on_repos_fetched(self, repos, authenticated_user, account_id, account_name):
        """Handle repos fetched from worker"""
        self._log_to_file(f"[{account_name}] Received {len(repos)} repos from API")
        print(
            f"DEBUG: _on_repos_fetched ENTER with {len(repos)} repos, authenticated_user={authenticated_user}",
            file=sys.stderr,
        )
        try:
            # Merge org repos with user repos for complete coverage
            account = self.rate_manager.accounts.get(account_id, {})
            token = account.get("token", "")
            orgs = account.get("orgs", [])
            if orgs:
                org_repos = []
                for org_login in orgs:
                    org_repos.extend(self._fetch_org_repos(org_login, token))
                repos = repos + org_repos
                self._log_to_file(f"[{account_name}] Added {len(org_repos)} org repos (total: {len(repos)})")
            
            # Use authenticated_user from API instead of cached username
            self._on_single_account_repos(repos, account_id, authenticated_user)
        except Exception as e:
            self._log_to_file(f"[{account_name}] Error processing repos: {e}")
            print(f"DEBUG: _on_repos_fetched error: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc()
            # Still advance to next account on error
            QTimer.singleShot(0, self._fetch_next_account_repos)
        print(f"DEBUG: _on_repos_fetched EXIT", file=sys.stderr)

    def _on_fetch_error(self, err, account_id=None, account_name="Unknown"):
        """Handle fetch error"""
        self._log_to_file(f"[{account_name}] ERROR: {err}")
        print(f"DEBUG: _on_fetch_error ENTER: {err}", file=sys.stderr)
        self._log(f"  -> Error fetching {account_name}: {err}")
        QTimer.singleShot(0, self._fetch_next_account_repos)
        print(f"DEBUG: _on_fetch_error EXIT", file=sys.stderr)

    def _on_single_account_repos(
        self, repos: list, account_id: str, authenticated_user: str
    ):
        """Handle repos fetched from single account - filter out forks to comply with GitHub ToS"""
        account = self.rate_manager.accounts.get(account_id, {})
        token = account.get("token", "")

        # Use authenticated_user from API response (this is the actual GitHub user for this token)
        actual_username = authenticated_user or account_id
        print(
            f"DEBUG: _on_single_account_repos - account_id={account_id}, actual_username={actual_username}",
            file=sys.stderr,
        )

        # Detailed debug: show all repos with their fork status
        fork_count = 0
        owner_count = 0
        for r in repos:
            if r.get("fork", False):
                fork_count += 1
            else:
                owner_count += 1

        self._log(
            f"DEBUG: Got {len(repos)} repos from {actual_username}: {owner_count} owned, {fork_count} forks"
        )
        self._log_to_file(
            f"[{actual_username}] API returned {len(repos)} repos: {owner_count} owned, {fork_count} forks"
        )

        # Filter out forked repos AND filter by actual owner (only repos owned by this user)
        filtered_repos = []
        for r in repos:
            # Exclude forks
            if r.get("fork", False):
                continue
            # Only include repos where the owner matches the authenticated user
            repo_owner = r.get("owner", {}).get("login", "")
            if repo_owner == actual_username:
                filtered_repos.append(r)
            else:
                self._log_to_file(
                    f"[{actual_username}] Excluded (wrong owner): {r.get('full_name')} (owner: {repo_owner})"
                )

        self._log(
            f"DEBUG: After owner filter: {len(filtered_repos)} repos for {actual_username}"
        )
        self._log_to_file(
            f"[{actual_username}] After filtering: {len(filtered_repos)} repos queued"
        )

        # Store repos with their account's token
        for r in filtered_repos:
            r["_account_token"] = token
            r["_account_name"] = actual_username

        self._all_accounts_repos.extend(filtered_repos)
        self._log(
            f"  -> Found {len(filtered_repos)} repos for {actual_username} ({len(repos)} total)"
        )
        self._log_to_file(
            f"[{actual_username}] Added {len(filtered_repos)} to queue. Total queue: {len(self._all_accounts_repos)}"
        )
        # Use QTimer to avoid recursive call blocking - schedule next fetch asynchronously
        QTimer.singleShot(0, self._fetch_next_account_repos)

    def _on_all_accounts_repos_fetched(self):
        """Add all fetched repos to download queue"""
        print("DEBUG: _on_all_accounts_repos_fetched ENTER", file=sys.stderr)
        self._log_to_file("=" * 60)
        self._log_to_file("_on_all_accounts_repos_fetched - ALL DONE!")
        self._log_to_file(f"Total repos to queue: {len(self._all_accounts_repos)}")
        self._log(
            f"DEBUG: _on_all_accounts_repos_fetched called with {len(self._all_accounts_repos)} repos"
        )

        # Show per-account breakdown
        account_counts = {}
        for r in self._all_accounts_repos:
            acc_name = r.get("_account_name", "unknown")
            account_counts[acc_name] = account_counts.get(acc_name, 0) + 1
        self._log_to_file(f"Per-account breakdown: {account_counts}")

        count = 0
        try:
            for r in self._all_accounts_repos:
                # Parse owner from full_name (e.g., "username/repo" -> "username")
                full_name = r.get("full_name", "")
                owner = full_name.split("/")[0] if "/" in full_name else "unknown"

                task = DownloadTask(
                    r["clone_url"],
                    output_dir=self.download_dir_input.text(),
                    account_id=owner,
                    branch=r.get("default_branch"),
                    submodules=self.submodules_check.isChecked(),
                    shallow=self.shallow_check.isChecked(),
                )
                task.status = "queued"  # CRITICAL - must set status!

                # Add directly to queue list widget with correct token for this account
                item = QListWidgetItem(f"[Wait] {r['full_name']}")
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"task": task, "token": r.get("_account_token", "")},
                )
                self.queue_list.addItem(item)
                count += 1
        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            self._log(f"Error adding repos to queue: {e}")
            self._log_to_file(f"ERROR adding repos to queue: {e}\n{tb}")
            print(f"DEBUG: Error adding repos: {e}\n{tb}", file=sys.stderr)

        self._all_accounts_repos = []
        self._log(f"Queued {count} repos from ALL accounts (public + private)")
        self._log_to_file(f"SUCCESS: Queued {count} repos total")
        self._log_to_file("=" * 60)

        # Auto-start queue processing
        if not self.active_workers and count > 0:
            QTimer.singleShot(500, self._process_queue)

        try:
            self._notify(
                "Repos Queued", f"{count} repositories from all accounts added to queue"
            )
        except Exception as e:
            print(f"DEBUG: _notify error: {e}", file=sys.stderr)

        # Refresh status display
        try:
            self._refresh_download_status()
        except Exception as e:
            print(f"DEBUG: _refresh_download_status error: {e}", file=sys.stderr)

        print("DEBUG: _on_all_accounts_repos_fetched EXIT", file=sys.stderr)

    def _download_starred_repos(self):
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("Add a GitHub account first")
            return
        self._log("Fetching your starred repositories...")
        api_url = self._get_api_url()
        self._repos_worker = ListReposWorker(
            token, repo_type="starred", api_url=api_url
        )
        self._repos_worker.results_ready.connect(self._on_starred_listed)
        self._repos_worker.error_occurred.connect(self._on_repos_error)
        self._repos_worker.start()

    def _on_repos_listed(
        self,
        repos: list,
        account_id: str = None,
        account_name: str = None,
        authenticated_user: str = "",
    ):
        """Handle repos listed - optionally from specific account"""
        debug_log(
            f"_on_repos_listed ENTER - repos={len(repos) if isinstance(repos, list) else repos}, account_id={account_id}, account_name={account_name}, authenticated_user={authenticated_user}"
        )
        self._log_to_file(
            f"_on_repos_listed: repos={len(repos) if isinstance(repos, list) else 'tuple'}, account_id={account_id}, authenticated_user={authenticated_user}"
        )

        # Handle new format where repos is a tuple (repos, authenticated_user)
        if isinstance(repos, tuple):
            repos, authenticated_user = repos
            debug_log(
                f"_on_repos_listed: Unpacked tuple - repos={len(repos)}, authenticated_user={authenticated_user}"
            )

        if account_id is None:
            account_id = self.rate_manager.current_account
            debug_log(
                f"_on_repos_listed: account_id was None, using current_account: {account_id}"
            )
        if account_name is None:
            account_name = account_id

        # Get token for this account
        account = self.rate_manager.accounts.get(account_id, {})
        token = account.get("token", "")
        debug_log(
            f"_on_repos_listed: Got token for {account_id}: {'present' if token else 'MISSING'}"
        )

        # Use authenticated_user from API response (this is the actual GitHub user for this token)
        actual_username = authenticated_user or self._account_usernames.get(
            account_id, account_name
        )
        debug_log(f"_on_repos_listed: actual_username={actual_username}")

        # Filter repos - include forks but only repos owned by this user
        filtered_repos = []
        fork_count = 0
        wrong_owner_count = 0
        for r in repos:
            # Count forks but include them (user wants all repos including forks)
            if r.get("fork", False):
                fork_count += 1
            # Only include repos owned by this user
            repo_owner = r.get("owner", {}).get("login", "")
            if repo_owner == actual_username:
                filtered_repos.append(r)
            else:
                wrong_owner_count += 1
                if wrong_owner_count <= 3:  # Log first few
                    self._log_to_file(
                        f"Excluded wrong owner: {r.get('full_name')} owner={repo_owner} expected={actual_username}"
                    )

        debug_log(
            f"_on_repos_listed: Filtering complete - {len(filtered_repos)} kept, {fork_count} forks excluded, {wrong_owner_count} wrong owner"
        )
        self._log_to_file(
            f"Filtering: {len(filtered_repos)} kept, {fork_count} forks, {wrong_owner_count} wrong owner"
        )
        self._log(
            f"Filtered: {len(filtered_repos)} owned repos from {len(repos)} total"
        )

        count = 0
        for r in filtered_repos:
            task = DownloadTask(
                r["clone_url"],
                output_dir=self.download_dir_input.text(),
                account_id=account_id,
                branch=r.get("default_branch"),
                submodules=self.submodules_check.isChecked(),
                shallow=self.shallow_check.isChecked(),
            )
            task.status = "queued"  # Set status so _process_queue can find it

            # Add directly to queue_list widget with token
            item = QListWidgetItem(f"[Wait] {r['full_name']}")
            item.setData(Qt.ItemDataRole.UserRole, {"task": task, "token": token})
            self.queue_list.addItem(item)
            count += 1

        self._log(f"Queued {count} repos from {account_name} (public + private)")
        self._notify(
            "Repos Queued", f"{count} repositories from {account_name} added to queue"
        )

        # Refresh status display
        self._refresh_download_status()

        # Auto-start queue processing
        if not self.active_workers and count > 0:
            QTimer.singleShot(500, self._process_queue)

    def _on_starred_listed(self, repos: list, authenticated_user: str = ""):
        # Handle both old format (list) and new format (list, str)
        if isinstance(repos, tuple):
            repos, authenticated_user = repos
        count = 0
        for r in repos:
            task = DownloadTask(
                r["clone_url"],
                output_dir=self.download_dir_input.text(),
                account_id=self.rate_manager.current_account,
                branch=r.get("default_branch"),
                submodules=self.submodules_check.isChecked(),
            )
            self.download_queue.append(task)
            count += 1
        self._update_queue_list()
        self._log(f"Queued {count} starred repos")
        self._notify("Starred Queued", f"{count} starred repos added to queue")

    def _on_repos_error(self, err: str):
        self._log(f"Error fetching repos: {err}")

    def _add_account(self, token: str, dialog: QDialog):
        if not token or len(token) < 10:
            self._log("Invalid token")
            QMessageBox.warning(self, "Error", "Please enter a valid GitHub token")
            return
        if HAS_REQUESTS:
            try:
                headers = github_headers(token)
                resp = requests.get(
                    "https://api.github.com/user", headers=headers, timeout=10
                )
                self.rate_manager.handle_rate_limit_response(resp)
                if resp.status_code != 200:
                    QMessageBox.warning(
                        self,
                        "Invalid Token",
                        f"Token validation failed: {resp.status_code}",
                    )
                    return
                username = resp.json().get("login", "unknown")
                rate_remaining = resp.headers.get("X-RateLimit-Remaining", "5000")
            except Exception:
                username = f"account_{len(self.rate_manager.accounts) + 1}"
                rate_remaining = "5000"
        else:
            username = f"account_{len(self.rate_manager.accounts) + 1}"
            rate_remaining = "5000"

        account_id = f"{username}_{int(time.time())}"
        self.rate_manager.add_account(account_id, token, username)
        if rate_remaining.isdigit():
            self.rate_manager.accounts[account_id]["remaining"] = int(rate_remaining)
        
        # Store orgs for this account
        try:
            headers = github_headers(token)
            resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if resp.status_code == 200:
                user_data = resp.json()
                orgs = [org["login"] for org in user_data.get("orgs", [])]
                if orgs:
                    self.rate_manager.accounts[account_id]["orgs"] = orgs
                    self._log(f"Stored {len(orgs)} orgs for {username}")
        except Exception as e:
            self._log(f"Failed to fetch orgs: {e}")
        
        self.account_manager.add_account(account_id, token, username)
        self._update_account_selector()
        self._refresh_accounts_list()
        self._save_settings()
        self._log(f"Added account: {username}")
        dialog.close()

    def _remove_selected_account(self):
        rows = self.accounts_table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        status = self.rate_manager.get_status()
        accounts = list(status["accounts"].keys())
        if row < len(accounts):
            account_id = accounts[row]
            self.rate_manager.remove_account(account_id)
            self.account_manager.remove_account(account_id)
            self._update_account_selector()
            self._refresh_accounts_list()
            self._log(f"Removed account: {account_id}")

    def _download_from_selected_account(self):
        """Download repos from the selected account in the table"""
        debug_log("_download_from_selected_account ENTER")
        self._log_to_file("_download_from_selected_account called")

        rows = self.accounts_table.selectionModel().selectedRows()
        if not rows:
            # No selection, try current account
            if self.rate_manager.current_account:
                debug_log(
                    f"_download_from_selected_account: No row selected, using current_account: {self.rate_manager.current_account}"
                )
                self._log_to_file(
                    f"No row selected, using current_account: {self.rate_manager.current_account}"
                )
                self._download_all_repos(self.rate_manager.current_account)
            else:
                self._log("Select an account or add one first")
                self._log_to_file("No account selected and no current_account")
            return

        row = rows[0].row()
        status = self.rate_manager.get_status()
        accounts = list(status["accounts"].keys())
        debug_log(
            f"_download_from_selected_account: Selected row={row}, accounts={accounts}"
        )
        self._log_to_file(f"Selected row={row}, accounts={accounts}")

        if row < len(accounts):
            account_id = accounts[row]
            debug_log(
                f"_download_from_selected_account: Calling _download_all_repos with account_id={account_id}"
            )
            self._log_to_file(f"Calling _download_all_repos({account_id})")
            self._download_all_repos(account_id)

    def _on_account_changed(self, index):
        if index >= 0:
            account_id = self.account_selector.itemData(index)
            if account_id and self.rate_manager.switch_account(account_id):
                self._log(
                    f"Switched to: {self.rate_manager.accounts.get(account_id, {}).get('name', account_id)}"
                )
                self._update_rate_display()

    def _update_account_selector(self):
        self.account_selector.clear()
        status = self.rate_manager.get_status()
        for acc_id, acc_info in status["accounts"].items():
            display = f"{acc_info['name']} ({acc_info['remaining']} remaining)"
            self.account_selector.addItem(display, acc_id)

    def _refresh_accounts_list(self):
        status = self.rate_manager.get_status()
        self.accounts_table.setRowCount(len(status["accounts"]))
        for row, (acc_id, acc_info) in enumerate(status["accounts"].items()):
            self.accounts_table.setItem(
                row, 0, QTableWidgetItem(acc_info.get("name", acc_id))
            )
            self.accounts_table.setItem(
                row, 1, QTableWidgetItem(acc_info.get("reset", "--"))
            )
            self.accounts_table.setItem(
                row,
                2,
                QTableWidgetItem("Active" if acc_info["is_current"] else "Inactive"),
            )
            self.accounts_table.setItem(
                row, 3, QTableWidgetItem(f"{acc_info['remaining']}")
            )

    def _check_rate_limits(self):
        if not HAS_REQUESTS:
            self._log("Rate limit check requires internet connection")
            return
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account configured")
            return
        try:
            headers = github_headers(token)
            resp = requests.get(
                "https://api.github.com/rate_limit", headers=headers, timeout=10
            )
            self.rate_manager.handle_rate_limit_response(resp)
            if resp.status_code == 200:
                data = resp.json()
                core = data.get("resources", {}).get("core", {})
                remaining = core.get("remaining", 0)
                limit = core.get("limit", 0)
                reset_epoch = core.get("reset", 0)
                self.rate_manager.update_rate_limit(remaining, reset_epoch)
                self._log(f"Rate limit: {remaining}/{limit} remaining")
            else:
                self._log(f"Rate limit check failed: HTTP {resp.status_code}")
        except Exception as e:
            self._log(f"Rate limit check error: {e}")
        self._update_rate_display()

    # --- Rate Monitor ---

    def _start_rate_monitor(self):
        self.rate_timer = QTimer()
        self.rate_timer.timeout.connect(self._update_rate_display)
        self.rate_timer.start(30000)

    def _update_rate_display(self):
        status = self.rate_manager.get_status()
        if status["current"]:
            acc = status["accounts"].get(status["current"], {})
            remaining = acc.get("remaining", 0)
            reset = acc.get("reset", "--:--")
            name = acc.get("name", status["current"])
            self.rate_status_label.setText(
                f"Rate Limit: {remaining} (resets {reset}) - {name}"
            )
            self.rate_remaining_label.setText(f"API Remaining: {remaining}")

    # --- Theme & Matrix ---

    def _apply_theme(self, index):
        theme_name = self.theme_combo.currentText()
        themes = {
            "Dark (Default)": {
                "bg": "#1e1e1e",
                "widget_bg": "#2d2d2d",
                "btn_bg": "#3c3c3c",
                "text": "#ffffff",
                "border": "#555",
                "accent": "#4a90d9",
                "matrix_opacity": 0.4,
            },
            "Light": {
                "bg": "#ffffff",
                "widget_bg": "#f5f5f5",
                "btn_bg": "#e0e0e0",
                "text": "#000000",
                "border": "#ccc",
                "accent": "#2196f3",
                "matrix_opacity": 0.15,
            },
            "Flame": {
                "bg": "#1a0a0a",
                "widget_bg": "#2d1515",
                "btn_bg": "#4a1f1f",
                "text": "#ffccaa",
                "border": "#662222",
                "accent": "#ff4400",
                "matrix_opacity": 0.5,
                "matrix_color": "255, 100, 50",
            },
            "Lightning": {
                "bg": "#0a0a1a",
                "widget_bg": "#15152d",
                "btn_bg": "#1f1f4a",
                "text": "#ccddff",
                "border": "#333366",
                "accent": "#00aaff",
                "matrix_opacity": 0.6,
                "matrix_color": "150, 200, 255",
            },
            "Neon": {
                "bg": "#0a0a12",
                "widget_bg": "#12121f",
                "btn_bg": "#1a1a2a",
                "text": "#00ffaa",
                "border": "#2a2a4a",
                "accent": "#ff00ff",
                "matrix_opacity": 0.55,
                "matrix_color": "255, 0, 255",
            },
            "Cyberpunk": {
                "bg": "#0d0015",
                "widget_bg": "#1a0025",
                "btn_bg": "#2d0040",
                "text": "#ff00ff",
                "border": "#ff00aa",
                "accent": "#00ffff",
                "matrix_opacity": 0.5,
                "matrix_color": "255, 0, 255",
            },
            "Ocean": {
                "bg": "#001a2d",
                "widget_bg": "#00334d",
                "btn_bg": "#004d66",
                "text": "#aaddff",
                "border": "#005580",
                "accent": "#00aaff",
                "matrix_opacity": 0.35,
                "matrix_color": "50, 150, 220",
            },
            "Forest": {
                "bg": "#0d1a0d",
                "widget_bg": "#152d15",
                "btn_bg": "#1f3d1f",
                "text": "#aaffaa",
                "border": "#2d4d2d",
                "accent": "#00ff44",
                "matrix_opacity": 0.4,
                "matrix_color": "100, 220, 100",
            },
            "Midnight": {
                "bg": "#050510",
                "widget_bg": "#0a0a1f",
                "btn_bg": "#0f0f2f",
                "text": "#9999cc",
                "border": "#222244",
                "accent": "#6666ff",
                "matrix_opacity": 0.45,
                "matrix_color": "100, 100, 200",
            },
            "Sunset": {
                "bg": "#1a1000",
                "widget_bg": "#2d1a00",
                "btn_bg": "#4a2d00",
                "text": "#ffeebb",
                "border": "#664400",
                "accent": "#ff8800",
                "matrix_opacity": 0.4,
                "matrix_color": "255, 150, 50",
            },
        }
        t = themes.get(theme_name, themes["Dark (Default)"])

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {t["bg"]}; color: {t["text"]}; }}
            QWidget#contentWidget {{ background-color: {t["widget_bg"]}; }}
            QPushButton {{ background-color: {t["btn_bg"]}; color: {t["text"]}; padding: 5px 15px; border: 1px solid {t["border"]}; }}
            QPushButton:hover {{ background-color: {t["accent"]}; }}
            QLineEdit, QTextEdit {{ background-color: {t["widget_bg"]}; color: {t["text"]}; border: 1px solid {t["border"]}; }}
            QListWidget, QTableWidget {{ background-color: {t["bg"]}; color: {t["text"]}; }}
            QProgressBar {{ border: 1px solid {t["border"]}; background-color: {t["btn_bg"]}; }}
            QGroupBox {{ border: 1px solid {t["border"]}; color: {t["text"]}; }}
            QComboBox {{ background-color: {t["btn_bg"]}; color: {t["text"]}; border: 1px solid {t["border"]}; }}
            QSpinBox {{ background-color: {t["widget_bg"]}; color: {t["text"]}; }}
            QStatusBar {{ background-color: {t["widget_bg"]}; color: {t["text"]}; }}
            QTabWidget::pane {{ border: 1px solid {t["border"]}; }}
            QCheckBox {{ color: {t["text"]}; }}
            QLabel {{ color: {t["text"]}; }}
        """)
        self.matrix_bg.setOpacity(t["matrix_opacity"])
        self.matrix_color_override = t.get("matrix_color")
        self._log(f"Theme applied: {theme_name}")
        self.is_dark_mode = index > 0

    def _toggle_theme(self):
        idx = (self.theme_combo.currentIndex() + 1) % self.theme_combo.count()
        self.theme_combo.setCurrentIndex(idx)
        self._apply_theme(idx)

    def _toggle_matrix(self, state):
        self.matrix_enabled = bool(state)
        if self.matrix_enabled:
            self.matrix_bg.show()
            self.matrix_bg._timer.start(50)
        else:
            self.matrix_bg.hide()
            self.matrix_bg._timer.stop()

    # --- Settings ---

    def _update_premium_title(self):
        state = "Restricted" if getattr(self, "premium_gate_enabled", False) else "Open"
        self.setWindowTitle(f"GitHub Repo Downloader v{self.VERSION}  Premium: {state}")

    def _handle_tab_change(self, index):
        try:
            if getattr(self, "premium_gate_enabled", False):
                tab_text = self.tabs.tabText(index)
                if "(Premium)" in tab_text or "Premium" in tab_text:
                    QMessageBox.information(
                        self,
                        "Premium Access",
                        "This feature requires Premium access (login/licensing).",
                    )
                    # revert to last allowed index
                    self.tabs.blockSignals(True)
                    self.tabs.setCurrentIndex(self._last_tab_index)
                    self.tabs.blockSignals(False)
                    return
            self._last_tab_index = index
        except Exception:
            self._last_tab_index = index

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                self.is_dark_mode = settings.get("dark_mode", False)
                if self.is_dark_mode:
                    self._toggle_theme()
                download_dir = settings.get("download_dir")
                if download_dir:
                    self.download_dir_input.setText(download_dir)
                self.max_concurrent_spin.setValue(settings.get("max_concurrent", 3))
                self.auto_switch_check.setChecked(settings.get("auto_switch", True))
                dl_speed = settings.get("dl_speed_limit", 0)
                self.dl_speed_spin.setValue(dl_speed)
                self._update_speed_label()
                self.matrix_enabled = settings.get("matrix_enabled", True)
                self.matrix_check.setChecked(self.matrix_enabled)
                if not self.matrix_enabled:
                    self.matrix_bg.hide()
                    self.matrix_bg._timer.stop()
                else:
                    opacity = 0.4 if self.is_dark_mode else 0.15
                    self.matrix_bg.setOpacity(opacity)
                self.proxy_http.setText(settings.get("proxy_http", ""))
                self.proxy_socks.setText(settings.get("proxy_socks", ""))
                self.total_downloaded_bytes = settings.get("total_downloaded_bytes", 0)
                self._update_total_downloaded_label()

                theme_index = settings.get("selected_theme", 0)
                if 0 <= theme_index < self.theme_combo.count():
                    self.theme_combo.setCurrentIndex(theme_index)
                    self._apply_theme(theme_index)

                # premium gate flag
                self.premium_gate_enabled = settings.get("premium_gate_enabled", False)
                if hasattr(self, "premium_gate_check"):
                    self.premium_gate_check.setChecked(self.premium_gate_enabled)
                self._update_premium_title()

                # Load recent downloads
                self.recent_downloads = settings.get("recent_downloads", [])
                self._update_recent_list()

                # GitHub Enterprise settings
                if hasattr(self, "github_enterprise_check"):
                    self.github_enterprise_check.setChecked(
                        settings.get("github_enterprise_enabled", False)
                    )
                    self.github_enterprise_url.setText(
                        settings.get("github_enterprise_url", "")
                    )

                # Scheduled downloads settings
                if hasattr(self, "scheduled_enabled_check"):
                    self.scheduled_enabled_check.setChecked(
                        settings.get("scheduled_enabled", False)
                    )
                    time_str = settings.get("schedule_time", "00:00")
                    from PyQt6.QtCore import QTime

                    t = QTime.fromString(time_str, "HH:mm")
                    if t.isValid():
                        self.schedule_time_edit.setTime(t)
                    for day, cb in self.schedule_days.items():
                        day_key = f"schedule_{day.lower()}"
                        cb.setChecked(settings.get(day_key, True))
                    self._init_scheduled_timer()

                # Backup options settings
                if hasattr(self, "clone_type_combo"):
                    self.clone_type_combo.setCurrentIndex(settings.get("clone_type", 0))
                    self.include_issues_check.setChecked(
                        settings.get("include_issues", False)
                    )
                    self.include_prs_check.setChecked(
                        settings.get("include_prs", False)
                    )
                    self.include_releases_check.setChecked(
                        settings.get("include_releases", False)
                    )
                    self.include_wiki_check.setChecked(
                        settings.get("include_wiki", False)
                    )
                    self.include_gists_check.setChecked(
                        settings.get("include_gists", False)
                    )
                    self.include_starred_check.setChecked(
                        settings.get("include_starred", False)
                    )
                    self.include_lfs_check.setChecked(
                        settings.get("include_lfs", False)
                    )
                    if hasattr(self, "backup_compress_check"):
                        self.backup_compress_check.setChecked(
                            settings.get("backup_compress", False)
                        )

                self._log("Settings loaded")
        except Exception as e:
            self._log(f"Failed to load settings: {e}")

    def _save_settings(self):
        try:
            premium_gate_enabled = False
            if hasattr(self, "premium_gate_check"):
                premium_gate_enabled = self.premium_gate_check.isChecked()

            github_enterprise_enabled = False
            github_enterprise_url = ""
            if hasattr(self, "github_enterprise_check"):
                github_enterprise_enabled = self.github_enterprise_check.isChecked()
                github_enterprise_url = self.github_enterprise_url.text()

            scheduled_enabled = False
            schedule_time = "00:00"
            schedule_days_data = {}
            if hasattr(self, "scheduled_enabled_check"):
                scheduled_enabled = self.scheduled_enabled_check.isChecked()
                schedule_time = self.schedule_time_edit.time().toString("HH:mm")
                for day, cb in self.schedule_days.items():
                    schedule_days_data[f"schedule_{day.lower()}"] = cb.isChecked()

            settings = {
                "dark_mode": self.is_dark_mode,
                "download_dir": self.download_dir_input.text(),
                "max_concurrent": self.max_concurrent_spin.value(),
                "auto_switch": self.auto_switch_check.isChecked(),
                "dl_speed_limit": self.dl_speed_spin.value(),
                "matrix_enabled": self.matrix_enabled,
                "proxy_http": self.proxy_http.text(),
                "proxy_socks": self.proxy_socks.text(),
                "total_downloaded_bytes": getattr(self, "total_downloaded_bytes", 0),
                "selected_theme": self.theme_combo.currentIndex(),
                "premium_gate_enabled": premium_gate_enabled,
                "recent_downloads": getattr(self, "recent_downloads", []),
                "github_enterprise_enabled": github_enterprise_enabled,
                "github_enterprise_url": github_enterprise_url,
                "scheduled_enabled": scheduled_enabled,
                "schedule_time": schedule_time,
                **schedule_days_data,
                # Backup options
                "clone_type": self.clone_type_combo.currentIndex(),
                "include_issues": self.include_issues_check.isChecked(),
                "include_prs": self.include_prs_check.isChecked(),
                "include_releases": self.include_releases_check.isChecked(),
                "include_wiki": self.include_wiki_check.isChecked(),
                "include_gists": self.include_gists_check.isChecked(),
                "include_starred": self.include_starred_check.isChecked(),
                "include_lfs": self.include_lfs_check.isChecked(),
                "backup_compress": self.backup_compress_check.isChecked()
                if hasattr(self, "backup_compress_check")
                else False,
                "version": self.VERSION,
            }
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=2)
            self._log("Settings saved")
        except Exception as e:
            self._log(f"Failed to save settings: {e}")

    # --- Shortcuts ---

    def _new_download(self):
        self.url_input.clear()
        self.url_input.setFocus()

    def _focus_search(self):
        self.search_input.setFocus()

    # --- Utilities ---

    def _update_speed_label(self):
        val = self.dl_speed_spin.value()
        if val == 0:
            self.dl_speed_label.setText("Downloads: unlimited")
        else:
            self.dl_speed_label.setText(f"Downloads: limited to {val} KB/s")

    def _notify(self, title: str, message: str):
        if self.tray:
            self.tray.showMessage(
                title, message, QSystemTrayIcon.MessageIcon.Information, 5000
            )

    def _show_notification(self, title: str, message: str):
        """Show desktop notification - alias for _notify"""
        self._notify(title, message)
        # Update tray menu status if available
        if hasattr(self, "tray_status_menu"):
            self.tray_status_menu.clear()
            self.tray_status_menu.addAction(f"{title}: {message[:50]}")

    def _log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_output.append(f"[{timestamp}] {message}")

    def _log_to_file(self, message: str):
        """Write log message to debug file"""
        try:
            import tempfile

            debug_log = os.path.join(tempfile.gettempdir(), "gh_downloader.log")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass  # Silently fail to avoid console spam

    # --- Download Wallet ---
    def _get_proxies(self):
        proxies = {}
        http_proxy = self.proxy_http.text().strip()
        socks_proxy = self.proxy_socks.text().strip()
        if http_proxy:
            proxies["http"] = http_proxy
            proxies["https"] = http_proxy
        if socks_proxy:
            proxies["socks5"] = socks_proxy
        return proxies if proxies else None

    def _reset_download_wallet(self):
        self.total_downloaded_bytes = 0
        self._update_total_downloaded_label()
        self._log("Download statistics reset")

    def _update_total_downloaded_label(self):
        """Update the total downloaded label with human-readable size"""
        if not hasattr(self, "total_downloaded_label"):
            return
        if not hasattr(self, "total_downloaded_bytes"):
            self.total_downloaded_bytes = 0

        bytes_val = self.total_downloaded_bytes
        if bytes_val < 1024:
            size_str = f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            size_str = f"{bytes_val / 1024:.1f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            size_str = f"{bytes_val / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

        self.total_downloaded_label.setText(f"Total Downloaded: {size_str}")

    # --- Scheduled Downloads ---
    def _on_schedule_enabled_changed(self, state):
        """Enable/disable schedule controls"""
        enabled = state == Qt.CheckState.Checked
        self.schedule_time_edit.setEnabled(enabled)
        for cb in self.schedule_days.values():
            cb.setEnabled(enabled)
        if enabled:
            self._init_scheduled_timer()
        elif hasattr(self, "schedule_timer"):
            self.schedule_timer.stop()
            self._log("Scheduled downloads disabled")

    def _init_scheduled_timer(self):
        """Initialize the scheduled download timer"""
        if not hasattr(self, "schedule_timer"):
            self.schedule_timer = QTimer(self)
            self.schedule_timer.timeout.connect(self._run_scheduled_download)
        self.schedule_timer.stop()

        if not self.scheduled_enabled_check.isChecked():
            return

        # Check if any days are selected
        any_day_selected = any(cb.isChecked() for cb in self.schedule_days.values())
        if not any_day_selected:
            self._log("No days selected for scheduled downloads")
            return

        # Schedule daily check every minute
        self.schedule_timer.start(60000)  # Check every minute
        self._log("Scheduled download timer started")

    def _run_scheduled_download(self):
        """Run scheduled download if conditions are met"""
        now = datetime.now()

        # Check if current day is selected
        day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        current_weekday = day_map[now.strftime("%a")]
        current_day_name = now.strftime("%a")

        day_checkbox_map = {
            "Mon": 0,
            "Tue": 1,
            "Wed": 2,
            "Thu": 3,
            "Fri": 4,
            "Sat": 5,
            "Sun": 6,
        }
        # Map day names to checkbox indices
        checkbox_map = {
            0: self.schedule_days["Mon"],
            1: self.schedule_days["Tue"],
            2: self.schedule_days["Wed"],
            3: self.schedule_days["Thu"],
            4: self.schedule_days["Fri"],
            5: self.schedule_days["Sat"],
            6: self.schedule_days["Sun"],
        }

        if not checkbox_map[current_weekday].isChecked():
            return

        # Check if it's the scheduled time (within 1 minute window)
        scheduled_time = self.schedule_time_edit.time()
        now_time = QTime.currentTime()

        if (
            scheduled_time.hour() == now_time.hour()
            and scheduled_time.minute() == now_time.minute()
        ):
            # Check if there are items in the queue
            if hasattr(self, "queue_list") and self.queue_list.count() > 0:
                self._log("Scheduled download triggered")
                self._process_queue()
            else:
                self._log("Scheduled time reached but queue is empty")

    # --- Sync/Diff ---
    def _select_sync_directory(self):
        d = QFileDialog.getExistingDirectory(self, "Select local repo")
        if d:
            self.sync_dir_input.setText(d)

    def _show_repo_diff(self):
        repo_dir = self.sync_dir_input.text().strip()
        if not repo_dir or not os.path.isdir(repo_dir):
            self._log("Select a valid local repository directory")
            return
        try:
            result = subprocess.run(
                ["git", "fetch", "--dry-run"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                self.diff_output.setPlainText(
                    f"Remote is up to date with local.\n\n{result.stdout}"
                )
            else:
                self.diff_output.setPlainText(
                    f"Changes detected:\n\n{result.stdout}\n{result.stderr}"
                )
        except Exception as e:
            self.diff_output.setPlainText(f"Error: {e}")

    def _fetch_remote_info(self):
        repo_dir = self.sync_dir_input.text().strip()
        if not repo_dir or not os.path.isdir(repo_dir):
            self._log("Select a valid local repository directory")
            return
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.diff_output.setPlainText(result.stdout or result.stderr)
        except Exception as e:
            self.diff_output.setPlainText(f"Error: {e}")

    # --- Commits ---
    def _fetch_commits(self):
        repo = self.commits_repo_input.text().strip()
        if not repo or "/" not in repo:
            self._log("Enter repo in format owner/repo")
            return
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account configured")
            return
        url = f"https://api.github.com/repos/{repo}/commits?per_page=20"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubDownloader/2.5.0",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                commits = r.json()
                self.commits_list.clear()
                for c in commits:
                    msg = c["commit"]["message"].split("\n")[0][:60]
                    date = c["commit"]["author"]["date"][:10]
                    sha = c["sha"][:7]
                    self.commits_list.addItem(f"{sha} - {date} - {msg}")
                self.commits_info.setText(f"Showing {len(commits)} recent commits")
            else:
                self.commits_info.setText(f"Error: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            self.commits_info.setText(f"Error: {e}")

    # --- Gists ---
    def _fetch_gists(self):
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account configured")
            return
        url = "https://api.github.com/gists"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubDownloader/2.5.0",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                gists = r.json()
                self.gists_list.clear()
                for g in gists:
                    desc = g.get("description", "No description")[:40]
                    files = list(g.get("files", {}).keys())
                    self.gists_list.addItem(
                        f"{g['id'][:8]} - {desc} ({len(files)} files)"
                    )
                self._log(f"Fetched {len(gists)} gists")
            else:
                self._log(f"Error fetching gists: {r.status_code}")
        except Exception as e:
            self._log(f"Error: {e}")

    def _download_selected_gist(self):
        item = self.gists_list.currentItem()
        if not item:
            self._log("Select a gist to download")
            return
        gist_id = item.text().split(" - ")[0]
        token = self.rate_manager.get_current_token()
        if not token:
            return
        url = f"https://api.github.com/gists/{gist_id}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubDownloader/2.5.0",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                gist = r.json()
                out_dir = os.path.join(
                    self.download_dir_input.text(), f"gist_{gist_id}"
                )
                os.makedirs(out_dir, exist_ok=True)
                for fname, fdata in gist["files"].items():
                    with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
                        f.write(fdata.get("content", ""))
                self._log(f"Gist saved to {out_dir}")
                self._open_folder(out_dir)
            else:
                self._log(f"Error: {r.status_code}")
        except Exception as e:
            self._log(f"Error: {e}")

    def _show_create_gist_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Gist")
        layout = QVBoxLayout(dialog)
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("Description (optional)")
        layout.addWidget(desc_input)
        content_input = QTextEdit()
        content_input.setPlaceholderText("File content")
        layout.addWidget(content_input)
        private_check = QCheckBox("Private gist")
        layout.addWidget(private_check)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(
            lambda: self._create_gist(
                desc_input.text(),
                content_input.toPlainText(),
                private_check.isChecked(),
                dialog,
            )
        )
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec()

    def _create_gist(self, desc: str, content: str, private: bool, dialog: QDialog):
        if not content:
            self._log("Gist content cannot be empty")
            return
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account configured")
            return
        url = "https://api.github.com/gists"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubDownloader/2.5.0",
        }
        data = {
            "description": desc,
            "public": not private,
            "files": {"file.txt": {"content": content}},
        }
        try:
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 201:
                gist = r.json()
                self._log(f"Gist created: {gist['html_url']}")
                dialog.accept()
            else:
                self._log(f"Error creating gist: {r.status_code}")
        except Exception as e:
            self._log(f"Error: {e}")

    # --- File Browser ---
    def _browse_repo_files(self):
        repo = self.files_repo_input.text().strip()
        if not repo or "/" not in repo:
            self._log("Enter repo in format owner/repo")
            return
        path = self.files_path_input.text().strip() or "/"
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account configured")
            return
        url = f"https://api.github.com/repos/{repo}/contents{path}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubDownloader/2.5.0",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                items = r.json()
                self.files_tree.clear()
                if isinstance(items, list):
                    for item in items:
                        name = item.get("name", "")
                        ftype = "dir" if item.get("type") == "dir" else "file"
                        size = item.get("size", 0)
                        self.files_tree.addTopLevelItem(
                            QTreeWidgetItem([name, ftype, str(size)])
                        )
                else:
                    self.files_tree.addTopLevelItem(
                        QTreeWidgetItem(
                            [items.get("name", ""), "file", str(items.get("size", 0))]
                        )
                    )
                self._log(f"Browsed {repo}{path}")
            else:
                self._log(f"Error: {r.status_code}")
        except Exception as e:
            self._log(f"Error: {e}")

    def _file_tree_double_click(self, item: QTreeWidgetItem, col: int):
        name = item.text(0)
        ftype = item.text(1)
        if ftype == "dir":
            current = self.files_path_input.text().strip()
            if current.endswith("/"):
                self.files_path_input.setText(current + name + "/")
            else:
                self.files_path_input.setText("/" + name + "/")
            self._browse_repo_files()

    def _clone_from_file_browser(self):
        repo = self.files_repo_input.text().strip()
        if repo:
            self.url_input.setText(repo)
            self._log(f"Set repo to {repo} for cloning")

    # --- Pull Requests ---
    def _fetch_pr_info(self):
        repo = self.pr_repo_input.text().strip()
        pr_num = self.pr_number_input.value()
        if not repo or "/" not in repo:
            self._log("Enter repo in format owner/repo")
            return
        token = self.rate_manager.get_current_token()
        if not token:
            self._log("No account configured")
            return
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_num}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubDownloader/2.5.0",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                pr = r.json()
                info = f"PR #{pr_num}: {pr.get('title')}\n\nState: {pr.get('state')}\nUser: {pr.get('user', {}).get('login')}\n\n{pr.get('body', '')[:500]}"
                self.pr_info.setPlainText(info)
            else:
                self.pr_info.setPlainText(f"Error: {r.status_code}")
        except Exception as e:
            self.pr_info.setPlainText(f"Error: {e}")

    def _checkout_pr(self):
        repo = self.pr_repo_input.text().strip()
        pr_num = self.pr_number_input.value()
        repo_dir = self.download_dir_input.text().strip()
        if not repo or "/" not in repo:
            self._log("Enter repo in format owner/repo")
            return
        local_dir = os.path.join(repo_dir, repo.replace("/", "_"))
        if not os.path.isdir(local_dir):
            self._log(f"Repo not found locally: {local_dir}. Clone it first.")
            return
        try:
            ref = f"refs/pull/{pr_num}/head"
            result = subprocess.run(
                ["git", "fetch", "origin", ref],
                cwd=local_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                subprocess.run(
                    ["git", "checkout", "FETCH_HEAD"],
                    cwd=local_dir,
                    capture_output=True,
                    timeout=30,
                )
                self._log(f"Checked out PR #{pr_num}")
            else:
                self._log(f"Failed to fetch PR: {result.stderr}")
        except Exception as e:
            self._log(f"Error checking out PR: {e}")

    # --- Scheduler ---
    def _toggle_scheduler(self):
        if hasattr(self, "scheduler_running") and self.scheduler_running:
            self.scheduler_running = False
            self.schedule_toggle_btn.setText("Start Scheduler")
            self.schedule_status.setText("Scheduler: stopped")
            if hasattr(self, "scheduler_timer"):
                self.scheduler_timer.stop()
            self._log("Scheduler stopped")
        else:
            self.scheduler_running = True
            self.schedule_toggle_btn.setText("Stop Scheduler")
            self.schedule_status.setText("Scheduler: running")
            interval_map = {
                "Every 30 minutes": 30,
                "Every hour": 60,
                "Every 6 hours": 360,
                "Every 24 hours": 1440,
            }
            mins = interval_map.get(self.schedule_interval.currentText(), 60)
            self.scheduler_timer = QTimer(self)
            self.scheduler_timer.timeout.connect(self._run_scheduled_update)
            self.scheduler_timer.start(mins * 60 * 1000)
            self._log(f"Scheduler started (interval: {mins} minutes)")

    def _run_scheduled_update(self):
        repos_text = self.schedule_repos_input.toPlainText().strip()
        if not repos_text:
            return
        repos = [r.strip() for r in repos_text.split("\n") if r.strip()]
        self.schedule_log.append(
            f"--- Running scheduled update for {len(repos)} repos ---"
        )
        for repo in repos:
            self.schedule_log.append(f"Updating {repo}...")
            self._update_single_repo(repo)
        self.schedule_log.append("--- Scheduled update complete ---")

    def _update_single_repo(self, owner_repo: str):
        repo_dir = os.path.join(
            self.download_dir_input.text(), owner_repo.replace("/", "_")
        )
        if not os.path.isdir(repo_dir):
            self._log(f"Local repo not found: {owner_repo}")
            return
        try:
            subprocess.run(
                ["git", "pull", "origin"],
                cwd=repo_dir,
                capture_output=True,
                timeout=120,
            )
            self._log(f"Updated {owner_repo}")
        except Exception as e:
            self._log(f"Failed to update {owner_repo}: {e}")

    def _open_folder(self, path: str):
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.startfile(path)

    # --- Premium: Releases ---
    def _fetch_releases(self):
        repo = self.releases_repo_input.text().strip()
        if not repo or "/" not in repo:
            self._log("Enter repo in format owner/repo")
            return
        token = self.rate_manager.get_current_token()
        url = f"https://api.github.com/repos/{repo}/releases?per_page=20"
        headers = github_headers(token)
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                releases = r.json()
                self.releases_list.clear()
                for rel in releases:
                    tag = rel.get("tag_name", "unknown")
                    name = rel.get("name", tag)
                    date = rel.get("published_at", "")[:10]
                    self.releases_list.addItem(f"{tag} - {name} ({date})")
                self._log(f"Found {len(releases)} releases")
            else:
                self._log(f"Error fetching releases: {r.status_code}")
        except Exception as e:
            self._log(f"Error: {e}")

    def _download_latest_release(self):
        repo = self.releases_repo_input.text().strip()
        if not repo:
            self._log("Enter repo first")
            return
        if self.releases_list.count() == 0:
            self._log("Fetch releases first")
            return
        selected = self.releases_list.currentItem().text().split(" - ")[0]
        output_dir = self.release_download_dir.text().strip() or os.path.join(
            os.path.expanduser("~"), "Downloads"
        )
        os.makedirs(output_dir, exist_ok=True)

        token = self.rate_manager.get_current_token()
        url = f"https://api.github.com/repos/{repo}/releases/tags/{selected}"
        headers = github_headers(token)
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                for asset in data.get("assets", []):
                    if asset["name"].endswith((".zip", ".tar.gz", ".tar.gz")):
                        self._log(f"Downloading {asset['name']}...")
                        download_url = asset["browser_download_url"]
                        resp = requests.get(download_url, headers=headers, stream=True)
                        path = os.path.join(output_dir, asset["name"])
                        with open(path, "wb") as f:
                            for chunk in resp.iter_content(8192):
                                f.write(chunk)
                        self._log(f"Saved to {path}")
                        break
        except Exception as e:
            self._log(f"Download failed: {e}")

    # --- Premium: Analytics ---
    def _fetch_analytics(self):
        repo = self.analytics_repo_input.text().strip()
        if not repo or "/" not in repo:
            self._log("Enter repo in format owner/repo")
            return
        token = self.rate_manager.get_current_token()
        url = f"https://api.github.com/repos/{repo}"
        headers = github_headers(token)
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                stars = data.get("stargazers_count", 0)
                forks = data.get("forks_count", 0)
                watchers = data.get("watchers_count", 0)
                size_kb = data.get("size", 0)
                lang = data.get("language", "Unknown")
                license_name = (data.get("license") or {}).get("name", "None")
                topics = ", ".join(data.get("topics", [])[:5]) or "None"

                self.analytics_output.setPlainText(
                    f"""
Repository: {repo}
------------------------
Stars: {stars:,}
Forks: {forks:,}
Watchers: {watchers}
Language: {lang}
Size: {size_kb} KB
License: {license_name}
Topics: {topics}
                """.strip()
                )
                self._log(f"Loaded analytics for {repo}")
        except Exception as e:
            self._log(f"Error: {e}")

    def _update_analytics_summary(self):
        download_dir = self.download_dir_input.text().strip() or os.path.join(
            os.path.expanduser("~"), "Downloads", "GitHubRepos"
        )
        if not os.path.isdir(download_dir):
            self.analytics_summary.setPlainText("No repositories downloaded yet.")
            return
        repos = [
            d
            for d in os.listdir(download_dir)
            if os.path.isdir(os.path.join(download_dir, d))
        ]
        # Compute total size by iterating each repo and walking its directory
        total_size = 0
        for r in repos:
            for dp, ds, files in os.walk(os.path.join(download_dir, r)):
                for f in files:
                    fp = os.path.join(dp, f)
                    if os.path.isfile(fp):
                        total_size += os.path.getsize(fp)
        self.analytics_summary.setPlainText(
            f"Total Repositories: {len(repos)}\nTotal Size: {total_size / 1024 / 1024:.1f} MB"
        )

    # --- Premium: Templates ---
    def _save_template(self):
        template_name, ok = QInputDialog.getText(
            self, "Save Template", "Template name:"
        )
        if not ok or not template_name:
            return
        repo = self.url_input.text().strip()
        if not repo:
            self._log("Enter a repository URL first")
            return
        templates_file = os.path.join(APPDATA_DIR, "templates.json")
        templates = {}
        if os.path.exists(templates_file):
            with open(templates_file, "r") as f:
                templates = json.load(f)
        templates[template_name] = {
            "repo": repo,
            "branch": self.branch_combo.currentText().strip(),
            "shallow": self.shallow_check.isChecked(),
            "submodules": self.submodules_check.isChecked(),
        }
        with open(templates_file, "w") as f:
            json.dump(templates, f, indent=2)
        self._load_templates_list()
        self._log(f"Saved template: {template_name}")

    def _load_templates_list(self):
        templates_file = os.path.join(APPDATA_DIR, "templates.json")
        self.templates_list.clear()
        if os.path.exists(templates_file):
            with open(templates_file, "r") as f:
                templates = json.load(f)
            for name in templates:
                self.templates_list.addItem(name)

    def _load_template(self):
        selected = self.templates_list.currentItem()
        if not selected:
            return
        templates_file = os.path.join(APPDATA_DIR, "templates.json")
        with open(templates_file, "r") as f:
            templates = json.load(f)
        template = templates.get(selected.text())
        if template:
            self.url_input.setText(template.get("repo", ""))
            self.branch_combo.setCurrentText(template.get("branch", ""))
            self.shallow_check.setChecked(template.get("shallow", False))
            self.submodules_check.setChecked(template.get("submodules", False))
            self._log(f"Loaded template: {selected.text()}")

    # --- Premium: Import/Export ---
    def _export_data(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", f"{APP_NAME}_backup.json", "JSON Files (*.json)"
        )
        if not path:
            return
        data = {
            "accounts": self.account_manager.accounts,
            "settings": {},
            "templates": {},
        }
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data["settings"] = json.load(f)
        templates_file = os.path.join(APPDATA_DIR, "templates.json")
        if os.path.exists(templates_file):
            with open(templates_file, "r") as f:
                data["templates"] = json.load(f)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        self._log(f"Data exported to {path}")

    def _import_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Data", "", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if "accounts" in data:
                for acc_id, acc_data in data["accounts"].items():
                    self.account_manager.add_account(
                        acc_id, acc_data.get("token", ""), acc_data.get("username", "")
                    )
                self._load_accounts()
            if "settings" in data:
                with open(SETTINGS_FILE, "w") as f:
                    json.dump(data["settings"], f, indent=2)
            if "templates" in data:
                templates_file = os.path.join(APPDATA_DIR, "templates.json")
                with open(templates_file, "w") as f:
                    json.dump(data["templates"], f, indent=2)
            self._load_templates_list()
            self._load_settings()
            self._log("Data imported successfully")
        except Exception as e:
            self._log(f"Import failed: {e}")

    # --- Premium: Backup ---
    def _select_backup_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if d:
            self.backup_dir_input.setText(d)

    def _run_backup(self):
        if not self.backup_enabled.isChecked():
            self._log("Enable auto-backup first")
            return
        source_dir = self.download_dir_input.text().strip() or os.path.join(
            os.path.expanduser("~"), "Downloads", "GitHubRepos"
        )
        backup_dir = self.backup_dir_input.text().strip()
        if not backup_dir:
            self._log("Select backup directory")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = os.path.join(backup_dir, f"backup_{timestamp}")

        try:
            import shutil

            # Backup settings and accounts
            if os.path.exists(SETTINGS_FILE):
                shutil.copy2(
                    SETTINGS_FILE, os.path.join(backup_subdir, "settings.json")
                )
            if os.path.exists(ACCOUNTS_FILE):
                shutil.copy2(
                    ACCOUNTS_FILE, os.path.join(backup_subdir, "accounts.json")
                )

            # Backup downloaded repos
            repos_copied = 0
            if os.path.isdir(source_dir):
                repos = [
                    d
                    for d in os.listdir(source_dir)
                    if os.path.isdir(os.path.join(source_dir, d))
                ]
                for repo in repos:
                    src = os.path.join(source_dir, repo)
                    dst = os.path.join(backup_subdir, repo)
                    shutil.copytree(src, dst)
                    repos_copied += 1

            # Compress if enabled
            if self.backup_compress_check.isChecked():
                zip_path = os.path.join(backup_dir, f"backup_{timestamp}.zip")
                self._log("Compressing backup...")
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(backup_subdir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, backup_subdir)
                            zf.write(file_path, arcname)
                # Remove uncompressed folder after zipping
                shutil.rmtree(backup_subdir)
                backup_subdir = zip_path

            self.backup_log.append(
                f"[{timestamp}] Backed up {repos_copied} repos + config files to {backup_subdir}"
            )
            self._log(f"Backup complete: {repos_copied} repos + settings")
        except Exception as e:
            self._log(f"Backup failed: {e}")

    def _quit_app(self):
        self._save_settings()
        # Auto-backup settings on quit if enabled
        if self.backup_enabled.isChecked() and self.backup_dir_input.text().strip():
            self._log("Performing backup before exit...")
            self._run_backup()
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._notify("Minimized", "Running in background. Use tray menu to quit.")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
def main():
    # Setup logging to file for debugging
    log_file = os.path.join(APPDATA_DIR, "startup.log")
    try:
        with open(log_file, "w") as f:
            f.write(f"Starting {APP_NAME} v{VERSION} at {datetime.now().isoformat()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Platform: {platform.platform()}\n")
            f.write(f"Executable: {sys.executable}\n")
            f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
            f.write(f"CWD: {os.getcwd()}\n")
    except Exception as e:
        print(f"Cannot write log: {e}")

    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        with open(log_file, "a") as f:
            f.write("Creating main window...\n")

        window = GitHubDownloaderEnhanced()

        with open(log_file, "a") as f:
            f.write("Window created, calling show()...\n")

        window.show()

        with open(log_file, "a") as f:
            f.write(
                f"Window shown! Visible: {window.isVisible()}, Handle: {window.winId()}\n"
            )

        sys.exit(app.exec())

    except Exception as e:
        import traceback

        error_msg = traceback.format_exc()
        print(f"FATAL ERROR: {e}\n{error_msg}", file=sys.stderr)
        try:
            with open(log_file, "a") as f:
                f.write(f"FATAL ERROR: {e}\n{error_msg}\n")
        except:
            pass
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start application:\n\n{e}\n\nCheck {log_file} for details.",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
