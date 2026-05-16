# Test running the packaged EXE with PowerShell capturing all output
$ErrorActionPreference = "Continue"
$start = Get-Date
$errLog = "$env:TEMP\ghdl_out_$PID.log"

Write-Host "Starting EXE..."
$proc = Start-Process -FilePath "dist\GitHubDownloader.exe" -PassThru -NoNewWindow

Write-Host "Process started with ID: $($proc.Id)"
Start-Sleep -Seconds 3

if ($proc.HasExited) {
    Write-Host "Process exited with code: $($proc.ExitCode)"
} else {
    Write-Host "Process is still running"
    Stop-Process -Id $proc.Id -Force
}
