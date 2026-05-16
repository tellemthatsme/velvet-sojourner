# Validation Document

## GitHub Repo Downloader v2.6.0

**Date:** 2026-04-09  
**Validator:** Development Team  
**Status:** Complete  

---

## 1. Validation Overview

This document validates that the GitHub Repo Downloader meets all requirements defined in the PRD and functions correctly as a Windows EXE application.

## 2. Test Environment

| Item | Value |
|------|-------|
| OS | Windows 10/11 |
| Python | 3.13 |
| PyInstaller | Latest (pip install) |
| Dependencies | PyQt6, requests |
| Build Command | `pyinstaller GitHubDownloader.spec` |

## 3. Functional Test Cases

### 3.1 Single Repo Download

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-01 | Clone by URL | Enter `https://github.com/octocat/Hello-World`, click Download | Repo cloned to output dir | [ ] |
| TC-02 | Clone by owner/repo | Enter `octocat/Hello-World`, click Download | Repo cloned, URL auto-expanded | [ ] |
| TC-03 | Clone with branch | Enter repo + branch name, click Download | Repo cloned to specified branch | [ ] |
| TC-04 | Shallow clone | Check "Shallow (--depth 1)", download | Repo cloned with depth 1 | [ ] |
| TC-05 | Fallback to ZIP | Download on machine without git | ZIP downloaded and extracted | [ ] |
| TC-06 | Drag and drop | Drag URL from browser onto window | URL field populated | [ ] |
| TC-07 | Cancel download | Start download, click cancel | Process killed, "Cancelled" logged | [ ] |

### 3.2 Bulk Operations

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-08 | Download All My Repos | Select account, click "Download All My Repos" | All user repos (public+private) queued and downloaded | [ ] |
| TC-09 | Download Starred Repos | Select account, click "Download Starred Repos" | All starred repos downloaded | [ ] |
| TC-10 | Bulk with rate limit | Use token with low rate limit, bulk download | Auto-switches accounts or pauses when limited | [ ] |

### 3.3 Account Management

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-11 | Add PAT account | Click "+ Add Account", enter token, validate | Account added with username shown | [ ] |
| TC-12 | Add OAuth account | Click "+ Add Account", switch to OAuth tab, complete flow | Account added via device flow | [ ] |
| TC-13 | Delete account | Select account, click remove | Account removed from list and storage | [ ] |
| TC-14 | Switch account | Select different account from dropdown | Active account changes, rate limit info updates | [ ] |
| TC-15 | Invalid token | Enter invalid token, validate | Error message shown, account not saved | [ ] |

### 3.4 Git Operations

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-16 | Update repo | Enter path to existing repo, click Update | `git pull` executed, status shown | [ ] |
| TC-17 | Push changes | Go to Push tab, enter commit msg, push | Files staged, committed, pushed | [ ] |
| TC-18 | Push specific files | Select files in push tab, commit, push | Only selected files staged and pushed | [ ] |

### 3.5 Search & Discovery

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-19 | Search repos | Enter keyword, click Search | Results displayed in table | [ ] |
| TC-20 | Display topics | Search and select a repo with topics | Topics shown in info panel | [ ] |
| TC-21 | Repo info preview | Enter repo, view info panel | Stars, description, language, license, topics shown | [ ] |

### 3.6 UI & Appearance

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-22 | Dark mode | Click "Toggle Dark/Light Mode" | Dark theme applied, matrix visible at 0.4 alpha | [ ] |
| TC-23 | Light mode | Click "Toggle Dark/Light Mode" | Light theme applied, matrix visible at 0.15 alpha | [ ] |
| TC-24 | Matrix toggle | Uncheck "Matrix Background Effect" | Matrix hidden, timer stopped | [ ] |
| TC-25 | Matrix re-enable | Check "Matrix Background Effect" | Matrix visible, timer restarted | [ ] |
| TC-26 | System tray minimize | Close window | App minimized to tray, notification shown | [ ] |
| TC-27 | System tray quit | Right-click tray icon, Quit | App fully exits | [ ] |
| TC-28 | Keyboard shortcuts | Press Ctrl+N, Ctrl+F, Ctrl+S | Correct actions triggered | [ ] |

### 3.7 Speed Limiting

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-29 | Unlimited speed | Set speed limit to 0, download ZIP | Download runs at full speed | [ ] |
| TC-30 | Throttled speed | Set speed limit to 100 KB/s, download ZIP | Download throttled to ~100 KB/s | [ ] |
| TC-31 | Speed label update | Change speed limit value | Label updates to reflect current setting | [ ] |

