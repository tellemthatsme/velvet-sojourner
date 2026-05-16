# AgentForge Platform Installer (Windows)
param(
    [string]$Dir = "agentforge-platform"
)

Write-Host "=== AgentForge Platform Installer ===" -ForegroundColor Cyan
Write-Host ""

# Check Docker
try {
    $dockerVer = docker --version
    Write-Host "Docker: $dockerVer" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker not found. Install from https://docs.docker.com/get-docker/" -ForegroundColor Red
    exit 1
}

# Download platform
if (Test-Path $Dir) {
    Write-Host "Directory $Dir exists. Pulling latest..." -ForegroundColor Yellow
    Push-Location $Dir
    git pull
    Pop-Location
} else {
    Write-Host "Downloading AgentForge Platform..." -ForegroundColor Yellow
    git clone --depth 1 "https://github.com/agentforge/platform.git" $Dir
}

Write-Host ""
Write-Host "=== Starting Platform ===" -ForegroundColor Cyan
Push-Location $Dir
docker compose up -d
Pop-Location

Write-Host ""
Write-Host "=== Ready ===" -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:8080"
Write-Host "  API:        http://localhost:8000/docs"
Write-Host "  n8n:        http://localhost:5678"
Write-Host "  Grafana:    http://localhost:3001"
