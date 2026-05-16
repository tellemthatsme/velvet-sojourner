# GitHub Downloader v2.1

Windows EXE for downloading, verifying, and managing GitHub repositories.

## Files

| File | Size | Type |
|------|------|------|
| `GitHubDownloader-CLI.exe` | 19 MB | Headless (runs in terminal) |
| `GitHubDownloader-GUI.exe` | 48 MB | Desktop GUI (includes PyQt6) |

Both are standalone — no Python or dependencies needed.

## CLI Commands

```bash
# Download a single repo
GitHubDownloader-CLI.exe download --url owner/repo --output ./downloads

# Batch download from file (one URL per line)
GitHubDownloader-CLI.exe batch --file repos.txt --output ./downloads --concurrent 3

# Verify downloaded repos
GitHubDownloader-CLI.exe verify --path ./repos

# Verify a single repo
GitHubDownloader-CLI.exe verify --path ./repos --repo repo-name

# Export metadata as JSON or CSV
GitHubDownloader-CLI.exe export --path ./repos --format csv --output report.csv

# Health check
GitHubDownloader-CLI.exe health --path ./repos

# Show current config
GitHubDownloader-CLI.exe config --show

# List user's GitHub repos
GitHubDownloader-CLI.exe list --user github_username

# Search GitHub
GitHubDownloader-CLI.exe search --query "agent framework"
```

## GUI Mode

Run without arguments to launch the desktop GUI:

```bash
GitHubDownloader-GUI.exe
```

Features: search repos, queue downloads, view progress, manage tokens.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | Auth for private repos / higher rate limits |
| `GITHUB_DOWNLOAD_DIR` | Default output directory |
| `GITHUB_MAX_CONCURRENT` | Max parallel batch downloads (default: 3) |
| `GITHUB_DOWNLOAD_METHOD` | `git`, `zip`, or `tar` (default: `git`) |

## Download Methods

| Method | Speed | Metadata | Needs Git? |
|--------|-------|----------|------------|
| `git` | Medium | Full history + branches | Yes (included in EXE) |
| `zip` | Fastest | No git history | No |
| `tar` | Fast | No git history | No |
