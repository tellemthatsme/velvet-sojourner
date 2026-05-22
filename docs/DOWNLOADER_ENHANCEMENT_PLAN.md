# GITHUB DOWNLOADER — ENHANCEMENT PLAN

**Goal:** Launch-ready in 7 days  
**Current quality:** 7.5/10 → **Target:** 9/10

---

## DAY 1: CONSOLIDATION (4 hours)

### Step 1: Identify Canonical Version
- **Canonical:** `github-downloader-new/` (most complete, has GUI+CLI+EXEs)
- **Archive:** `src/`, `github-downloader-v2/`, `github-repo-download/`

### Step 2: Archive Duplicates
```powershell
# Move duplicates to archive folder
New-Item -ItemType Directory -Path "C:\temp\velvet-sojourner\archive\github-downloader-duplicates"
Move-Item "C:\temp\velvet-sojourner\src" "C:\temp\velvet-sojourner\archive\github-downloader-duplicates\src"
Move-Item "C:\temp\velvet-sojourner\github-downloader-v2" "C:\temp\velvet-sojourner\archive\github-downloader-duplicates\github-downloader-v2"
Move-Item "C:\temp\velvet-sojourner\github-repo-download" "C:\temp\velvet-sojourner\archive\github-downloader-duplicates\github-repo-download"
```

### Step 3: Verify Canonical Structure
```
github-downloader-new/
├── main.py                    # Entry point (GUI)
├── cli_main.py                # Entry point (CLI)
├── downloader.py              # Core download logic
├── github_api.py              # GitHub API client
├── user_auth.py               # Authentication
├── gui_enhanced.py            # Enhanced GUI
├── gui.py                     # Base GUI
├── enhancements.py            # Feature enhancements
├── incremental_sync.py        # Sync logic
├── webhooks.py                # Webhook notifications
├── config.json                # Configuration
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── DEVELOPER_DOCS.md          # Developer guide
├── AUTHENTICATION.md          # Auth guide
├── build_exe.py               # Build script
├── build_gui_exe.py           # GUI build
├── build_cli_exe.py           # CLI build
├── build_clean_exe.py         # Clean build
├── build.bat                  # Batch build
├── GitHubDownloader.spec      # PyInstaller spec
├── GitHubDownloader-GUI.spec  # GUI spec
├── GitHubDownloader-CLI.spec  # CLI spec
├── run_tests.py               # Test runner
├── tests/                     # Test suite
├── dist/                      # Built EXEs
└── logs/                      # Log files
```

---

## DAY 2: BRANDING (3 hours)

### Step 1: Create App Icon
1. Use favicon-gen skill or create 128x128 PNG
2. Convert to .ico format
3. Save as `github-downloader-new/assets/icon.ico`

### Step 2: Update Spec Files
```python
# In all .spec files, change:
icon=None
# To:
icon='assets/icon.ico'

# Add version info:
version='1.0.0',
company_name='AgentForge',
product_name='GitHub Downloader',
```

### Step 3: Rebuild EXEs
```powershell
cd C:\temp\velvet-sojourner\github-downloader-new
python build_gui_exe.py
python build_cli_exe.py
```

### Step 4: Verify EXEs
```powershell
# Check file sizes
Get-ChildItem "dist\*.exe" | Select-Object Name, Length

# Test CLI
.\dist\GitHubDownloader-CLI.exe --help
```

---

## DAY 3: DOCUMENTATION (4 hours)

### Step 1: Update README.md
Add to existing README:
- [ ] Screenshots (GUI tabs, CLI output)
- [ ] Installation instructions
- [ ] Quick start guide
- [ ] Feature comparison table
- [ ] Pricing tiers
- [ ] Support contact

### Step 2: Create CHANGELOG.md
```markdown
# Changelog

## [1.0.0] - 2026-05-21
### Added
- Full GUI with 7 tabs (Download, Batch, Search, My Repos, Bookmarks, Sync, History)
- CLI with 8 commands (download, batch, verify, export, health, config, list, search)
- 4 authentication methods (PAT, OAuth2, GitHub CLI, SSH)
- 3 download methods (Git Clone, ZIP, TAR)
- Incremental sync for changed files
- Webhook notifications (Discord, Slack, Email)
- Download history tracking (SQLite)
- Bookmarks management
- Dark/Light theme
- Rate limit compliance (80% safety margin)
- Private repository support
- Batch download from file list
- Selective download (files/folders)
```

