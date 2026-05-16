@echo off
echo Starting Background Download...
echo This will run independently and download all 831 repos.
echo.
cd /d C:\temp\velvet-sojourner
start /min cmd /c "python download_all.py > download_background.log 2>&1"
echo.
echo Download started in background.
echo Check progress: type download_background.log
echo.
pause
