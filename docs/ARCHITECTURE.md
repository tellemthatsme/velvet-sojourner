# AgentForge — Architecture Overview

**Last updated:** 2026-05-17

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentForge Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │  Repo    │   │ Analysis │   │  Scoring │   │ Catalog  │ │
│  │ Collector│──▶│ Pipeline │──▶│  Engine  │──▶│ Generator│ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ 843 repos│   │ 9 QA     │   │ 0-116    │   │ MD/CSV/  │ │
│  │ 4.4 GB   │   │ checks   │   │ scores   │   │ JSON     │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Docker Platform                         │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │   │
│  │  │Traefik │ │Deployer│ │  n8n   │ │ LiteLLM│        │   │
│  │  │:80/443 │ │:8000   │ │:5678   │ │:4000   │        │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │   │
│  │  │Postgres│ │ Redis  │ │Promethe│ │ Grafana│        │   │
│  │  │:5432   │ │:6379   │ │us:9090 │ │:3001   │        │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Repo Collection Pipeline

**Purpose:** Clone and organize 843 GitHub repositories.

**Flow:**
```
repo-list.txt → GitHubDownloader → /repos/{name}/ → 843 directories
```

**Key scripts:**
- `scan_all_repos.py` — Scores and classifies all repos
- `download_all.py` — Bulk download from repo list
- `enhance_all_repos.py` — Batch enhancement (LICENSE, Dockerfile, .gitignore, README)

**Enhancement process:**
1. Detect language (Python, JS, TS, etc.)
2. Generate appropriate LICENSE (MIT default)
3. Generate Dockerfile based on language
4. Generate .gitignore based on language
5. Generate README if missing

### 2. Analysis Pipeline

**Purpose:** Analyze each repo for quality signals.

**9 QA Checks:**
1. **Directories** — Repo has expected directory structure
2. **READMEs** — README.md exists and has content
3. **Licenses** — LICENSE file exists and is recognized
4. **Dockerfiles** — Dockerfile exists
5. **Git status** — Clean working tree
6. **Integrity** — No zero-byte files (excluding git internals)
7. **Sizing** — Reasonable file sizes
8. **Tests** — Test directory or test files present
9. **Categories** — Repo assigned to a category

**Scoring Algorithm (0-116):**
- Code structure: 0-20 points
- Documentation: 0-20 points
- License presence: 0-10 points
- Docker support: 0-15 points
- Test coverage signals: 0-15 points
- Maintenance activity: 0-15 points
- Clone penalty: -20 points (if duplicate detected)

**Tier Classification:**
- A-Tier: 57+ (572 repos) — Production-ready
- B-Tier: 38-56 (168 repos) — Usable with work
- C-Tier: <38 (103 repos) — Needs effort

### 3. Token Stripping

**Purpose:** Remove exposed GitHub tokens from git remote URLs.

**Process:**
1. Scan all `.git/config` files for `https://token@github.com`
2. Replace with `https://github.com`
3. Log stripped tokens for audit
4. Result: 837 tokens stripped across 843 repos

### 4. Web Index Generation

**Purpose:** Create searchable offline HTML catalog.

**Flow:**
```
repo data → JSON → repo-browser.html (501 KB)
```

**Features:**
- Instant search across 843 repos
- Filter by 32 categories
- Sort by size, tier, name
- PWA-enabled (manifest.json + sw.js)
- Works offline

### 5. Docker Platform

**Architecture:**
```
                    ┌─────────┐
                    │ Traefik │ :80/:443
                    └────┬────┘
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │Deployer │ │   n8n   │ │ LiteLLM │
        │ :8000   │ │ :5678   │ │ :4000   │
        └────┬────┘ └────┬────┘ └────┬────┘
             │           │           │
        ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
        │Postgres │ │ Postgres│ │ Postgres│
        │ :5432   │ │ :5432   │ │ :5432   │
        └─────────┘ └─────────┘ └─────────┘
```

**Service roles:**
- **Traefik:** Reverse proxy, SSL termination, routing
- **Deployer API:** FastAPI app that deploys repos via Docker
- **n8n:** Workflow automation (monitoring, notifications)
- **LiteLLM:** Unified LLM API gateway (OpenAI-compatible)
- **Open WebUI:** Self-hosted ChatGPT alternative
- **Postgres:** Shared database for all services
- **Redis:** Caching and session management
- **Prometheus:** Metrics collection
- **Grafana:** Monitoring dashboards

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Collection | Python, GitPython | Repo cloning and management |
| Analysis | Python, os, pathlib | File system analysis |
| Scoring | Python, custom algorithm | Quality evaluation |
| Web Index | HTML, JS, CSS | Offline searchable catalog |
| Platform | Docker Compose | Service orchestration |
| API | FastAPI, Python | Deployer REST API |
| Database | PostgreSQL 16 | Persistent storage |
| Cache | Redis 7 | Session and data caching |
| Proxy | Traefik v3 | Reverse proxy + SSL |
| Automation | n8n | Workflow engine |
| Monitoring | Prometheus + Grafana | Metrics and dashboards |
| LLM Gateway | LiteLLM | Unified API for multiple LLMs |
| Chat UI | Open WebUI | Self-hosted chat interface |

---

## Data Flow

### Repo Collection → Analysis → Product

```
1. repo-list.txt (URLs)
       │
       ▼
2. GitHubDownloader clones repos → /repos/{name}/
       │
       ▼
3. enhance_all_repos.py adds LICENSE, Dockerfile, .gitignore, README
       │
       ▼
4. qa_all_repos.py runs 9 checks → qa-results/qa-report.json
       │
       ▼
5. scan_all_repos.py scores repos → tiered classification
       │
       ▼
6. categorize_repos.py assigns 32 categories → repo-categories.json
       │
       ▼
7. build_html.py generates repo-browser.html
       │
       ▼
8. package_product.py creates AgentForge-Product-v2.zip
```

---

## Design Decisions

### Why Python?
- Best ecosystem for file system operations
- Fast prototyping for analysis pipelines
- Native Git integration via GitPython
- Easy to package as EXE with PyInstaller

### Why Docker Compose?
- Single-file deployment
- Easy to understand and modify
- Works on any Linux VPS
- No Kubernetes complexity

### Why FastAPI?
- Automatic OpenAPI documentation
- Async support for background scans
- Type-safe with Pydantic
- Fast performance

### Why PostgreSQL?
- Shared database for all services
- Reliable and well-supported
- Easy backup and restore
- n8n and LiteLLM both support it natively

### Why 0-116 Scoring?
- Granular enough to differentiate repos
- Not arbitrary (based on 6 weighted criteria)
- Clone penalty creates clear separation
- Easy to explain to customers
