"""
GitHub Repo Downloader Package
"""
__version__ = "2.1.0"
__author__ = "User"

from .user_auth import UserDatabase
from .github_api import GitHubAPIClient, GitHubOAuth, AuthType, RateLimitInfo
from .downloader import GitRepoDownloader, DownloadTask, DownloadStatus, DownloadMethod
from .enhancements import (
    download_from_file, verify_download, verify_all_downloads,
    export_metadata, load_config_from_env, check_downloader_health,
    ProgressBar, setup_package,
)

# GUI modules (optional imports)
try:
    from .gui import main as gui_main, MainWindow
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

try:
    from .gui_enhanced import main as gui_main_enhanced, MainWindow as MainWindowEnhanced
    GUI_ENHANCED_AVAILABLE = True
except ImportError:
    GUI_ENHANCED_AVAILABLE = False

__all__ = [
    'UserDatabase',
    'GitHubAPIClient',
    'GitHubOAuth',
    'AuthType',
    'RateLimitInfo',
    'GitRepoDownloader',
    'DownloadTask',
    'DownloadStatus',
    'DownloadMethod',
    'download_from_file',
    'verify_download',
    'verify_all_downloads',
    'export_metadata',
    'load_config_from_env',
    'check_downloader_health',
    'ProgressBar',
    'setup_package',
    'GUI_AVAILABLE',
    'GUI_ENHANCED_AVAILABLE',
]
