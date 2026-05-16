# Test script to capture stderr from the EXE
$errLog = "$env:TEMP\gh_stderr.log"
$outLog = "$env:TEMP\gh_stdout.log"

Write-Host "Starting GitHubDownloader..."
$proc = Start-Process "C:\temp\velvet-sojourner\dist\GitHubDownloader.exe" -RedirectStandardError $errLog -RedirectStandardOutput $outLog -PassThru -WindowStyle Normal

Write-Host "Started PID: $($proc.Id)"
Write-Host ""
Write-Host "===== INSTRUCTIONS ====="
Write-Host "1. Wait for the app window to appear"
Write-Host "2. Click the 'Download All Accounts' button"
Write-Host "3. Wait 15 seconds for the operation to complete"
Write-Host "4. Close the app window"
Write-Host "5. Press ENTER here to see results"
Write-Host "========================"
Write-Host ""

Read-Host "Press ENTER after clicking the button and waiting..."

# Give it a moment to write logs
Start-Sleep 2

Write-Host ""
Write-Host "===== STDERR OUTPUT ====="
if (Test-Path $errLog) {
    Get-Content $errLog
} else {
    Write-Host "(No stderr log file found)"
}

Write-Host ""
Write-Host "===== STDOUT OUTPUT ====="
if (Test-Path $outLog) {
    Get-Content $outLog
} else {
    Write-Host "(No stdout log file found)"
}

# Cleanup
if (!$proc.HasExited) {
    Write-Host ""
    Write-Host "Stopping process..."
    Stop-Process $proc.Id -Force -ErrorAction SilentlyContinue
}
