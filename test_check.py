import sys
import os

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication([])

from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

window = GitHubDownloaderEnhanced()

print(f"Window created with {len(window.rate_manager.accounts)} accounts")

# Direct call
print("Calling _download_all_accounts...")
result = window._download_all_accounts()
print(f"Returned: {result}")

# Process events to let workers run
import time

for _ in range(50):
    app.processEvents()
    time.sleep(0.1)

# Check log output
print(f"Queue: {window.queue_list.count()}")
print(f"Repos: {len(window._all_accounts_repos)}")
print(f"Accounts to fetch: {window._accounts_to_fetch}")
