import sys
import os

print("START", flush=True)

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QEventLoop

print("Creating app", flush=True)
app = QApplication([])

from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

print("Creating window", flush=True)
window = GitHubDownloaderEnhanced()

accounts = list(window.rate_manager.accounts.keys())
print(f"Accounts: {len(accounts)}", flush=True)

# Test _download_all_accounts
print("Calling _download_all_accounts", flush=True)
window._download_all_accounts()
print("_download_all_accounts returned", flush=True)

# Process events for a while to let workers run
import time

for i in range(50):
    app.processEvents()
    time.sleep(0.1)
    if i % 10 == 0:
        print(f"Processed {i * 0.1}s", flush=True)

print(f"Queue count: {window.queue_list.count()}", flush=True)
print(f"_all_accounts_repos: {len(window._all_accounts_repos)}", flush=True)
print("DONE", flush=True)
