"""
PyInstaller build script for GitHub Repo Downloader CLI executable
No GUI dependencies — pure CLI, smaller, faster startup.
"""
from PyInstaller.__main__ import run

opts = [
    'main.py',
    '--name=GitHubDownloader',
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
    '--exclude-module=PyQt6',
    '--exclude-module=PyQt5',
    '--exclude-module=tkinter',
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=pandas',
    '--exclude-module=PIL',
]

run(opts)
