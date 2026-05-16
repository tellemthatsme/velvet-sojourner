@echo off
REM GitHub Repo Downloader - Build Script for Windows

echo ============================================
echo GitHub Repo Downloader - Build Script
echo ============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://python.org
 exit /b     pause
   1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building Windows executable...
pyinstaller build_exe.py --clean

echo.
echo ============================================
if exist "dist\GitHubDownloader.exe" (
    echo Build successful!
    echo Executable: dist\GitHubDownloader.exe
) else (
    echo Build may have failed. Check dist folder.
)

echo.
pause
