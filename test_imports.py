import sys
sys.path.insert(0, 'src')

# Try importing step by step
print("Testing imports...")

from github_downloader.rate_manager import RateLimitManager
print("RateLimitManager OK")

from github_downloader.account_manager import AccountManager  
print("AccountManager OK")

from github_downloader.token_validator import TokenValidator
print("TokenValidator OK")

from github_downloader.oauth_worker import OAuthDeviceFlowWorker
print("OAuthDeviceFlowWorker OK")

from github_downloader.search_worker import SearchWorker
print("SearchWorker OK")

from github_downloader.download_worker import DownloadWorker
print("DownloadWorker OK")

from github_downloader.backup_worker import BackupWorker
print("BackupWorker OK")

print("All imports OK!")
