@echo off
REM GitHub Repo Downloader v2.6.0 - Release Packaging Script
REM Creates a distributable release package with all necessary files

echo ============================================
echo GitHub Repo Downloader v2.6.0 - Release
echo ============================================
echo.

setlocal
cd /d "%~dp0"

set VERSION=2.6.0
set RELEASE_DIR=release\GitHubDownloader-v%VERSION%-win-x64

if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"

echo [1/4] Building executable with PyInstaller...
pyinstaller GitHubDownloader.spec --clean

if not exist "dist\GitHubDownloader.exe" (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo       Build completed.

echo.
echo [2/4] Copying files to release folder...
copy "dist\GitHubDownloader.exe" "%RELEASE_DIR%\" >nul
copy "README.md" "%RELEASE_DIR%\" >nul
copy "requirements.txt" "%RELEASE_DIR%\" >nul

mkdir "%RELEASE_DIR%\assets" 2>nul
copy "icons\app.ico" "%RELEASE_DIR%\assets\" >nul

echo NOTE: This executable is self-contained and does not require Python. > "%RELEASE_DIR%\PORTABLE.txt"
echo Simply run GitHubDownloader.exe to start the application. >> "%RELEASE_DIR%\PORTABLE.txt"
echo. >> "%RELEASE_DIR%\PORTABLE.txt"
echo First run: Add your GitHub Personal Access Token via the + Add Account button. >> "%RELEASE_DIR%\PORTABLE.txt"
echo Create tokens at: https://github.com/settings/tokens >> "%RELEASE_DIR%\PORTABLE.txt"
echo Required scopes: repo, read:user >> "%RELEASE_DIR%\PORTABLE.txt"

echo       Files copied.

echo.
echo [3/4] Creating launcher batch file...
(
echo @echo off
echo REM Start GitHub Downloader
echo "%%~dp0GitHubDownloader.exe"
) > "%RELEASE_DIR%\Start GitHub Downloader.bat"

echo.
echo [4/4] Creating ZIP archive...
powershell -command "Compress-Archive -Path '%RELEASE_DIR%' -DestinationPath 'release\GitHubDownloader-v%VERSION%-win-x64.zip' -Force"

echo.
echo ============================================
echo Release package created!
echo ============================================
echo.
echo Location: %CD%\%RELEASE_DIR%
echo Archive:  %CD%\release\GitHubDownloader-v%VERSION%-win-x64.zip
echo.
echo EXE Size:
powershell -command "(Get-Item 'dist\GitHubDownloader.exe').Length / 1MB | ForEach-Object { '{0:N2} MB' -f $_ }"

endlocal
pause