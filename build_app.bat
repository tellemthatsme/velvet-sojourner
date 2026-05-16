@echo off
echo ==========================================
echo   BUILDING GITHUB DOWNLOADER EXE
echo ==========================================
echo.

cd /d C:\temp\velvet-sojourner

echo Step 1: Checking requirements...
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import requests; print('requests OK')"
python -c "import cryptography; print('cryptography OK')"

echo.
echo Step 2: Cleaning old build...
if exist dist\GitHubDownloader.exe (
    echo Backing up old executable...
    move /Y dist\GitHubDownloader.exe dist\GitHubDownloader.exe.bak >nul 2>&1
)
if exist build rmdir /S /Q build
if exist __pycache__ rmdir /S /Q __pycache__

echo.
echo Step 3: Building executable...
pyinstaller --name=GitHubDownloader ^
    --onefile ^
    --windowed ^
    --add-data "src/github_downloader;github_downloader" ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import requests ^
    --hidden-import cryptography ^
    --hidden-import sqlite3 ^
    --hidden-import urllib.parse ^
    --hidden-import webbrowser ^
    --hidden-import json ^
    --hidden-import datetime ^
    --clean ^
    src/main.py

echo.
echo Step 4: Verifying build...
if exist dist\GitHubDownloader.exe (
    echo SUCCESS: dist\GitHubDownloader.exe created
    for %%F in (dist\GitHubDownloader.exe) do echo Size: %%~zF bytes
) else (
    echo ERROR: Build failed
)

echo.
echo ==========================================
echo   BUILD COMPLETE
echo ==========================================
pause
