"""
PyInstaller build for GitHub Repo Downloader FULL GUI executable
Includes PyQt6 for the desktop GUI mode.
"""
from PyInstaller.__main__ import run

opts = [
    'main.py',
    '--name=GitHubDownloader-GUI',
    '--console',
    '--onefile',
    '--clean',
    '--noconfirm',
    '--add-data=github_downloader;github_downloader',
    '--hidden-import=github_downloader',
    '--hidden-import=github_downloader.gui',
    '--hidden-import=github_downloader.gui.cli',
    '--hidden-import=github_downloader.gui.managers',
    '--hidden-import=github_downloader.gui.threads',
    '--hidden-import=github_downloader.gui.dialogs',
    '--hidden-import=github_downloader.downloader',
    '--hidden-import=github_downloader.github_api',
    '--hidden-import=github_downloader.user_auth',
    '--hidden-import=github_downloader.enhancements',
    '--hidden-import=github_downloader.gui_enhanced',
    '--hidden-import=requests',
    '--hidden-import=git',
    '--hidden-import=cryptography',
]

run(opts)
