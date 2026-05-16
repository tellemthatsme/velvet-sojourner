"""
GitHub Repo Downloader Package
"""
__version__ = "2.0.0"
__author__ = "User"

from .user_auth import UserDatabase
from .github_api import GitHubAPIClient, GitHubOAuth, AuthType, RateLimitInfo
from .downloader import GitRepoDownloader, DownloadTask, DownloadStatus, DownloadMethod

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
    'GUI_AVAILABLE',
    'GUI_ENHANCED_AVAILABLE',
]
