"""
PyInstaller build for GitHub Repo Downloader CLI-ONLY executable
No PyQt6 — suitable for headless/server environments.
"""
from PyInstaller.__main__ import run

opts = [
    'cli_main.py',
    '--name=GitHubDownloader-CLI',
    '--console',
    '--onefile',
    '--clean',
    '--noconfirm',
    '--add-data=github_downloader;github_downloader',
    '--hidden-import=github_downloader',
    '--hidden-import=github_downloader.gui',
    '--hidden-import=github_downloader.gui.cli',
    '--hidden-import=github_downloader.downloader',
    '--hidden-import=github_downloader.github_api',
    '--hidden-import=github_downloader.user_auth',
    '--hidden-import=github_downloader.enhancements',
    '--hidden-import=requests',
    '--hidden-import=git',
    '--hidden-import=cryptography',
    '--exclude-module=PyQt6',
    '--exclude-module=PyQt5',
    '--exclude-module=PySide6',
    '--exclude-module=PySide2',
]

run(opts)
