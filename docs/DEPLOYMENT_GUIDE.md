# AgentForge — Deployment Guide

**Last updated:** 2026-05-17

---

## Platform Overview

The AgentForge platform is a Docker Compose stack with 7 services:

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| Traefik | traefik:v3.0 | 80, 443, 8080 | Reverse proxy + SSL |
| Deployer API | Custom build | 8000 | Repo deployment API |
| n8n | n8nio/n8n:latest | 5678 | Workflow automation |
| Postgres | postgres:16-alpine | 5432 | Database |
| Redis | redis:7-alpine | 6379 | Cache |
| Prometheus | prom/prometheus:latest | 9090 | Metrics collection |
| Grafana | grafana/grafana:latest | 3001 | Monitoring dashboards |

**Commented out (requires GHCR access on VPS):**
- LiteLLM (ghcr.io/berriai/litellm) — LLM API gateway
- Open WebUI (ghcr.io/open-webui/open-webui) — Chat interface

---

## Prerequisites

- VPS with Docker (Hetzner CX21, $11/mo recommended)
- Domain name (optional, for production)
- SSH access to VPS
- 4 GB RAM minimum, 8 GB recommended

---

## Step 1: VPS Setup

### Hetzner Cloud (Recommended)

1. Create account at **console.hetzner.cloud**
2. Create project: `agentforge`
3. Create server:
   - Type: CX21 (2 vCPU, 4 GB RAM, 40 GB SSD)
   - Image: Ubuntu 24.04
   - Location: Nuremberg or Helsinki
   - SSH key: Add your public key
4. Note the server IP address

### Install Docker

```bash
ssh root@YOUR_VPS_IP
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker
docker compose version
```

---

## Step 2: Deploy Platform

### Clone Repository

```bash
cd /opt
git clone <your-repo-url> agentforge
cd agentforge/deploy-ready/agentforge-platform
```

### Configure Environment

```bash
cp .env.example .env
nano .env
```

Set these values:

```env
LITELLM_MASTER_KEY=sk-your-master-key
WEBUI_SECRET_KEY=your-webui-secret
N8N_PASSWORD=your-n8n-password
DEPLOYER_SECRET=your-deployer-secret
GRAFANA_PASSWORD=your-grafana-password
```

### Uncomment GHCR Services

Edit `docker-compose.yml` and uncomment the `litellm` and `open-webui` services (lines 21-63).

### Deploy

```bash
docker compose up -d
```

### Verify

```bash
docker compose ps
# All services should show "running"

docker compose logs deployer
# Should show "Uvicorn running on http://0.0.0.0:8000"
```

---

## Step 3: Configure Traefik

Traefik handles routing and SSL automatically.

### Local Access (no domain)

| Service | URL |
|---------|-----|
| Deployer API | http://YOUR_IP:8000 |
| n8n | http://YOUR_IP:5678 |
| Grafana | http://YOUR_IP:3001 |
| Prometheus | http://YOUR_IP:9090 |
| Traefik Dashboard | http://YOUR_IP:8080 |

### With Domain

1. Point domain to VPS IP (A record)
2. Create subdomains: `forge`, `automate`, `monitor`, `api`, `chat`
3. Update Traefik labels in `docker-compose.yml`
4. Traefik auto-provisions Let's Encrypt SSL certificates

---

## Step 4: Test Deployer API

```bash
# List available repos
curl http://YOUR_IP:8000/api/repos | head -20

# Get repo details
curl http://YOUR_IP:8000/api/repos/litellm

# Deploy a repo
curl -X POST http://YOUR_IP:8000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{"repo": "litellm", "port": 4000}'

# List deployments
curl http://YOUR_IP:8000/api/deployments
```

---

## Step 5: Configure n8n

1. Open http://YOUR_IP:5678
2. Set up admin account (password from .env)
3. Create workflows:
   - **Repo monitor** — Check for updates every 24h
   - **Deployment notifier** — Slack/email on deploy
   - **Quality scan** — Run QA checks on new repos

---

## Step 6: Set Up Monitoring

### Grafana

1. Open http://YOUR_IP:3001
2. Login: admin / password from .env
3. Add Prometheus as data source (http://prometheus:9090)
4. Import dashboards:
   - Docker monitoring (ID: 1229)
   - Node exporter (ID: 1860)
   - Postgres monitoring (ID: 9628)

### Prometheus

Verify targets at http://YOUR_IP:9090/targets — all should be "UP".

---

## Troubleshooting

### Service Won't Start

```bash
docker compose logs <service-name>
# Check for specific errors
```

### Port Already in Use

```bash
sudo lsof -i :8000
# Kill conflicting process or change port in docker-compose.yml
```

### GHCR Pull Fails

This happens on restricted networks. On VPS it should work. If not:

```bash
# Try with authentication
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker compose pull
```

### Out of Memory

```bash
# Check memory usage
free -h

# Stop non-essential services
docker compose stop prometheus grafana

# Or upgrade VPS to CX31 (8 GB RAM)
```

### Deployer API Returns 500

```bash
# Check database connection
docker compose exec deployer python -c "import psycopg2; psycopg2.connect('postgresql://postgres:postgres@postgres:5432/agentforge')"

# Check repos directory mount
docker compose exec deployer ls /repos
# Should show 843 repo directories
```

---

## Backup and Restore

### Backup

```bash
# Database backup
docker compose exec postgres pg_dump -U postgres agentforge > backup_$(date +%Y%m%d).sql

# Volume backup
docker run --rm -v agentforge-platform_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

### Restore

```bash
docker compose exec -T postgres psql -U postgres agentforge < backup_20260517.sql
```

---

## Security Hardening

1. **Firewall:** Only open ports 80, 443, 22
2. **SSH:** Disable password auth, use key-only
3. **Environment:** Never commit .env files
4. **Updates:** Run `docker compose pull && docker compose up -d` monthly
5. **Backups:** Automated daily database backups
6. **SSL:** Let Traefik handle certificates automatically
