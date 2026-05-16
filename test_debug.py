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

# Process events - more iterations, longer wait
import time

for i in range(100):
    app.processEvents()
    time.sleep(0.05)
    if i % 10 == 0:
        print(f"Processed {i} events...", flush=True)

# Check log output
print(f"Queue: {window.queue_list.count()}")
print(f"Repos: {len(window._all_accounts_repos)}")
print(f"Accounts to fetch: {window._accounts_to_fetch}")
print(f"Active workers: {window.active_workers}")
