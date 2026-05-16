import sys
import os

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication([])

from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

window = GitHubDownloaderEnhanced()

print(
    f"Window created with {len(window.rate_manager.accounts)} accounts", file=sys.stderr
)
print(f"Accounts: {list(window.rate_manager.accounts.keys())}", file=sys.stderr)

# Call the method directly
print("Calling _download_all_accounts...", file=sys.stderr)
window._download_all_accounts()
print("_download_all_accounts returned", file=sys.stderr)

# Process events
import time

for i in range(50):
    app.processEvents()
    time.sleep(0.1)

print(f"Queue: {window.queue_list.count()}", file=sys.stderr)
print(f"Repos: {len(window._all_accounts_repos)}", file=sys.stderr)
print(f"Accounts to fetch: {window._accounts_to_fetch}", file=sys.stderr)
