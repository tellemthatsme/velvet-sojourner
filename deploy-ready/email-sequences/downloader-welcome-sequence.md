# GitHub Downloader — Welcome Email Sequence

## Email 1 of 3 — Welcome + Setup
**Send:** Day 0 (immediately after purchase)

**Subject:** Your GitHub Downloader is ready — download repos in 2 clicks

**Preview:** GUI quick start + CLI reference card included

---

Thanks for your purchase!

**GitHub Downloader** is ready to install. Here's everything you need to get started.

### Download & Install

**Download the installer:**
[Download GitHub Downloader →](https://gumroad.com/l/github-downloader/your-download-link)

*You can also access this anytime from your Gumroad library.*

### GUI Mode — First Repo Download

1. Launch the app
2. Paste a GitHub repo URL (e.g., `https://github.com/user/repo`)
3. Choose a download destination
4. Click **Download**

That's it. Your repo — including all files, commit history (if selected), and release assets — will be saved locally.

### CLI Mode — Quick Reference

```bash
# Download a single repo
github-downloader download --url https://github.com/user/repo

# Download with specific branch
github-downloader download --url https://github.com/user/repo --branch main

# List available repos in your account
github-downloader list

# Show help
github-downloader --help
```

> **Tip:** The CLI is fully documented. Run `github-downloader --help` anytime.

---

Happy downloading,

**The Downloader Team**

---

[Launch GitHub Downloader →](https://gumroad.com/l/github-downloader/your-download-link)

---

## Email 2 of 3 — Advanced Usage
**Send:** Day 3

**Subject:** Automate your downloads — CLI tips & batch mode

**Preview:** Cron jobs, CI/CD pipelines, and batch download 50 repos at once

---

Hey,

Ready to go beyond single downloads? Here's how to automate everything.

### CLI Automation

**Cron job (macOS/Linux):** Schedule weekly backups of your team's repos.

```bash
# Every Sunday at 2 AM — backup org repos
0 2 * * 0 /usr/local/bin/github-downloader batch --org your-org --output ~/backups
```

**CI/CD pipeline (GitHub Actions):** Download dependencies before builds.

```yaml
- name: Download dependency repos
  run: |
    github-downloader batch \
      --urls deps.txt \
      --output ./vendor
```

### Batch Downloads

Download multiple repos at once:

```bash
# Download all repos from an organization
github-downloader batch --org google --output ./google-repos

# Download from a list file (one URL per line)
github-downloader batch --file repos.txt --output ./batch

# Download all starred repos
github-downloader batch --starred --output ./starred
```

### Environment Variables

Set these once and skip repeated authentication:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx    # Personal access token
export GITHUB_DOWNLOADER_DIR=~/repos    # Default output directory
export GITHUB_DOWNLOADER_PARALLEL=5     # Concurrent downloads
```

---

Power up,

**The Downloader Team**

---

[View CLI Docs →](https://docs.github-downloader.com/cli)

---

## Email 3 of 3 — Pro Tips + Upgrade
**Send:** Day 7

**Subject:** Power user secrets + a special bundle offer

**Preview:** Save 30% when you bundle GitHub Downloader with AgentForge Index

---

Hi,

You've been using GitHub Downloader for a week. Here are some pro tips — plus an exclusive bundle offer.

### Power User Tips

- **Incremental downloads** — Use `--incremental` to only download changed files since last run
- **Asset extraction** — `github-downloader download --url ... --include-assets` grabs release binaries, not just source
- **Format filters** — `--include "*.py,*.md"` only downloads matching file types
- **Resume interrupted downloads** — Add `--resume` to pick up where you left off

### Bundle Offer: Complete Your Toolkit

You bought **GitHub Downloader** — now pair it with **AgentForge Index** to find the best repos before you download them.

| Product | What It Does | Standalone Price |
|---|---|---|
| GitHub Downloader | Download any repo locally | $29 |
| AgentForge Index | Curated directory of 2,000+ agent repos | $49 |
| **Bundle** | Both products | **$55 (save 30%)** |

**Use code `BUNDLE30` at checkout.**

[Get the Bundle →](https://checkout.com/bundle/downloader-forge)

---

**The Downloader Team**

---

[Claim Bundle Offer →](https://checkout.com/bundle/downloader-forge)