### Step 3: Add LICENSE
```bash
# Create MIT LICENSE file
echo "MIT License

Copyright (c) 2026 AgentForge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE." > LICENSE
```

### Step 4: Create Demo Video
- Record 3-minute screen capture
- Show: GUI download, batch download, CLI usage
- Save as `docs/github-downloader-demo.mp4`

---

## DAY 4: LANDING PAGE (3 hours)

### Step 1: Create HTML Landing Page
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Downloader — Batch Download Any Repo</title>
    <style>
        /* Dark theme, modern design */
        body { font-family: system-ui; background: #0a0a0a; color: #fff; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        h1 { font-size: 3rem; margin-bottom: 1rem; }
        .subtitle { font-size: 1.25rem; color: #888; margin-bottom: 2rem; }
        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .feature { background: #1a1a1a; padding: 20px; border-radius: 8px; }
        .pricing { display: flex; gap: 20px; margin-top: 40px; }
        .tier { background: #1a1a1a; padding: 30px; border-radius: 8px; flex: 1; }
        .cta { background: #0070f3; color: #fff; padding: 15px 30px; border: none; border-radius: 8px; font-size: 1.1rem; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GitHub Downloader</h1>
        <p class="subtitle">Download any GitHub repo, even private ones, with one click. Batch download 100 repos while you grab coffee.</p>
        
        <div class="features">
            <div class="feature">
                <h3>📦 Batch Download</h3>
                <p>Download hundreds of repos at once from a file list</p>
            </div>
            <div class="feature">
                <h3>🔐 Private Repos</h3>
                <p>Full support for private repos via PAT authentication</p>
            </div>
            <div class="feature">
                <h3>🔄 Incremental Sync</h3>
                <p>Only download changed files — save time and bandwidth</p>
            </div>
            <div class="feature">
                <h3>🌐 Webhooks</h3>
                <p>Get notified on Discord, Slack, or email when downloads complete</p>
            </div>
            <div class="feature">
                <h3>📊 History & Bookmarks</h3>
                <p>Track all downloads and bookmark your favorites</p>
            </div>
            <div class="feature">
                <h3>🖥️ GUI + CLI</h3>
                <p>Beautiful desktop app or powerful command-line interface</p>
            </div>
        </div>

        <div class="pricing">
            <div class="tier">
                <h3>Free</h3>
                <p class="price">$0</p>
                <ul>
                    <li>Public repos only</li>
                    <li>CLI access</li>
                    <li>Unlimited downloads</li>
                </ul>
                <button class="cta">Download CLI</button>
            </div>
            <div class="tier">
                <h3>Pro</h3>
                <p class="price">$19</p>
                <ul>
                    <li>Private repos</li>
                    <li>Full GUI</li>
                    <li>Batch download</li>
                    <li>Incremental sync</li>
                </ul>
                <button class="cta">Buy Pro</button>
            </div>
            <div class="tier">
                <h3>Team</h3>
                <p class="price">$49</p>
                <ul>
                    <li>Everything in Pro</li>
                    <li>Multi-user</li>
                    <li>Shared bookmarks</li>
                    <li>Webhook notifications</li>
                </ul>
                <button class="cta">Buy Team</button>
            </div>
        </div>
    </div>
</body>
</html>
```

### Step 2: Deploy to Vercel
```powershell
cd C:\temp\velvet-sojourner\github-downloader-new
vercel --prod
```

---

## DAY 5: GUMROAD SETUP (2 hours)

### Step 1: Create Gumroad Product
1. Go to gumroad.com → Products → New Product
2. Name: **GitHub Downloader**
3. Type: Digital Product
4. Price: $19 (Pro tier)

### Step 2: Upload Files
- `dist/GitHubDownloader-GUI.exe` (45.7 MB)
- `dist/GitHubDownloader-CLI.exe` (18.4 MB)
- `README.md`
- `CHANGELOG.md`
- `LICENSE`

### Step 3: Write Description
```markdown
# GitHub Downloader

Download any GitHub repository, even private ones, with one click. Batch download 100 repos while you grab coffee.

## Features

- **Full GUI** with 7 tabs: Download, Batch, Search, My Repos, Bookmarks, Sync, History
- **CLI** with 8 commands: download, batch, verify, export, health, config, list, search
- **4 authentication methods**: PAT, OAuth2, GitHub CLI, SSH
- **3 download methods**: Git Clone, ZIP, TAR
- **Incremental sync** — only download changed files
- **Webhook notifications** — Discord, Slack, Email
- **Download history** tracking (SQLite)
- **Bookmarks** management
- **Dark/Light theme**
- **Rate limit compliance** (80% safety margin)
- **Private repository** support

## What's Included

- GitHubDownloader-GUI.exe (45.7 MB) — Full desktop app
- GitHubDownloader-CLI.exe (18.4 MB) — Command-line interface
- README.md — Complete documentation
- CHANGELOG.md — Version history
- LICENSE — MIT license

## System Requirements

- Windows 10/11 (64-bit)
- Git installed (for git clone method)
- GitHub account (for private repos)

## Support

Email: ashlee69r@gmail.com
Documentation: [Link to docs]

## Refund Policy

30-day money-back guarantee. If it doesn't save you time, we'll refund you in full.
```

### Step 4: Add Screenshots
- Upload 3-4 screenshots from `docs/screenshots/`
- Cover image: Best GUI screenshot
- Thumbnail: App icon

### Step 5: Publish
- Set URL slug: `github-downloader`
- Click **Publish**
- **Save your Gumroad URL**

---

## DAY 6-7: LAUNCH (4 hours)

### Step 1: Update All Links
- Replace placeholder URLs with Gumroad URL in:
  - `README.md`
  - Landing page HTML
  - Launch posts

### Step 2: Post on Reddit
- r/Python: Technical deep-dive
- r/github: Tool showcase
- r/devops: Backup/mirror angle
- r/selfhosted: Self-hosted angle

### Step 3: Post Show HN
- Title: `Show HN: GitHub Downloader — Desktop app for batch downloading repos`
- URL: Your Gumroad URL
- First comment: Technical details

### Step 4: Post on Dev.to
- Title: "How I built a GitHub repo downloader with PyQt6"
- Include screenshots, code snippets, lessons learned

### Step 5: Submit to Directories
- alternative.to
- slant.co
- saashub.com
- producthunt.com (schedule for later)

### Step 6: Twitter/X Thread
- 8-tweet thread showing features
- Attach screenshots
- Tag: @github @PyQt @python

---

## POST-LAUNCH ENHANCEMENTS

### Week 2-3: v1.1
- [ ] Add download resume for interrupted transfers
- [ ] Add HTTP/HTTPS proxy configuration
- [ ] Add auto-update checker
- [ ] Build macOS version
- [ ] Build Linux AppImage

### Week 4-6: v1.2
- [ ] Add GitHub Enterprise support
- [ ] Add download scheduling
- [ ] Add repository size estimation
- [ ] Build CI/CD pipeline
- [ ] Publish to Winget, Chocolatey, Scoop

### Week 7-12: v2.0
- [ ] Add plugin system
- [ ] Add repository comparison/diff
- [ ] Add export to Docker image
- [ ] Add team sharing
- [ ] Add telemetry (opt-in)

---

## FILES TO CREATE/UPDATE

| File | Action | Status |
|------|--------|--------|
| `github-downloader-new/README.md` | Update with screenshots | ⏳ |
| `github-downloader-new/CHANGELOG.md` | Create | ⏳ |
| `github-downloader-new/LICENSE` | Create (MIT) | ⏳ |
| `github-downloader-new/assets/icon.ico` | Create | ⏳ |
| `github-downloader-new/docs/landing.html` | Create | ⏳ |
| `github-downloader-new/docs/demo.mp4` | Record | ⏳ |
| `deploy-ready/github-downloader/README.md` | Update | ⏳ |
| `docs/github-downloader-launch-posts.md` | Create | ⏳ |

---

## SUCCESS METRICS

| Metric | 7-Day Target | 30-Day Target |
|--------|--------------|---------------|
| Gumroad views | 500 | 2,000 |
| Downloads | 50 | 200 |
| Sales | 10 | 50 |
| Revenue | $200 | $1,000 |
| HN upvotes | 30+ | 100+ |
| Reddit upvotes | 50+ | 200+ |
| GitHub stars | 20 | 100 |

---

**Start Day 1 now. Complete each step before moving to the next. Track everything.**
