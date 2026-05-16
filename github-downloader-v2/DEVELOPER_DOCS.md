# GitHub Repo Downloader v2.0 - Developer Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Modules](#core-modules)
4. [Enhancement Modules](#enhancement-modules)
5. [Data Flow](#data-flow)
6. [API Reference](#api-reference)
7. [Extending the Application](#extending-the-application)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Repo Downloader                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   GUI Layer  │  │  CLI Layer   │  │    Core      │          │
│  │  (PyQt6)     │  │ (argparse)   │  │   Logic      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                    │
│  ┌──────┴────────────────┴─────────────────┴──────┐            │
│  │                 Application Manager              │            │
│  │  (ThemeManager, SyncManager, BookmarksManager,  │            │
│  │   MultiAccountManager, NotificationManager)     │            │
│  └─────────────────────────┬───────────────────────┘            │
│                            │                                      │
│  ┌─────────────────────────┴───────────────────────┐            │
│  │              User Authentication Layer           │            │
│  │              (UserDatabase, Encrypted)           │            │
│  └─────────────────────────┬───────────────────────┘            │
│                            │                                      │
│  ┌─────────────────────────┴───────────────────────┐            │
│  │              GitHub API Layer                    │            │
│  │         (GitHubAPIClient, Rate Limiting)         │            │
│  └─────────────────────────┬───────────────────────┘            │
│                            │                                      │
│  ┌─────────────────────────┴───────────────────────┐            │
│  │              Download Layer                      │            │
│  │     (GitRepoDownloader, BatchDownloader)         │            │
│  └─────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
velvet-sojourner/
├── src/
│   ├── main.py                    # Entry point, GUI + CLI router
│   └── github_downloader/
│       ├── __init__.py            # Package exports
│       ├── user_auth.py           # User auth + encrypted credentials
│       ├── github_api.py          # GitHub REST API client
│       ├── downloader.py          # Download/clone logic
│       ├── gui.py                 # Original basic GUI
│       └── gui_enhanced.py        # Enhanced GUI (v2.0)
├── requirements.txt               # Python dependencies
├── build_exe.py                 # PyInstaller configuration
├── build.bat                    # Build script
└── README.md                    # User documentation
```

---

## Core Modules

### 1. user_auth.py - User Authentication

**Purpose:** Manages local user accounts and encrypted GitHub credentials.

**Classes:**
- `UserDatabase` - SQLite-based user management

**Key Methods:**
```python
class UserDatabase:
    def create_user(username, password)      # Create new user
    def authenticate_user(username, password) # Login
    def save_github_credentials(user_id, ...) # Store encrypted token
    def get_github_credentials(user_id)       # Retrieve decrypted token
    def log_download(user_id, ...)            # History tracking
    def get_download_history(user_id)         # Get history
```

**Security Features:**
- PBKDF2-HMAC-SHA256 password hashing (100,000 iterations)
- Fernet symmetric encryption for GitHub tokens
- Salted passwords

**Database Schema:**
```
users (id, username, password_hash, salt, created_at, last_login, is_active)
github_credentials (id, user_id, auth_type, access_token, refresh_token, token_expires_at, github_username)
download_history (id, user_id, repo_url, repo_name, local_path, downloaded_at, file_count, file_size, status)
app_settings (key, value)
```

---

### 2. github_api.py - GitHub API Client

**Purpose:** Interact with GitHub REST API with rate limiting and terms compliance.

**Classes:**
- `AuthType` - Enum (NONE, PAT, OAUTH)
- `RateLimitInfo` - Rate limit data class
- `GitHubRateLimitHandler` - Rate limiting logic
- `GitHubTermsCompliance` - Terms of service enforcement
- `GitHubAPIClient` - Main API client
- `GitHubOAuth` - OAuth helper

**Key Methods:**
```python
class GitHubAPIClient:
    def get_user()                           # Get authenticated user
    def get_rate_limit()                     # Check rate limits
    def get_repo(owner, repo)                # Get repo info
    def get_repo_contents(owner, repo, path) # Get file tree
    def get_repo_tree(owner, repo, recursive)# Get git tree
    def download_file(...)                   # Download single file
    def get_user_repos(username)             # List user repos
    def search_repos(query)                  # Search GitHub
    def get_org_repos(org)                   # List org repos
    def get_user_starred(username)           # List starred repos
    def validate_token()                     # Test token validity
```

**Rate Limiting:**
- Authenticated: 5,000 requests/hour (safe limit: 4,000)
- Unauthenticated: 60 requests/hour (safe limit: 48)
- Automatic waiting when approaching limits
- Respects `Retry-After` headers

---

### 3. downloader.py - Download Logic

**Purpose:** Handles downloading and cloning repositories.

**Classes:**
- `DownloadMethod` - Enum (GIT_CLONE, DOWNLOAD_ZIP, DOWNLOAD_TAR)
- `DownloadStatus` - Enum (PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED)
- `DownloadTask` - Data class for download job
- `GitRepoDownloader` - Main downloader
- `BatchDownloader` - Parallel batch downloader

**Key Methods:**
```python
class GitRepoDownloader:
    def create_download_task(repo_url, output_path, method, branch)
    def start_download(task_id)
    def cancel_download(task_id)
    def get_download_status(task_id)
    def get_all_downloads()
```

**Download Methods:**
1. **Git Clone** - Uses git.exe, best for large repos
2. **Download ZIP** - Downloads ZIP from GitHub, extracts
3. **Download TAR** - Downloads tar.gz from GitHub, extracts

---

## Enhancement Modules

### 4. gui_enhanced.py - Enhanced GUI

**Purpose:** Full-featured GUI with dark theme, shortcuts, and all enhancements.

**Classes:**
- `CLIMode` - Command-line interface
- `ThemeManager` - Light/dark theme management
- `NotificationManager` - System tray notifications
- `SyncManager` - Repository sync scheduling
- `BookmarksManager` - Favorite repos
- `MultiAccountManager` - Multiple GitHub accounts
- `SelectiveDownloadDialog` - Tree view for selective download
- `ScheduledDownloadDialog` - Schedule downloads
- `DownloadThread` - Background download thread
- `MainWindow` - Main application window

**MainWindow Tabs:**
1. Download - Single repo download
2. Batch - Multiple repos
3. Search - Search GitHub
4. My Repos - Load user's repos
5. Bookmarks - Saved favorites
6. Sync - Sync settings
7. History - Download history

**Keyboard Shortcuts:**
| Shortcut | Action |
|----------|--------|
| Ctrl+N | New download |
| Ctrl+B | Batch download |
| Ctrl+D | Download current |
| Ctrl+L | Focus path field |
| Ctrl+R | Load repos |
| Ctrl+S | Settings |
| Ctrl+T | Toggle theme |
| Ctrl+Q | Exit |

---

## Data Flow

### Download Flow
```
User enters repo URL
        ↓
Validate URL format
        ↓
Get GitHub token (if authenticated)
        ↓
Create DownloadTask
        ↓
Start DownloadThread
        ↓
GitRepoDownloader.start_download()
        ↓
[Git Clone / ZIP / TAR]
        ↓
Emit progress signals
        ↓
Update UI
        ↓
Log to history
        ↓
Show notification (if enabled)
```

### Authentication Flow
```
User logs in (local account)
        ↓
User enters GitHub PAT
        ↓
Test token with GET /user
        ↓
Encrypt token with Fernet
        ↓
Save to SQLite
        ↓
Create GitHubAPIClient with token
        ↓
API calls now authenticated (5,000/hr limit)
```

---

## API Reference

### UserDatabase
```python
# Create user
success, user_id = user_db.create_user("myuser", "password123")

# Login
user_id = user_db.authenticate_user("myuser", "password123")

# Get user info
user = user_db.get_user(user_id)
# Returns: {'id': 1, 'username': 'myuser', 'created_at': '...', 'last_login': '...'}

# Save GitHub credentials (encrypted)
user_db.save_github_credentials(
    user_id=1,
    auth_type='pat',
    access_token='ghp_xxxx',
    github_username='myuser'
)

# Get credentials (decrypted)
creds = user_db.get_github_credentials(user_id)
# Returns: {'auth_type': 'pat', 'access_token': 'ghp_xxxx', ...}

# Log download
user_db.log_download(
    user_id=1,
    repo_url='https://github.com/owner/repo',
    repo_name='repo',
    local_path='/downloads/repo',
    file_count=100,
    file_size=1024000,
    status='completed'
)

# Get history
history = user_db.get_download_history(user_id, limit=100)
```

### GitHubAPIClient
```python
# Create client (unauthenticated)
client = GitHubAPIClient()

# Create client (authenticated)
client = GitHubAPIClient(token='ghp_xxxx', auth_type=AuthType.PAT)

# Get authenticated user
user = client.get_user()
# Returns: {'login': 'username', 'name': 'Full Name', ...}

# Get rate limit status
limits = client.get_rate_limit()
# Returns: {'core': RateLimitInfo, 'search': RateLimitInfo}

# Get repository
repo = client.get_repo('owner', 'repo')
# Returns: {'name': 'repo', 'description': '...', 'size': 1234, ...}

# Get user repos
repos = client.get_user_repos('username', page=1, per_page=100)

# Search repos
results = client.search_repos('python web framework', page=1, per_page=30)

# Download file
success, path = client.download_file(
    owner='owner',
    repo='repo',
    path='src/main.py',
    output_path='/downloads',
    progress_callback=callback
)
```

### GitRepoDownloader
```python
# Create downloader
downloader = GitRepoDownloader(token='ghp_xxxx')

# Create task
task = downloader.create_download_task(
    repo_url='https://github.com/owner/repo',
    output_path='/downloads',
    method=DownloadMethod.GIT_CLONE,
    branch='main'
)

# Start download
success = downloader.start_download(task.id)

# Check status
status = downloader.get_download_status(task.id)
# Returns: DownloadTask with progress, status, etc.

# Cancel
download.cancel_download(task.id)
```

---

## Extending the Application

### Adding a New Download Method

1. Add enum value in `downloader.py`:
```python
class DownloadMethod(Enum):
    GIT_CLONE = "git_clone"
    DOWNLOAD_ZIP = "download_zip"
    DOWNLOAD_TAR = "download_tar"
    CUSTOM_METHOD = "custom_method"  # Add this
```

2. Implement method in `GitRepoDownloader`:
```python
def download_custom(self, task: DownloadTask) -> bool:
    # Your download logic here
    pass
```

3. Update `start_download` method:
```python
elif task.method == DownloadMethod.CUSTOM_METHOD:
    return self.download_custom(task)
```

### Adding a New GUI Tab

1. Create method in `MainWindow`:
```python
def create_custom_tab(self):
    tab = QWidget()
    layout = QVBoxLayout()
    # Add your widgets
    layout.addWidget(QLabel("My Custom Tab"))
    tab.setLayout(layout)
    return tab
```

2. Register in `init_ui`:
```python
self.custom_tab = self.create_custom_tab()
self.tabs.addTab(self.custom_tab, "Custom")
```

### Adding a New CLI Command

1. Add to CLIMode parser:
```python
def parse_args(self):
    parser = argparse.ArgumentParser(...)
    # ... existing commands ...
    parser.add_argument('command', choices=[..., 'custom'])
    # ... rest of args ...
```

2. Implement command:
```python
def cmd_custom(self, args):
    # Your logic here
    print("Custom command executed")
    return 0
```

3. Add to run method:
```python
def run(self):
    args = self.parse_args()
    # ... existing commands ...
    elif args.command == 'custom':
        return self.cmd_custom(args)
```

---

## Dependencies

```txt
PyQt6>=6.6.0          # GUI framework
requests>=2.31.0      # HTTP client
PyGithub>=1.59.0      # GitHub API wrapper
gitpython>=3.1.40     # Git operations
cryptography>=41.0.0  # Encryption
pywin32>=306          # Windows API
pyinstaller>=6.3.0    # EXE building
```

---

## Building Windows Executable

```bash
# Install dependencies
pip install -r requirements.txt

# Build
pyinstaller build_exe.py --clean

# Output in dist/GitHubDownloader.exe
```

---

## Testing

```bash
# Run imports test
python -c "from github_downloader import *; print('All imports successful')"

# Run CLI help
python src/main.py --cli --help

# Run GUI (requires display)
python src/main.py
```

---

## Troubleshooting

**Issue: ImportError for QShortcut**
- Fix: QShortcut is in `PyQt6.QtGui`, not `PyQt6.QtWidgets`

**Issue: GUI won't start**
- Check: Display environment variable (on remote servers, use `QT_QPA_PLATFORM=offscreen`)

**Issue: Rate limit errors**
- Fix: Use authentication token, reduce request frequency

**Issue: Git clone fails**
- Check: Git is installed and in PATH
- Fix: Use ZIP download method instead

---

## License

MIT License
