@echo off
REM GitHub Repo Downloader v2.5.0 - Build Script for Windows

echo ============================================
echo GitHub Repo Downloader v2.5.0 - Build
echo ============================================

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building Windows executable...
pyinstaller GitHubDownloader.spec --clean

echo.
echo ============================================
if exist "dist\GitHubDownloader.exe" (
    echo Build successful!
    echo Executable: dist\GitHubDownloader.exe
) else (
    echo Build may have failed. Check output above.
)

echo.
pause