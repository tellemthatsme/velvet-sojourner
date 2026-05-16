# AgentForge Quickstart

From zero to running in 5 minutes.

---

## 1. Browse the Collection

Open `docs/repo-browser.html` in any browser. Search by name, filter by category or language, view repo details and download status.

## 2. QA All Repos

```bash
python qa_all_repos.py --quick
```

Verifies all 843 repos have READMEs, licenses, Dockerfiles, and aren't corrupt. Full report at `qa-results/qa-report.json`.

## 3. Download Repos Via CLI

Use the standalone EXE (no Python needed):

```bash
deploy-ready\github-downloader\GitHubDownloader-CLI.exe health --path ./repos
deploy-ready\github-downloader\GitHubDownloader-CLI.exe export --path ./repos --format csv --output report.csv
```

## 4. Deploy Docker Platform

```bash
cd deploy-ready\agentforge-platform
docker compose up -d
```

Access:
- Dashboard: http://localhost:8080
- API: http://localhost:8000/docs
- n8n: http://localhost:5678
- Grafana: http://localhost:3001

## 5. Deploy Landing Pages

```bash
cd deploy-ready\consulting-page
vercel --prod

cd deploy-ready\saas-landing-page
vercel --prod
```

## 6. Launch Product

- Upload `deploy-ready/AgentForge-Product-v2.zip` to Gumroad
- Paste listing copy from `deploy-ready/gumroad-product/GUMROAD_LISTING.md`
- Send outreach from `deploy-ready/OUTREACH_MESSAGES.md`

---

## Architecture

```
User → Vercel (landing pages) → Gumroad (product sales)
     → VPS (Docker platform) → Deployer API → repo deployment
     → Consulting (direct engagement)
```

## Key Files

| File | Purpose |
|------|---------|
| `docs/repo-browser.html` | Offline searchable web index (501 KB) |
| `docs/QA_TOOL.md` | How to run repo validation |
| `docs/DOWNLOADER.md` | CLI/GUI EXE commands |
| `docs/DEPLOYER_API.md` | FastAPI endpoint reference |
| `docs/competitor-pricing.md` | Pricing strategy ($49-$499) |
| `deploy-ready/AgentForge-Product-v2.zip` | Product download (18 MB) |
| `deploy-ready/OUTREACH_MESSAGES.md` | 7-channel marketing copy |
| `MASTER_REPO_DIRECTORY.md` | Full 112 KB repo index |
| `LAUNCH_RUNBOOK.md` | Step-by-step launch sequence |
