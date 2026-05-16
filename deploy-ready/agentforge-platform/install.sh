#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/agentforge/platform.git"
DIR="agentforge-platform"

echo "=== AgentForge Platform Installer ==="
echo ""

# Check Docker
if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker not found. Install from https://docs.docker.com/get-docker/"
    exit 1
fi

echo "Docker: $(docker --version)"

# Check Compose
if ! docker compose version &>/dev/null; then
    echo "ERROR: Docker Compose not found."
    exit 1
fi

echo "Compose: $(docker compose version)"

# Download platform
if [ -d "$DIR" ]; then
    echo "Directory $DIR already exists. Pulling latest..."
    cd "$DIR" && git pull
else
    echo "Downloading AgentForge Platform..."
    git clone --depth 1 "$REPO" "$DIR"
    cd "$DIR"
fi

echo ""
echo "=== Starting Platform ==="
docker compose up -d

echo ""
echo "=== Ready ==="
echo "  Dashboard:  http://localhost:8080"
echo "  API:        http://localhost:8000/docs"
echo "  n8n:        http://localhost:5678"
echo "  Grafana:    http://localhost:3001"
echo ""
echo "Run 'docker compose logs -f' to follow all logs."
