# Product Requirements Document

## GitHub Repo Downloader v2.6.0

**Date:** 2026-04-09  
**Status:** Active  
**Author:** Development Team  

---

## 1. Overview

GitHub Repo Downloader is a Windows desktop application that provides a GUI for cloning, updating, and managing GitHub repositories. It supports multiple GitHub accounts, OAuth Device Flow authentication, bulk operations, and includes a Matrix-themed visual effect.

## 2. Problem Statement

Users who manage many GitHub repositories need a desktop tool that:
- Downloads all their repos (including private ones) in bulk
- Downloads repos they've starred, with topic metadata visible
- Manages multiple GitHub accounts and tokens
- Respects GitHub's API rate limits and policies
- Works reliably as a standalone Windows EXE without requiring Python installation

## 3. Target Users

- **Developers** who clone many repos across multiple GitHub accounts
- **Open-source contributors** who need to back up their starred repos
- **Teams** managing private repos across organizational accounts
- **Anyone** who needs offline copies of GitHub repositories

## 4. Functional Requirements

### 4.1 Core Download Features

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Clone a single repo by URL or `owner/repo` format | Must |
| FR-02 | Clone with branch/tag selection | Must |
| FR-03 | Shallow clone support (`--depth 1`) | Must |
| FR-04 | Fallback to ZIP download when git is unavailable | Must |
| FR-05 | Drag-and-drop repo URL from browser | Should |
| FR-06 | Download speed limiting (KB/s, 0=unlimited) | Must |
| FR-07 | Concurrent download queue with configurable max (1-5) | Must |
| FR-08 | Progress bar with percentage and status messages | Must |

### 4.2 Bulk Operations

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-09 | "Download All My Repos" — clone all repos owned by the authenticated user (public + private) | Must |
| FR-10 | "Download Starred Repos" — clone all repos the user has starred | Must |
| FR-11 | Display star count, description, language, license, and topics for repos | Should |
| FR-12 | Auto-switch accounts when rate-limited during bulk ops | Must |

### 4.3 Account Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-13 | Add accounts via Personal Access Token (PAT) | Must |
| FR-14 | Add accounts via OAuth Device Flow | Must |
| FR-15 | Validate tokens asynchronously before saving | Must |
| FR-16 | Switch between accounts from a dropdown | Must |
| FR-17 | Delete accounts | Should |
| FR-18 | Display per-account rate limit status (remaining/reset time) | Must |
| FR-19 | Persist accounts to `%APPDATA%/GitHubDownloader/accounts.json` | Must |

### 4.4 Git Operations

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-20 | Update existing repos via `git pull` | Must |
| FR-21 | Push changes — stage, commit, push with commit message | Must |
| FR-22 | Push with file selection (stage specific files or all) | Should |
| FR-23 | Authenticate git operations using stored tokens | Must |

### 4.5 Search & Discovery

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-24 | Search GitHub repos by keyword | Must |
| FR-25 | Display search results in a table with stars, language, description | Must |
| FR-26 | Display repo topics (tags) in search results and info panel | Must |
| FR-27 | Preview repo info before downloading (stars, desc, lang, license, topics) | Must |

### 4.6 UI & Appearance

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-28 | Tabbed interface (Download, Push, Search, Accounts, Settings) | Must |
| FR-29 | Dark/Light mode toggle | Must |
| FR-30 | Matrix rain background animation (toggleable) | Should |
| FR-31 | System tray icon with minimize-to-tray | Must |
| FR-32 | Status log with timestamps | Must |
| FR-33 | Keyboard shortcuts (Ctrl+N, Ctrl+F, Ctrl+S, Ctrl+Q) | Should |
| FR-34 | Drag-and-drop support | Should |

### 4.7 GitHub API Compliance

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-35 | User-Agent header in all API requests | Must |
| FR-36 | API versioning header (`2022-11-28`) | Must |
| FR-37 | Respect `X-RateLimit-Remaining` and `Retry-After` headers | Must |
| FR-38 | Token scope limited to `repo` and `read:user` | Must |
| FR-39 | Conditional requests with `If-Modified-Since` / `ETag` | Should |

### 4.8 Settings & Persistence

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-40 | Save/load settings from `%APPDATA%/GitHubDownloader/settings.json` | Must |
| FR-41 | Persist: dark mode, download dir, max concurrent, auto-switch, matrix enabled, speed limit | Must |
| FR-42 | Auto-load settings on startup | Must |

## 5. Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-01 | Application must work as a standalone Windows EXE (PyInstaller) | Must |
| NFR-02 | No dependency on sqlite3 or cryptography packages (Python 3.13 compat) | Must |
| NFR-03 | Crash logging to `%APPDATA%/GitHubDownloader/crash.log` with error dialog | Must |
| NFR-04 | All network operations on background threads (no UI freeze) | Must |
| NFR-05 | Single-file architecture to avoid PyInstaller import failures | Must |
| NFR-06 | Graceful degradation when `requests` library is unavailable (git-only mode) | Should |

## 6. Technical Architecture

- **Language:** Python 3.13
- **GUI Framework:** PyQt6
- **Packaging:** PyInstaller (single-file EXE via `.spec`)
- **Network:** `requests` for GitHub API; `subprocess` for git operations
- **Storage:** JSON files in `%APPDATA%/GitHubDownloader/`
- **Auth:** PAT + OAuth Device Flow (no client secret required)
- **Threading:** QThread for all network and git operations

## 7. Out of Scope

The following features were considered but are **not** in the current release:

- Repo diff view / compare local vs remote
- Commit history browser
- GitHub notifications tab
- Gist support
- Git submodule recursion (`--recurse-submodules`)
- Archive/backup export of all repos
- Scheduled automatic updates
- PR checkout by number
- File browser via API before cloning
- HTTP/SOCKS proxy configuration
- Upload (push) speed limiting (git push is a subprocess — throttling not feasible)

## 8. Release Criteria

- [ ] All Must requirements implemented and tested
- [ ] EXE builds successfully on Windows with Python 3.13
- [ ] No sqlite3 or cryptography dependency errors
- [ ] Matrix background renders visibly in both dark and light modes
- [ ] Speed limiter functions correctly (0 = unlimited, N KB/s = throttled)
- [ ] OAuth Device Flow completes successfully
- [ ] Crash log written on unexpected errors
- [ ] Settings persist across restarts