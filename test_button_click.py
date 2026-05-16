# Test script that loads the app and tries to download all accounts
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from github_downloader.gui_enhanced_full import MainWindow, QApplication, QTimer
import time


def test_download_all():
    print("Creating QApplication...", file=sys.stderr)
    app = QApplication(sys.argv)

    print("Creating MainWindow...", file=sys.stderr)
    window = MainWindow()

    print("Showing window...", file=sys.stderr)
    window.show()

    # Let the window show
    for i in range(3):
        app.processEvents()
        time.sleep(0.5)
        print(f"Processing events {i + 1}...", file=sys.stderr)

    # Check if there are accounts configured
    print(f"Accounts: {list(window.rate_manager.accounts.keys())}", file=sys.stderr)

    # Try to trigger the download
    print("Calling _download_all_accounts()...", file=sys.stderr)
    try:
        window._download_all_accounts()
        print("Call succeeded!", file=sys.stderr)
    except Exception as e:
        print(f"Call failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)

    # Process events for a bit to let things happen
    print("Processing events for 5 seconds...", file=sys.stderr)
    for i in range(10):
        app.processEvents()
        time.sleep(0.5)
        print(f"Tick {i + 1}...", file=sys.stderr)

    print("Test complete!", file=sys.stderr)

    # Don't quit, let the user see the window
    # app.quit()


if __name__ == "__main__":
    test_download_all()
