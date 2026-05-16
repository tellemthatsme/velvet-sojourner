# AgentForge Platform

7-service Docker infrastructure for deploying AI agent repositories.

## Quick Start

```bash
# Linux/macOS
curl -sSL https://agentforge-consulting.vercel.app/install.sh | bash

# Windows (PowerShell)
# Download and run install.ps1

# Or manually:
docker compose up -d
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Traefik | 80, 443 | Reverse proxy + SSL |
| Postgres | 5432 | Database |
| Redis | 6379 | Cache/queue |
| n8n | 5678 | Workflow automation |
| Deployer | 8000 | Auto-deployment API |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Dashboards |

## API

The Deployer API provides 8 endpoints for browsing and deploying repos.

```python
from sdk import AgentForge
af = AgentForge("http://localhost:8000")

# List all repos
repos = af.list_repos(limit=10)

# Deploy a repo
result = af.deploy("litellm", env_vars={"PORT": "8080"})
```

Full API reference: `deployer/main.py` or http://localhost:8000/docs

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REPOS_DIR` | `/repos` | Repositories directory |
| `TRAEFIK_ACM_EMAIL` | — | Let's Encrypt email |

## Deployment

```bash
# Pull all services (requires network)
docker compose up -d

# Build deployer locally
docker compose build deployer
docker compose up -d deployer
```
