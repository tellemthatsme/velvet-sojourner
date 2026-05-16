# GitHub Downloader v3.3.0 - Enhanced GUI

## Overview

A comprehensive, production-grade GitHub repository downloader with advanced multi-account support, organization repo fetching, and intelligent repo management.

## Features

- ✅ **Multi-Account Support** - Download from multiple GitHub accounts simultaneously
- ✅ **Organization Repo Support** - Automatically fetches repos from all organizations
- ✅ **Private Repo Access** - Downloads private repos with proper token scopes
- ✅ **Fork Support** - Optionally includes forked repos
- ✅ **Rate Limit Management** - Respects GitHub API rate limits (5000/hour)
- ✅ **Token Validation** - Validates tokens before use
- ✅ **OAuth Device Flow** - Secure token acquisition without manual token entry
- ✅ **Smart Filtering** - Filters by owner, visibility, and repository type
- ✅ **Progress Tracking** - Real-time download progress and queue management
- ✅ **Error Recovery** - Handles failures gracefully with detailed logging
- ✅ **Dark/Light Theme** - Customizable UI with theme support
- ✅ **System Tray** - Minimize to tray with notifications

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/GitHubDownloader.git
cd GitHubDownloader

# Install dependencies
uv sync

# Run the app
uv run python -m github_downloader
```

### Build Executable

```bash
# Build Windows exe
uv run pyinstaller GitHubDownloader.spec
```

The executable will be in `dist/GitHubDownloader.exe`

## Usage

### Adding Accounts

1. Go to **Accounts** tab
2. Click **"Add Account"**
3. Choose **OAuth Device Flow** (recommended) or **Personal Access Token**
4. For OAuth: Click "Start OAuth Login" and follow the browser flow
5. For PAT: Enter your token with `repo` scope

### Downloading Repos

**Single Account:**
1. Select the account in the Accounts tab
2. Click **"⬇ Download Selected"**

**All Accounts:**
1. Click **"⬇ Download ALL"** button
2. This downloads from ALL configured accounts

**Organization Repos:**
- The app automatically fetches org repos when you add an account
- Org repos are merged with user repos for complete coverage

### Download Location

Repos are downloaded to: `%APPDATA%\GitHubDownloader\downloads\`

## Configuration

### Token Scopes Required

Your GitHub token needs these scopes:
- `repo` - Access to repositories (public and private)
- `read:org` - Read organization membership (for org repos)
- `user` - Read user profile

### Settings

Settings are stored in: `%APPDATA%\GitHubDownloader\settings.json`

Key settings:
- `download_dir` - Default download location
- `theme` - UI theme (dark/light)
- `max_concurrent` - Maximum parallel downloads
- `auto_start` - Start download on app launch

## Debug & Logs

Debug logs are written to: `%APPDATA%\GitHubDownloader\debug.log`

Enable verbose logging by setting environment variable:
```bash
set GITHUB_DOWNLOADER_DEBUG=1
```

## Troubleshooting

### "Rate limit exceeded"
- Wait until the rate limit resets (shown in status bar)
- Use a token with higher rate limit (GitHub Pro/Organization)

### "Invalid token"
- Ensure your token has the `repo` scope
- Re-authenticate using OAuth Device Flow

### "No repos found"
- Check that the token has `repo` scope
- Verify the account has repositories
- Check if repos are organization-owned (requires `read:org` scope)

### "422 error: visibility and type incompatible"
- This is a GitHub API limitation
- The app uses `type=all` which includes all repo types

## Development

### Project Structure

```
C:\temp\velvet-sojourner\
├── src/
│   └── github_downloader/
│       ├── gui_enhanced_full.py    # Main GUI application
│       └── backup_worker.py        # Backup worker module
├── icons/
│   └── app.ico                     # Application icon
├── GitHubDownloader.spec           # PyInstaller spec
├── dist/
│   └── GitHubDownloader.exe        # Built executable
├── scan_repos.py                   # Repo scanner utility
├── categorize_repos.py             # Repo categorizer
├── REPO_INVENTORY.md               # Complete repo inventory
└── README.md                       # This file
```

### Key Components

**ListReposWorker** - Threaded worker for fetching repos from GitHub API
**DownloadWorker** - Threaded worker for cloning/pulling repos
**RateManager** - Manages API rate limits and account switching
**OAuthDeviceFlowWorker** - Handles OAuth Device Flow authentication

### API Endpoints Used

- `GET /user` - Get authenticated user
- `GET /user/repos` - List user repositories (type=all)
- `GET /users/{username}/repos` - List user repositories
- `GET /orgs/{org}/repos` - List organization repositories
- `GET /user/orgs` - List user organizations

## Monetization Guide

See [REPO_INVENTORY.md](REPO_INVENTORY.md) for detailed monetization recommendations for your repositories.

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please open an issue on GitHub.
