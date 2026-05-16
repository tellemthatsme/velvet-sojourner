# AgentForge Deployer API

FastAPI backend for browsing, searching, and deploying repos. Runs at `http://localhost:8000`.

## Start

```bash
docker compose up -d deployer
# or directly:
cd deploy-ready/agentforge-platform/deployer
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoints

### `GET /` — Dashboard

Serves the static web dashboard. Automatically shows repo index once background scan completes.

### `GET /api/repos` — List repos

Query params:

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Filter by name or description |
| `category` | string | Filter by category |
| `language` | string | Filter by language |
| `deployable_only` | bool | Only repos with Dockerfile/compose |
| `limit` | int | Results per page (max 500, default 50) |
| `offset` | int | Pagination offset |

Returns `{ total, offset, limit, repos: [...], scanning }`.

### `GET /api/repos/{name}` — Single repo

Returns full metadata for one repository.

### `GET /api/categories` — Category counts

Returns `{ category_name: count, ... }`.

### `GET /api/stats` — Server stats

Returns total repos, size, files, deployable count, categories, top 10.

### `POST /api/deploy/{name}` — Deploy a repo

Body (JSON):

```json
{
  "repo_name": "my-repo",
  "env_vars": { "KEY": "value" },
  "port_mapping": { "8080": 80 }
}
```

Generates docker-compose.yml in `/deployments/{id}/` with Traefik labels.

### `GET /api/deployments` — List deployments

Returns all active deployment directories.

### `POST /api/scan` — Rescan repos

Triggers a fresh scan of the repos directory.

## Scan Behavior

- Runs in background via `asynccontextmanager` — server starts instantly
- Uses `os.scandir` (no `rglob(*)`) — handles 194k files without blocking
- `/api/repos` returns `scanning: true` until first scan completes (max 5s wait)
- Sorts repos by size descending
