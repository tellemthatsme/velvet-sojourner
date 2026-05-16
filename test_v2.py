import sys
import os

print("START")
sys.stdout.flush()

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtWidgets import QApplication

    print("Creating app")
    sys.stdout.flush()
    app = QApplication([])

    from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

    print("Creating window")
    sys.stdout.flush()
    window = GitHubDownloaderEnhanced()

    accounts = list(window.rate_manager.accounts.keys())
    print(f"Accounts: {accounts}")
    sys.stdout.flush()

    # Test _download_all_accounts
    print("Calling _download_all_accounts")
    sys.stdout.flush()
    window._download_all_accounts()
    print("_download_all_accounts returned")
    sys.stdout.flush()

    # Let workers run
    import time

    for i in range(30):
        app.processEvents()
        time.sleep(0.2)

    print(f"Queue count: {window.queue_list.count()}")
    sys.stdout.flush()
    print(f"_all_accounts_repos: {len(window._all_accounts_repos)}")
    sys.stdout.flush()

except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
    sys.stdout.flush()
finally:
    print("DONE")
    sys.stdout.flush()
