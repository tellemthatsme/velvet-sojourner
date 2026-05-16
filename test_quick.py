import sys
import os

print("START", flush=True)

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication([])

from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

window = GitHubDownloaderEnhanced()
print(f"Window created with {len(window.rate_manager.accounts)} accounts", flush=True)

# Just call the method and check if it returns without exception
print("Calling _download_all_accounts...", flush=True)

# Check state
print(f"Queue items: {window.queue_list.count()}", flush=True)
print(f"_all_accounts_repos: {len(window._all_accounts_repos)}", flush=True)
print(f"_accounts_to_fetch: {window._accounts_to_fetch}", flush=True)
print("DONE", flush=True)
