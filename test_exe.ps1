$errLog = "$env:TEMP\ghdl_err.log"
$proc = Start-Process -FilePath "dist\GitHubDownloader.exe" -PassThru -RedirectStandardError $errLog
Start-Sleep -Seconds 5
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
if (Test-Path $errLog) {
    Write-Host "=== ERROR LOG ==="
    Get-Content $errLog
} else {
    Write-Host "No error log created"
}
