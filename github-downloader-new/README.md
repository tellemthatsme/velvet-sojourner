# GitHub Repo Downloader

A powerful desktop application for downloading GitHub repositories with support for private repos, batch downloads, scheduling, and more.

## Features

- ✅ **Private Repository Support** - Download private repos with authentication
- ✅ **Multiple Authentication Methods** - PAT, OAuth, GitHub CLI, SSH
- ✅ **Dark/Light Theme** - Beautiful dark mode by default
- ✅ **CLI Mode** - Command line interface for automation
- ✅ **Batch Downloads** - Download multiple repos at once
- ✅ **Download ALL Repos** - One-click download all repos from a user
- ✅ **Selective Download** - Choose specific files/folders
- ✅ **Bookmarks & History** - Save and revisit repositories
- ✅ **Incremental Sync** - Only download changed files
- ✅ **Webhook Integration** - Discord/Slack/Email notifications
- ✅ **Rate Limit Compliance** - 80% safety margin to avoid throttling

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

### Option 1: Personal Access Token (PAT) - Recommended

1. Create a token: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Select scope: `repo` (for private repos)
3. Use in app:
   - **GUI:** Account → GitHub Authentication → Enter token
   - **CLI:** `python main.py --cli download --url owner/repo -t ghp_your_token`

### Option 2: OAuth2

1. Create OAuth App: GitHub → Settings → Developer settings → OAuth Apps
2. Set callback: `http://localhost:8080/callback`
3. Enter Client ID/Secret in app

### Option 3: GitHub CLI

```bash
gh auth login
```
App detects GitHub CLI session automatically.

### Option 4: SSH Keys

For git clone, use SSH keys:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add public key to GitHub
```

## Rate Limits

| Method | Limit |
|--------|-------|
| Unauthenticated | 60/hour |
| Authenticated (PAT/OAuth) | 5,000/hour |
| App uses (safety margin) | 4,000/hour |

The app automatically stays within rate limits.

## Download Methods

1. **Git Clone** - Full git repository with history
2. **Download ZIP** - Single ZIP file
3. **Download TAR.gz** - Single TAR file

## Configuration

Edit `config.json` to customize:
- Rate limit safety margin
- Default download location
- Max concurrent downloads
- Notification settings
- Theme preferences

## Building Windows EXE

```bash
build.bat
```

Output: `dist/GitHubDownloader.exe`

## Requirements

- Python 3.11+
- PyQt6
- requests
- PyGithub
- GitPython
- cryptography

## Files

```
github-downloader-new/
├── main.py              # Entry point
├── config.json          # Configuration
├── AUTHENTICATION.md    # Auth guide
├── README.md            # This file
├── requirements.txt     # Dependencies
├── github_downloader/   # Source code
│   ├── user_auth.py     # User accounts
│   ├── github_api.py    # GitHub API
│   ├── downloader.py    # Downloads
│   ├── gui_enhanced.py  # GUI
│   ├── webhooks.py      # Webhooks
│   └── incremental_sync.py  # Sync
└── tests/               # Unit tests
```

## Support

- All 13 unit tests pass
- GitHub Terms compliant
- No bulk scraping
- Respects robots.txt
