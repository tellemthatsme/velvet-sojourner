# Disable GPU Acceleration Guide

**Goal:** Prevent freezing, crashes, and MCP connection errors by disabling GPU hardware acceleration in AI coding tools.

## Quick Fix (PowerShell Script)

Run this in an Administrator PowerShell terminal:

```powershell
Write-Host "=== Disabling GPU Acceleration ===" -ForegroundColor Cyan

$apps = @(
    @{Name="Cursor"; Path="$env:APPDATA\Cursor\argv.json"},
    @{Name="Trae"; Path="$env:APPDATA\Trae\argv.json"},
    @{Name="Antigravity"; Path="$env:APPDATA\Antigravity\argv.json"},
    @{Name="AbacusAI"; Path="$env:APPDATA\AbacusAI\argv.json"},
    @{Name="VS Code"; Path="$env:APPDATA\Code\argv.json"}
)

foreach ($app in $apps) {
    $dir = Split-Path $app.Path -Parent
    if (Test-Path $dir) {
        $content = @{args=@("--disable-gpu")}
        $content | ConvertTo-Json | Set-Content $app.Path -Encoding UTF8
        Write-Host "✅ $($app.Name) - GPU disabled" -ForegroundColor Green
    } else {
        Write-Host "❌ $($app.Name) - Not found" -ForegroundColor Red
    }
}

Write-Host "`n=== DONE ===" -ForegroundColor Cyan
Write-Host "Restart all apps for changes to take effect."
```

## Manual Steps

1.  **Cursor:** `Ctrl+,` > Search "gpu" > Check "Disable Hardware Acceleration".
2.  **VS Code:** `Ctrl+Shift+P` > "Configure Runtime Arguments" > Add `"disable-hardware-acceleration": true`.
3.  **Others:** locate `argv.json` in `%APPDATA%` and add `{"args": ["--disable-gpu"]}`.

## Verification
Restart the application. If the white screen or freezing issues persist, ensure the file `argv.json` was correctly saved.
