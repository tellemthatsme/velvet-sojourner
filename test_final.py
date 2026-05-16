import sys
import os
import time

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication([])

from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

window = GitHubDownloaderEnhanced()

print("Calling _download_all_accounts...")

window._download_all_accounts()

for i in range(30):
    app.processEvents()
    time.sleep(0.05)

print(f"Queue: {window.queue_list.count()} repos")
print(f"Accounts to fetch: {len(window._accounts_to_fetch)}")
