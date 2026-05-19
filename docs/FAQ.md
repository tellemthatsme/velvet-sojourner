# AgentForge — Frequently Asked Questions

**Last updated:** 2026-05-17

---

## General

### What is AgentForge?

AgentForge is a curated research product analyzing 843 open-source AI agent repositories. Every repo has been cloned, scored for quality (0-116), license-verified, Docker-tested, and organized into 32 categories. We sell the analysis, not the code — the repos remain free on GitHub.

### How many repos are included?

843 repositories, totaling 4.4 GB and 194,645 files. They span 32 categories including AI App Builders (179), Trading Bots (107), Developer Tools (27), MCP Servers (13), and AI Frameworks (13).

### Is this just a list of GitHub URLs?

No. It's a complete research product — every repo was cloned, analyzed, scored, and documented. You get quality scores (0-116), license audits, Docker readiness flags, 32 category tags, clone analysis, curated subsets, and a searchable catalog in Markdown + CSV + JSON. The repos themselves remain on GitHub (free to clone), but the analysis work that would take 200+ hours is done for you.

### What's the scoring system?

Each repo is scored 0-116 based on six weighted criteria:
- Code structure (0-20)
- Documentation completeness (0-20)
- License presence (0-10)
- Docker support (0-15)
- Test coverage signals (0-15)
- Maintenance activity (0-15)
- Clone penalty (-20 if duplicate detected)

Tiers: A-Tier (57+, 572 repos), B-Tier (38-56, 168 repos), C-Tier (<38, 103 repos).

### Can I use these repos commercially?

License status is documented for every repo. MIT and Apache-licensed repos are safe for commercial use. GPL repos require you to share your source code. Repos without clear licenses are flagged — use at your own discretion or contact the original authors. The Enterprise tier includes redistribution rights for your own products built using our analysis.

---

## Product

### What's the download size?

The research product is a compact ZIP (~18 MB) containing the catalog, reports, scores, and documentation. The underlying repos total 4.4 GB across 194,000 files — those remain on GitHub. You get the analysis, not the raw code.

### What format is the catalog?

Three formats: Markdown (human-readable), CSV (spreadsheet/database import), and JSON (programmatic access). All three are included in every tier.

### How often is this updated?

Quarterly updates are included free with all tiers. We track new repos, update scores, refresh categories, and re-run the full QA pipeline. You'll receive download links automatically.

### What's the refund policy?

30-day money-back guarantee, no questions asked. If the index doesn't save you at least 10 hours of research time, we'll refund you in full.

### Do you provide support?

The index is a self-service research product. Professional tier includes 30 days of email support. Enterprise includes 90 days plus custom integration help. For done-for-you deployment, see our consulting packages at agentforge-consulting.vercel.app.

---

## Pricing

### Why does this cost money if the repos are open-source?

You're not paying for the code. You're paying for curation, time saved, and the work of making 843 repos actually usable. All the value is in the signal extraction. The repos are free on GitHub. The analysis is the product.

### Why three pricing tiers?

- **Starter ($49):** For individual developers exploring the AI agent landscape
- **Professional ($149):** For teams who need license audits, custom filtering, and support
- **Enterprise ($299):** For organizations needing redistribution rights and priority support

Each tier targets a different use case and budget.

### Can I get a specific subset (e.g., only trading bots)?

The full index is a single download. You can filter by category using the CSV or JSON catalog. Enterprise tier includes custom filtering and subset packaging.

### Is there a free tier?

No free tier, but the 30-day money-back guarantee means you can try it risk-free. If it doesn't deliver value, you get a full refund.

---

## Technical

### How was the analysis done?

Custom Python pipeline:
1. Clone repos via GitHub API
2. Analyze directory structure and file types
3. Auto-generate missing documentation (READMEs, LICENSE, .gitignore)
4. Run 9 QA checks (directories, READMEs, licenses, Dockerfiles, git status, integrity, sizing, tests, categories)
5. Score each repo 0-116
6. Classify into tiers (A/B/C)
7. Assign to 32 categories
8. Detect clones (265 found across 6 patterns)
9. Strip exposed tokens (837 found)
10. Generate catalog exports (MD, CSV, JSON)

### What tools were used?

Python, GitPython, PyInstaller (EXE builds), FastAPI (Deployer API), Docker Compose (platform), PostgreSQL, Redis, Traefik (proxy), n8n (automation), Prometheus + Grafana (monitoring).

### Can I run the analysis pipeline myself?

Yes. All scripts are in the project repository:
- `scan_all_repos.py` — Scoring and classification
- `qa_all_repos.py` — 9-check QA system
- `enhance_all_repos.py` — Batch enhancement
- `categorize_repos.py` — Category assignment
- `strip_tokens.py` — Token stripping

### What's the Docker platform?

A Docker Compose stack with 7 services: Traefik (reverse proxy), Deployer API (repo deployment), n8n (workflow automation), Postgres (database), Redis (cache), Prometheus (metrics), Grafana (dashboards). Plus LiteLLM and Open WebUI (commented out, require GHCR access).

---

## Usage

### How do I find the best repos for my use case?

1. Open the CSV export in a spreadsheet
2. Filter by category (e.g., "Trading Bots")
3. Sort by score (descending)
4. Check license column for commercial compatibility
5. Review the top 5-10 repos in detail

### What if a repo I need isn't included?

Contact us with the repo URL. We'll analyze it and add it to the next quarterly update. Enterprise customers get priority additions.

### How do I deploy a repo from the index?

1. Clone the repo from GitHub (URL is in the catalog)
2. Check if it has a Dockerfile (flagged in the catalog)
3. Run `docker build -t my-app . && docker run -p 8080:8080 my-app`
4. Or use the Deployer API for one-click deployment

### Can I contribute new repos?

Yes! See CONTRIBUTING.md for guidelines. We accept repos that fit our 32 categories and meet minimum quality standards.

---

## Business

### Who is this for?

- **AI Developers** — Skip weeks of repo research. Start with the best code.
- **Startup Founders** — Find your technical foundation before building.
- **AI Agencies & Consultants** — Deliver faster with a curated library.
- **Solo Indie Hackers** — Build MVPs from proven open-source components.
- **Engineering Leaders** — Evaluate the landscape before committing to a framework.
- **Researchers & Students** — Study real-world agent implementations at scale.

### How many customers do you have?

We're in early launch phase. The product is designed for 100+ developers in the first quarter.

### Can I resell this product?

Only with the Enterprise tier, which includes redistribution rights. Starter and Professional tiers are for personal/internal use only.

### Do you offer white-label or custom versions?

Yes, Enterprise tier includes custom integration support. Contact us at agentforge-consulting.vercel.app for details.
