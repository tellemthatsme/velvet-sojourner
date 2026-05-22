# GitHub Repo Downloader

A powerful desktop application for downloading GitHub repositories with support for private repos, batch downloads, incremental sync, and webhook notifications.

## Screenshots

*(Screenshots coming soon — run `python main.py` to see the GUI)*

## Features

- **Private Repository Support** — Download private repos with PAT, OAuth2, GitHub CLI, or SSH
- **Batch Downloads** — Download 100+ repos at once from a file list
- **3 Download Methods** — Git Clone (with history), ZIP, TAR
- **Incremental Sync** — Only download changed files
- **Webhook Notifications** — Discord, Slack, Email
- **Full GUI** — 7 tabs: Download, Batch, Search, My Repos, Bookmarks, Sync, History
- **8 CLI Commands** — download, batch, verify, export, health, config, list, search
- **Dark/Light Theme** — Beautiful dark mode by default
- **Download History** — SQLite-powered tracking
- **Bookmarks** — Save and revisit repositories
- **Rate Limit Compliant** — 80% safety margin to avoid throttling

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | Public repos, CLI only, unlimited downloads |
| **Pro** | $19 | Private repos, GUI, batch download, incremental sync |
| **Team** | $49 | Multi-user, shared bookmarks, webhooks, priority support |

## Quick Start

### GUI Mode
```bash
cd github-downloader-new
python main.py
```

### CLI Mode
```bash
python main.py --cli download --url owner/repo -o ~/Downloads
python main.py --cli list --user username
python main.py --cli search -q "python web framework"
```

## Authentication

### Option 1: Personal Access Token (PAT) — Recommended
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Scope: `repo` (for private repos)
3. GUI: Account → GitHub Authentication → Enter token
4. CLI: `python main.py --cli download --url owner/repo -t ghp_your_token`

### Option 2: OAuth2
1. Create OAuth App: GitHub → Settings → Developer settings → OAuth Apps
2. Callback: `http://localhost:8080/callback`
3. Enter Client ID/Secret in app

### Option 3: GitHub CLI
```bash
gh auth login
```
App detects GitHub CLI session automatically.

### Option 4: SSH Keys
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add public key to GitHub Settings → SSH and GPG keys
```

## Download Methods

1. **Git Clone** — Full git repository with history (requires Git installed)
2. **Download ZIP** — Single ZIP file (fast, no Git needed)
3. **Download TAR.gz** — Single TAR file

## Rate Limits

| Method | Limit | App Limit (80%) |
|--------|-------|------------------|
| Unauthenticated | 60/hour | 48/hour |
| Authenticated (PAT/OAuth) | 5,000/hour | 4,000/hour |

## CLI Commands Reference

```bash
# Download a single repo
python main.py --cli download --url owner/repo -o ./output

# Batch download from file
python main.py --cli batch --file repos.txt -o ./output

# Verify downloaded repos
python main.py --cli verify --dir ./output

# Export metadata to JSON/CSV
python main.py --cli export --dir ./output --format json

# System health check
python main.py --cli health

# Show environment config
python main.py --cli config

# List user repos from GitHub
python main.py --cli list --user username

# Search GitHub repos
python main.py --cli search -q "keyword"
```

## Configuration

Edit `config.json`:
```json
{
  "rate_limit_margin": 0.8,
  "default_download_dir": "~/Downloads/github",
  "max_concurrent": 3,
  "theme": "dark",
  "notifications": {
    "discord": null,
    "slack": null,
    "email": null
  }
}
```

## Building Windows EXE

```bash
build.bat
```

Output files in `dist/`:
- `GitHubDownloader-GUI.exe` (45.7 MB) — Full desktop application
- `GitHubDownloader-CLI.exe` (18.4 MB) — Command-line tool

## Requirements

- Python 3.11+
- PyQt6 (for GUI)
- requests
- PyGithub
- GitPython
- cryptography

## Project Structure

```
github-downloader-new/
├── main.py                    # Entry point (GUI + CLI)
├── cli_main.py                # CLI-only entry point
├── config.json                # Configuration
├── github_downloader/         # Source code
│   ├── user_auth.py           # User accounts (PBKDF2-SHA256)
│   ├── github_api.py          # GitHub API client (Fernet encryption)
│   ├── downloader.py           # Download engine (540 lines)
│   ├── gui_enhanced.py        # PyQt6 GUI (52 KB)
│   ├── gui.py                 # Base GUI (44 KB)
│   ├── enhancements.py        # Feature enhancements (344 lines)
│   ├── incremental_sync.py    # Sync engine (24.7 KB)
│   ├── webhooks.py            # Discord/Slack/Email (20.1 KB)
│   └── gui/
│       ├── cli.py             # CLI command handler
│       ├── dialogs.py         # GUI dialogs
│       ├── managers.py        # GUI state management
│       └── threads.py         # Background workers
├── tests/                     # Unit tests
├── assets/                    # Brand assets
├── docs/                      # Launch materials
├── dist/                      # Built EXEs
├── CHANGELOG.md               # Version history
├── LICENSE                    # MIT license
├── README.md                  # This file
├── DEVELOPER_DOCS.md          # Developer guide
├── AUTHENTICATION.md          # Auth guide
└── requirements.txt           # Dependencies
```

## Tests

```bash
python run_tests.py
```

All 13 unit tests pass. Covers:
- URL parsing
- Download task creation
- API client
- User authentication
- Configuration loading

## Security

- GitHub tokens stored with Fernet symmetric encryption
- Passwords hashed with PBKDF2-HMAC-SHA256 (100K iterations)
- No data sent to third parties
- Open source and auditable

## License

MIT

## Support

Email: ashlee69r@gmail.com
