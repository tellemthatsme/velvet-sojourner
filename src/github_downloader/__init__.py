"""
GitHub Repo Downloader Package v2.5.0
"""

__version__ = "2.5.0"
__author__ = "User"

__all__ = ["main"]


def main():
    from github_downloader.gui_enhanced_full import main as gui_main

    gui_main()
