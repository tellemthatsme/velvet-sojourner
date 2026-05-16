# Entry point for PyInstaller
import sys
import os
import traceback


def main():
    """Main entry point with crash logging"""
    try:
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
            src_path = os.path.join(base_path, "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            module_path = os.path.join(src_path, "github_downloader")
            if module_path not in sys.path:
                sys.path.insert(0, module_path)
        else:
            src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

        from github_downloader.gui_enhanced_full import main as enhanced_main

        enhanced_main()
    except Exception:
        log_dir = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader"
        )
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "crash.log")
        with open(log_path, "w") as f:
            f.write(traceback.format_exc())
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0,
            f"GitHub Downloader crashed:\n\n{traceback.format_exc()[:500]}\n\nLog saved to: {log_path}",
            "GitHub Downloader - Error",
            0x10,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
