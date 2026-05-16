@echo off
REM Charm Crush Session Manager - Build Script for Windows

echo ============================================
echo Charm Crush Session Manager - Build Script
echo ============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building Windows executable...
pyinstaller build_exe.py --clean

echo.
echo ============================================
if exist "dist\CharmCrush.exe" (
    echo Build successful!
    echo Executable: dist\CharmCrush.exe
) else (
    echo Build may have failed. Check dist folder.
)

echo.
pause
