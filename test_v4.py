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

window = GitHubDownloaderEnhanced()
print("Window created", flush=True)


# Test in a way that catches exceptions from the thread
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

# Give workers time to run
for i in range(50):
    app.processEvents()
    time.sleep(0.1)

print(f"Queue: {window.queue_list.count()}", flush=True)
print(f"Repos: {len(window._all_accounts_repos)}", flush=True)
print("DONE", flush=True)