### 3.8 Settings Persistence

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| TC-32 | Save settings | Click "Save Settings" | Settings written to `%APPDATA%/GitHubDownloader/settings.json` | [ ] |
| TC-33 | Load on startup | Close and reopen app | All settings restored (theme, dir, concurrency, speed, matrix) | [ ] |
| TC-34 | Account persistence | Add account, restart app | Account still present in dropdown | [ ] |

## 4. Non-Functional Validation

### 4.1 EXE Build

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| NF-01 | Build EXE | Run `build.bat` | EXE produced in `dist/` without errors | [ ] |
| NF-02 | Run EXE | Double-click `dist/GitHubDownloader.exe` | App launches, no crash | [ ] |
| NF-03 | No sqlite3 crash | Run EXE on fresh machine | No `sqlite3` import error | [ ] |
| NF-04 | Crash log | Force crash | `crash.log` written to `%APPDATA%/GitHubDownloader/` | [ ] |
| NF-05 | Icon display | Check title bar and taskbar | App icon visible | [ ] |

### 4.2 Thread Safety

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| NF-06 | Concurrent downloads | Start 3 downloads simultaneously | All complete without UI freeze | [ ] |
| NF-07 | Token validation async | Add account while search running | No crash, validation completes | [ ] |

### 4.3 GitHub API Compliance

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| NF-08 | User-Agent header | Inspect API request headers | `GitHub-Repo-Downloader/v2.5.0` present | [ ] |
| NF-09 | API versioning | Inspect headers | `X-GitHub-Api-Version: 2022-11-28` present | [ ] |
| NF-10 | Rate limit handling | Exhaust rate limit | App pauses or switches accounts, respects `Retry-After` | [ ] |
| NF-11 | Token scope | Check PAT scope | Only `repo` and `read:user` requested | [ ] |

## 5. Bug Fix Validation

### 5.1 Matrix Background (Fixed in v2.5.0)

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| BF-01 | Matrix visible dark | Enable dark mode | Green Matrix characters visible over content | [ ] |
| BF-02 | Matrix visible light | Enable light mode | Green Matrix characters visible (subtle) | [ ] |
| BF-03 | Matrix click-through | Click UI elements with matrix enabled | All clicks pass through to underlying widgets | [ ] |
| BF-04 | Matrix key `"chars"` | Verify dict keys | No `" chars"` key (space prefix removed) | [ ] |

### 5.2 Speed Limiter (New in v2.5.0)

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| BF-05 | Speed limiter UI | Open Settings tab | "Speed Limiting" group with KB/s spin box visible | [ ] |
| BF-06 | Speed label | Change spin box value | Label updates dynamically | [ ] |
| BF-07 | Speed persistence | Set limit, save, restart | Limit value restored | [ ] |

## 6. Regression Tests

| TC | Test Case | Steps | Expected Result | Pass? |
|----|-----------|-------|-----------------|-------|
| RT-01 | Build after refactor | Build EXE with v2.5.0 source | Build succeeds | [ ] |
| RT-02 | All tabs load | Click each tab | Download, Push, Search, Accounts, Settings all render | [ ] |
| RT-03 | OAuth tab | Open Add Account dialog | PAT and OAuth tabs both present | [ ] |
| RT-04 | Status log | Perform actions | Timestamps in `[HH:MM:SS]` format | [ ] |

## 7. Validation Summary

| Category | Total | Passed | Failed | Blocked |
|----------|-------|--------|--------|---------|
| Functional - Download | 7 | - | - | - |
| Functional - Bulk | 3 | - | - | - |
| Functional - Accounts | 5 | - | - | - |
| Functional - Git Ops | 3 | - | - | - |
| Functional - Search | 3 | - | - | - |
| Functional - UI | 7 | - | - | - |
| Functional - Speed | 3 | - | - | - |
| Functional - Settings | 3 | - | - | - |
| Non-Functional | 5 | - | - | - |
| Thread Safety | 2 | - | - | - |
| API Compliance | 4 | - | - | - |
| Bug Fixes | 7 | - | - | - |
| Regression | 4 | - | - | - |
| **Total** | **56** | **0** | **0** | **0** |

**Overall Verdict:** Pending manual testing