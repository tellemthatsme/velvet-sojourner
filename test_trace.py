import sys
import os

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication([])

from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

window = GitHubDownloaderEnhanced()


def log(msg):
    print(msg, flush=True)


log("Calling _download_all_accounts...")
window._download_all_accounts()

import time

for i in range(20):
    app.processEvents()
    time.sleep(0.05)

log(f"Final state:")
log(f"  Queue: {window.queue_list.count()} repos")
log(f"  _all_accounts_repos: {len(window._all_accounts_repos)} repos")
log(f"  _accounts_to_fetch: {len(window._accounts_to_fetch)} accounts")

if window.queue_list.count() > 0:
    log(f"First item: {window.queue_list.item(0).text()}")
    data = window.queue_list.item(0).data(Qt.ItemDataRole.UserRole)
    log(f"Has token: {bool(data.get('token', ''))}")
