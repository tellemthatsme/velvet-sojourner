import sys
import os
import threading
import time

print("START", flush=True)

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication([])
print("App created", flush=True)

from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

# Monkey-patch to trace what's happening
original_on_single = GitHubDownloaderEnhanced._on_single_account_repos


def patched_on_single(self, repos, account_id, account_name):
    print(
        f"TRACE: _on_single_account_repos called with {len(repos)} repos for {account_id}",
        flush=True,
    )
    return original_on_single(self, repos, account_id, account_name)


GitHubDownloaderEnhanced._on_single_account_repos = patched_on_single

original_on_all = GitHubDownloaderEnhanced._on_all_accounts_repos_fetched


def patched_on_all(self):
    print(
        f"TRACE: _on_all_accounts_repos_fetched called with {len(self._all_accounts_repos)} repos",
        flush=True,
    )
    return original_on_all(self)


GitHubDownloaderEnhanced._on_all_accounts_repos_fetched = patched_on_all

original_fetch_next = GitHubDownloaderEnhanced._fetch_next_account_repos


def patched_fetch_next(self):
    print(
        f"TRACE: _fetch_next_account_repos called, accounts_to_fetch: {self._accounts_to_fetch}",
        flush=True,
    )
    return original_fetch_next(self)


GitHubDownloaderEnhanced._fetch_next_account_repos = patched_fetch_next

window = GitHubDownloaderEnhanced()
print("Window created", flush=True)


def test_func():
    try:
        print("Calling _download_all_accounts", flush=True)
        window._download_all_accounts()
        print("Returned from _download_all_accounts", flush=True)
    except Exception as e:
        print(f"EXCEPTION in thread: {e}", flush=True)
        import traceback

        traceback.print_exc()


t = threading.Thread(target=test_func, daemon=True)
t.start()
t.join(timeout=30)

# Give workers more time to complete
for i in range(100):
    app.processEvents()
    time.sleep(0.1)
    if i % 20 == 0:
        print(f"Waiting... {i * 0.1}s", flush=True)

print(f"Queue: {window.queue_list.count()}", flush=True)
print(f"Repos: {len(window._all_accounts_repos)}", flush=True)
print("DONE", flush=True)
