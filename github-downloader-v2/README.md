# GitHub Repo Downloader v2.0

A Windows application to download and clone GitHub repositories with user authentication.

## Quick Start

### GUI Mode
```bash
python src/main.py
```

### CLI Mode
```bash
# Download a repository
python src/main.py --cli download --url owner/repo --output ~/downloads

# List user repositories
python src/main.py --cli list --user octocat

# Search repositories
python src/main.py --cli search -q "python web framework"
```

### Build Windows EXE
```bash
build.bat
```
The executable will be at `dist/GitHubDownloader.exe`

---

## Features

- User account system with encrypted credentials
- GitHub authentication (PAT/OAuth)
- Single and batch downloads
- Download ALL repos from an account
- Dark/Light theme with one-click toggle
- CLI mode for automation
- Repo sync & scheduling
- Bookmarks
- Rate limit compliance

---

## Documentation

- **[README.md](README.md)** - User guide and features
- **[DEVELOPER_DOCS.md](DEVELOPER_DOCS.md)** - Architecture, API reference, and extension guide

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New download |
| Ctrl+B | Batch download |
| Ctrl+D | Download current |
| Ctrl+L | Focus path field |
| Ctrl+R | Load repos |
| Ctrl+S | Settings |
| Ctrl+T | Toggle theme |
| Ctrl+Q | Exit |

---

## Requirements

- Windows 10/11
- Python 3.10+
- Git (for git clone)

---

## License

MIT
