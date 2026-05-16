import sys
import os

sys.path.insert(0, "src")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from github_downloader.gui_enhanced_full import GitHubDownloaderEnhanced

    app = QApplication([])
    window = GitHubDownloaderEnhanced()

    print(f"Accounts: {list(window.rate_manager.accounts.keys())}")

    # Test _download_all_accounts
    print("Testing _download_all_accounts...")
    window._download_all_accounts()

    # Let async workers run
    import time

    for i in range(30):
        app.processEvents()
        time.sleep(0.2)

    print(f"Queue items: {window.queue_list.count()}")
    print(f"_all_accounts_repos after: {len(window._all_accounts_repos)}")

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
finally:
    print("Test done")
