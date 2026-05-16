@echo off
REM GitHub Repo Downloader v2.5.0 - Enhanced Build Script
REM Builds the self-contained enhanced GUI (no external module imports)

echo ============================================
echo GitHub Repo Downloader v2.5.0 - Build
echo ============================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [OK] Python found

if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo.
echo [INFO] Building with PyInstaller spec...
pyinstaller GitHubDownloader.spec --clean

echo.
echo ============================================
if exist "dist\GitHubDownloader.exe" (
    echo [SUCCESS] Build completed!
    echo Executable: %CD%\dist\GitHubDownloader.exe
    echo.
    echo To run in dev mode:
    echo   python src\github_downloader\gui_enhanced_full.py
) else (
    echo [ERROR] Build failed. Check output above.
)

echo.
pause