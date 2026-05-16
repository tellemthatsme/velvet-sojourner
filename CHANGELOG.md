# Changelog

## v2.1.0 — 2026-05-15

### Added
- Product landing page at `docs/product.html`
- 3 screenshots of the repo browser web index
- Screenshot gallery on product page
- `docs/QA_TOOL.md` — full QA tool documentation
- `docs/DOWNLOADER.md` — downloader CLI reference
- `docs/DEPLOYER_API.md` — deployer API endpoint reference
- `docs/QUICKSTART.md` — step-by-step getting started guide
- MIT LICENSE files added to 11 repos that were missing them
- QA tool now recognizes CC0, Creative Commons, and Community licenses

### Fixed
- License check in `qa_all_repos.py`: down from 18 false positives to 0
- Zero-byte file check: ignores git internals, `__init__.py`, `.nojekyll`, `.DS_Store`
- Root README updated to reflect current 843-repo count and live Vercel URLs

### Security
- 837 exposed GitHub tokens stripped from git remote URLs

## v2.0.0 — 2026-05-10

### Added
- 843 repos collected and scored (A/B/C tiers)
- Batch enhancement (LICENSE, Dockerfile, .gitignore, README) on all repos
- 32-category taxonomy in `docs/repo-categories.json`
- 501 KB searchable web index at `docs/repo-browser.html`
- Expanded docs for top 50 A-tier repos (10 sections each)
- 36 curated subset exports
- `GitHubDownloader-CLI.exe` (19 MB, 8 commands)
- `GitHubDownloader-GUI.exe` (48 MB, PyQt6)
- Docker platform with 7 services
- FastAPI deployer with background async scan
- Consulting page deployed to Vercel
- SaaS landing page deployed to Vercel
- `AgentForge-Product-v2.zip` (18 MB)
- Competitor pricing analysis
- Gumroad listing copy (3 tiers)
- 7-channel outreach templates

## v1.0.0 — 2026-04-20

### Added
- Initial repo collection (740 repos)
- Basic audit and scoring
- Documentation inventory
- Category taxonomy (initial 7 categories)
