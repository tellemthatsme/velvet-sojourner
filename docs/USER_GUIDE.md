# User Guide

## GitHub Repo Downloader v2.6.0

A Windows desktop application for cloning, updating, and managing GitHub repositories with support for multiple accounts, bulk operations, and a Matrix-themed interface.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Quick Start](#2-quick-start)
3. [Account Management](#3-account-management)
4. [Downloading Repositories](#4-downloading-repositories)
5. [Bulk Operations](#5-bulk-operations)
6. [Updating Repositories](#6-updating-repositories)
7. [Pushing Changes](#7-pushing-changes)
8. [Searching Repositories](#8-searching-repositories)
9. [Settings](#9-settings)
10. [Keyboard Shortcuts](#10-keyboard-shortcuts)
11. [System Tray](#11-system-tray)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Installation

### 1.1 Download the EXE

Download `GitHubDownloader.exe` from the `dist/` folder or release page.

### 1.2 Run the Application

Double-click `GitHubDownloader.exe`. No installation required — it's a standalone executable.

### 1.3 Requirements

- **Windows 10 or 11**
- **Git** installed and in PATH (for git clone/pull/push operations)
- **Internet connection**

> **Note:** If Git is not installed, the app will fall back to downloading repos as ZIP archives via the GitHub API.

---

## 2. Quick Start

### 2.1 Add Your GitHub Account

1. Click **+ Add Account**
2. Choose **PAT (Personal Access Token)** or **OAuth Device Flow**
3. Enter your credentials and click **Add & Validate**

### 2.2 Download a Repository

1. Enter a repo URL or `owner/repo` (e.g., `octocat/Hello-World`)
2. Optionally select a **Branch** and enable **Shallow Clone**
3. Click **Download**

### 2.3 Download All Your Repositories

1. Select your account from the dropdown
2. Click **Download All My Repos**
3. All your public and private repositories will be queued and downloaded automatically

---

## 3. Account Management

### 3.1 Adding an Account — PAT

1. Click **+ Add Account**
2. Select the **PAT** tab
3. Enter a label (e.g., "Work Account")
4. Paste your GitHub Personal Access Token
5. Click **Add & Validate**

> **How to get a PAT:**
> 1. Go to GitHub.com → Settings → Developer settings
> 2. Personal access tokens → Fine-grained tokens (or Tokens classic)
> 3. Generate new token with `repo` and `read:user` scopes

### 3.2 Adding an Account — OAuth Device Flow

1. Click **+ Add Account**
2. Select the **OAuth** tab
3. Enter your GitHub App Client ID
4. Click **Start OAuth Flow**
5. Copy the code from the browser
6. Paste it into the app
7. Click **Verify & Add**

> **Note:** Register your GitHub App at `https://github.com/settings/developers` and use your Client ID. The OAuth Device Flow doesn't require a client secret.

### 3.3 Switching Accounts

Use the **Account** dropdown at the top of the Download tab. The active account is used for all operations.

### 3.4 Deleting an Account

1. Go to the **Accounts** tab
2. Select the account to remove
3. Click **Remove Account**

### 3.5 Rate Limit Monitoring

The status bar shows your current rate limit. When GitHub's 5,000 requests/hour limit is low, the app can:
- Display a warning
- Automatically switch to another account if configured

---

## 4. Downloading Repositories

### 4.1 Single Repository Download

1. Enter the repository URL or `owner/repo` format
2. Optionally specify a **Branch** to download
3. Optionally enable **Shallow Clone (--depth 1)** for faster, smaller downloads
4. Click **Download**

### 4.2 Branch Selection

Leave the Branch field empty to download the default branch. Enter a branch name (e.g., `develop`, `v2.0`) to download a specific branch or tag.

### 4.3 Shallow Clone

Enable **Shallow Clone (--depth 1)** to download only the latest commit. This is much faster for large repos but loses full git history.

### 4.4 Drag and Drop

Drag a repository URL from your browser and drop it onto the main window — the URL will be automatically filled into the repo field.

### 4.5 Changing Download Location

1. Click **Browse...** next to the Save to field
2. Select your preferred download folder
3. The default is `~/Downloads/GitHubRepos`

---

## 5. Bulk Operations

### 5.1 Download All My Repositories

Click **Download All My Repos** to download every repository owned by your account (both public and private). The app will:

- Queue all repos
- Respect the **Max Concurrent Downloads** setting
- Auto-switch accounts if **Auto-switch accounts when rate limited** is enabled

### 5.2 Download Starred Repositories

Click **Download Starred Repos** to download all repositories you've starred on GitHub.

### 5.3 Concurrent Downloads

In **Settings → Rate Limit Settings**, adjust **Max Concurrent Downloads** (1-5). Higher values download faster but consume more API calls.

### 5.4 Speed Limiting

In **Settings → Speed Limiting**, set a **Download Speed Limit** in KB/s:
- `0` = unlimited (default)
- `100` = 100 KB/s
- `500` = 500 KB/s

> **Note:** Speed limiting only applies when the app downloads via ZIP (fallback mode). Git clone operations cannot be throttled as they use the `git` subprocess.

---

## 6. Updating Repositories

If you've already downloaded a repository, you can update it with the latest changes:

1. Enter the same repo URL or `owner/repo` you downloaded
2. Click **Update** (or use the **↻ Update** button)
3. The app detects the existing `.git` folder and runs `git pull`

> The Update button only works on repos previously downloaded with this app.

---

## 7. Pushing Changes

### 7.1 Push Tab

Go to the **Push** tab. This lets you stage, commit, and push changes to your repositories.

### 7.2 Stage All Changes

1. Navigate to the repository directory on your local machine
2. Enter a **Commit Message** describing your changes
3. Click **Commit & Push**
4. All changed files will be staged, committed, and pushed

### 7.3 Push Specific Files

1. Click **Select Files to Stage**
2. Check the files you want to commit
3. Enter a **Commit Message**
4. Click **Commit & Push**

> **Note:** Git operations authenticate using the stored GitHub token. Make sure the account has `repo` scope to push.

---

## 8. Searching Repositories

### 8.1 Search by Keyword

1. Go to the **Search** tab
2. Enter a search term (e.g., `machine learning`)
3. Click **Search**
4. Results are shown in a table with:
   - Repository name
   - Star count
   - Primary language
   - Description

### 8.2 Topic Tags

Repositories with topics will display their topics as tags below the description. Topic tags are pulled directly from GitHub's API.

### 8.3 Preview Before Downloading

When you select a repo from search results or enter a URL manually, the **info panel** shows:
- Star count
- Description
- Primary language
- License
- Topic tags

---

## 9. Settings

### 9.1 Appearance

**Toggle Dark/Light Mode** — Switch between dark and light themes.

**Matrix Background Effect** — Enable or disable the Matrix rain animation. The matrix animates on top of the UI and is click-through (doesn't interfere with controls).

### 9.2 Rate Limit Settings

- **Max Concurrent Downloads** — How many downloads run simultaneously (1-5)
- **Auto-switch accounts when rate limited** — Automatically switches to a non-rate-limited account

### 9.3 Speed Limiting

- **Download Speed Limit** — Cap download speed in KB/s. Set to 0 for unlimited.

### 9.4 Saving Settings

Click **Save Settings** to persist all settings to `%APPDATA%/GitHubDownloader/settings.json`. Settings are also auto-loaded on startup.

---

## 10. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New download (clear URL field) |
| `Ctrl+F` | Focus search field |
| `Ctrl+S` | Save settings |
| `Ctrl+Q` | Quit application |

---

## 11. System Tray

### 11.1 Minimize to Tray

Close the main window to minimize to the system tray. The app keeps running in the background.

### 11.2 Tray Menu

Right-click the tray icon to access:
- **Show Window** — Restore the main window
- **Check Rate Limits** — View current API rate limit status
- **Quit** — Fully exit the application

### 11.3 Notifications

When you minimize to tray, a Windows notification confirms the app is running in the background.

---

## 12. Troubleshooting

### The app crashes immediately

Check `%APPDATA%/GitHubDownloader/crash.log` for the error details. Common causes:
- Missing Visual C++ Redistributable
- Display issues on multi-monitor setups

### Matrix background not visible

- Make sure **Matrix Background Effect** is checked in Settings
- Try toggling **Dark/Light Mode** — the matrix is more visible in dark mode
- If still not visible, your graphics driver may not support the widget overlay

### Rate limit reached

- Wait for the reset time shown in the status bar
- Add another GitHub account and enable **Auto-switch accounts**
- Reduce **Max Concurrent Downloads** to use fewer API calls

### "git not found" error

Install Git for Windows from `https://git-scm.com`. Make sure it's in your system PATH. Without git, the app falls back to ZIP downloads.

### OAuth Device Flow fails

- Ensure the Client ID is valid
- Check your internet connection
- Try using a PAT instead (more reliable)

### Downloads fail silently

Check the status log at the bottom of the window. Each download entry shows success/failure status with error details.

### Account not persisting after restart

The accounts file is stored at `%APPDATA%/GitHubDownloader/accounts.json`. If the app crashes during save, the file may be corrupted. Try deleting `accounts.json` and re-adding your accounts.

---

## File Locations

| File | Location |
|------|----------|
| Settings | `%APPDATA%/GitHubDownloader/settings.json` |
| Accounts | `%APPDATA%/GitHubDownloader/accounts.json` |
| Crash Log | `%APPDATA%/GitHubDownloader/crash.log` |
| Downloads | `~/Downloads/GitHubRepos/` (default) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.5.0 | 2026-04-09 | Fixed Matrix background, added speed limiter, updated docs |
| 2.4.0 | 2026-04-08 | Self-contained rewrite, fixed crashes, PyQt6 fixes |
| 2.2.0 | Earlier | Initial enhanced release with multi-account support |