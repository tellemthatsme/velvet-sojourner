# COMPREHENSIVE TEST PLAN
# GitHub Downloader v3.3.0
# Date: 2026-04-22
# Status: READY FOR EXECUTION

---

## 1. TOKEN SCOPE TESTING

### Test 1.1: Token Validation with Scope Detection
**Objective:** Verify enhanced token validator detects missing scopes
**Prerequisites:** App built and running
**Steps:**
1. Open GitHubDownloader.exe
2. Go to Accounts tab
3. Add account with token that has NO scopes (current state)
4. **Expected:** Error message: "TOKEN SCOPE ERROR: Token has NO scopes!..."
5. Add account with token that has 'repo' scope
6. **Expected:** Success, shows username and repo count

**Pass Criteria:**
- [ ] NO-scope token shows clear error with fix instructions
- [ ] Proper-scope token validates successfully
- [ ] Debug log shows scope details

### Test 1.2: Token Scope Diagnostic Script
**Objective:** Verify standalone diagnostic tool works
**Prerequisites:** Python installed, check_tokens.py exists
**Steps:**
1. Run: `python check_tokens.py`
2. **Expected:** Shows all 5 accounts with NO_SCOPES status
3. Generate new token with 'repo' scope
4. Update accounts.json with new token
5. Re-run script
6. **Expected:** Shows OK status with fetched repo counts

**Pass Criteria:**
- [ ] Detects all 5 accounts automatically
- [ ] Reports NO_SCOPES for invalid tokens
- [ ] Reports OK for valid tokens
- [ ] Generates token_report.json

---

## 2. REPOSITORY DOWNLOAD TESTING

### Test 2.1: Download All Repos (Single Account)
**Objective:** Verify complete repo download for one account
**Prerequisites:** Valid token with 'repo' scope
**Steps:**
1. Add account with valid token
2. Go to Download tab
3. Click "All Accounts" button
4. Wait for completion
5. Check repo count matches GitHub profile

**Expected Results:**
| Account | Expected Min | Status |
|---------|--------------|--------|
| tellemthatsme | 200+ repos | |
| woodsai69rme | 200+ repos | |
| leahmfoots | 30+ repos | |
| acidlink | 30+ repos | |
| Ashlee69r | 30+ repos | |

**Pass Criteria:**
- [ ] Downloaded count >= 90% of expected
- [ ] Both public and private repos included
- [ ] No "rate limit exceeded" errors
- [ ] Progress bar updates correctly

### Test 2.2: Multi-Account Download
**Objective:** Download from all 5 accounts simultaneously
**Steps:**
1. Add all 5 accounts with valid tokens
2. Click "All Accounts" button
3. Monitor progress

**Expected:**
- Total repos: 500+
- Accounts switch automatically on rate limits
- Queue shows all repos

**Pass Criteria:**
- [ ] All 5 accounts processed
- [ ] Rate limit manager switches accounts
- [ ] Total downloaded >= 450 repos
- [ ] Download completes without crashes

### Test 2.3: Selective Download
**Objective:** Download specific repos only
**Steps:**
1. Click "Selective" button
2. Choose 5 specific repos
3. Click Download Selected

**Pass Criteria:**
- [ ] Only selected repos downloaded
- [ ] Progress shows correct count (5/5)
- [ ] Cancel button works mid-download

### Test 2.4: Batch Download
**Objective:** Download from URL list
**Steps:**
1. Enter 3 repo URLs in batch text area
2. Click "Download All"

**Pass Criteria:**
- [ ] All 3 repos downloaded
- [ ] Error shown for invalid URLs
- [ ] Progress updates per repo

---

## 3. GIT OPERATIONS TESTING

### Test 3.1: Update Existing Repos (Git Pull)
**Objective:** Update already-downloaded repos
**Prerequisites:** Repos exist in download directory
**Steps:**
1. Select a previously downloaded repo
2. Click "Update" button
3. Verify git pull executes

**Pass Criteria:**
- [ ] "Already up to date" or changes pulled
- [ ] No authentication errors
- [ ] Progress shows 100%

### Test 3.2: Push Changes
**Objective:** Push local changes to GitHub
**Prerequisites:** Repo with local changes
**Steps:**
1. Make change to downloaded repo
2. Go to Git Operations tab
3. Enter commit message
4. Click "Push"

**Pass Criteria:**
- [ ] Changes committed successfully
- [ ] Push completes without error
- [ ] Changes visible on GitHub

### Test 3.3: Branch Operations
**Objective:** Work with branches
**Steps:**
1. Enter repo URL
2. Click "Fetch Branches"
3. Select non-default branch
4. Download repo

**Pass Criteria:**
- [ ] Branch list populated correctly
- [ ] Specific branch downloaded
- [ ] Checkout shows correct branch

---

## 4. UI/UX TESTING

### Test 4.1: Theme Switching
**Objective:** Verify dark/light mode
**Steps:**
1. Click theme toggle
2. Verify Matrix background color changes
3. Verify text colors change

**Pass Criteria:**
- [ ] Dark mode: green Matrix, light text
- [ ] Light mode: blue Matrix, dark text
- [ ] Toggle switches correctly

### Test 4.2: Tab Navigation
**Objective:** All tabs accessible
**Steps:**
1. Click each tab (Download, Search, Batch, Git Ops, Settings)
2. Verify content loads
3. Test keyboard shortcuts (Ctrl+1, Ctrl+2, etc.)

**Pass Criteria:**
- [ ] All 5 tabs accessible
- [ ] No UI glitches
- [ ] Shortcuts work

### Test 4.3: System Tray
**Objective:** Minimize to tray works
**Steps:**
1. Click minimize button
2. Verify app minimizes to tray
3. Right-click tray icon
4. Select "Show" to restore

**Pass Criteria:**
- [ ] Minimizes to tray
- [ ] Context menu shows options
- [ ] Restore works
- [ ] Quit works from tray

---

## 5. SEARCH & PREVIEW TESTING

### Test 5.1: GitHub Search
**Objective:** Search public repos
**Steps:**
1. Go to Search tab
2. Enter keyword "ai agent"
3. Click Search

**Pass Criteria:**
- [ ] Results show relevant repos
- [ ] Star counts displayed
- [ ] Topics shown
- [ ] Can add to download queue

### Test 5.2: Repo Preview
**Objective:** Preview repo details
**Steps:**
1. Enter repo URL
2. Click "Preview" button

**Pass Criteria:**
- [ ] Shows stars, forks, language
- [ ] Shows description
- [ ] Shows topics
- [ ] Shows license info

---

## 6. RATE LIMIT TESTING

### Test 6.1: Rate Limit Display
**Objective:** Verify rate limit monitoring
**Steps:**
1. Make multiple API requests
2. Watch rate status label
3. Verify it updates

**Pass Criteria:**
- [ ] Shows remaining requests
- [ ] Shows reset time
- [ ] Warns when low (< 10)
- [ ] Critical warning when < 5

### Test 6.2: Account Auto-Switch
**Objective:** Switch accounts on rate limit
**Prerequisites:** Multiple accounts configured
**Steps:**
1. Exhaust rate limit on Account A
2. Continue making requests

**Expected:** App switches to Account B automatically

**Pass Criteria:**
- [ ] Auto-switches when rate limited
- [ ] Shows notification of switch
- [ ] Resumes operations

---

## 7. ERROR HANDLING TESTING

### Test 7.1: Invalid Token
**Objective:** Handle bad tokens gracefully
**Steps:**
1. Add account with invalid token
2. Try to fetch repos

**Expected:** Clear error message, no crash

**Pass Criteria:**
- [ ] Shows "Invalid or expired token"
- [ ] App remains stable
- [ ] Can remove bad account

### Test 7.2: Network Failure
**Objective:** Handle no internet
**Steps:**
1. Disconnect internet
2. Try to download repo

**Pass Criteria:**
- [ ] Shows "Network error" message
- [ ] Retry option available
- [ ] App doesn't crash

### Test 7.3: Invalid Repo URL
**Objective:** Handle bad URLs
**Steps:**
1. Enter "not-a-real-repo" in URL field
2. Click Download

**Pass Criteria:**
- [ ] Shows error: "Repository not found"
- [ ] No crash
- [ ] Can enter new URL

---

## 8. SETTINGS & PERSISTENCE TESTING

### Test 8.1: Settings Save/Load
**Objective:** Verify settings persist
**Steps:**
1. Change output directory
2. Change theme
3. Close app
4. Reopen app

**Pass Criteria:**
- [ ] Output directory remembered
- [ ] Theme preference saved
- [ ] Account list preserved

### Test 8.2: Recent Downloads
**Objective:** Recent list works
**Steps:**
1. Download 3 repos
2. Check Recent Downloads section
3. Click redownload

**Pass Criteria:**
- [ ] Shows downloaded repos
- [ ] Redownload works
- [ ] Clear Recent works

---

## 9. PERFORMANCE TESTING

### Test 9.1: Large Download Queue
**Objective:** Handle 100+ repos in queue
**Steps:**
1. Queue 100 repos
2. Start download
3. Monitor for 30 minutes

**Pass Criteria:**
- [ ] No memory leaks
- [ ] UI remains responsive
- [ ] Progress updates correctly
- [ ] Can cancel without crash

### Test 9.2: Concurrent Downloads
**Objective:** Multiple workers running
**Steps:**
1. Start 5 simultaneous downloads
2. Monitor system resources

**Pass Criteria:**
- [ ] CPU usage < 50%
- [ ] Memory usage stable
- [ ] All downloads complete

---

## 10. MONETIZATION FEATURE TESTING

### Test 10.1: Repo Inventory Display
**Objective:** Show categorized repo list
**Steps:**
1. Go to Download tab
2. Click "Show ALL Repos"

**Expected:** Shows categorized list (AI Agents, Trading, etc.)

**Pass Criteria:**
- [ ] Categories displayed correctly
- [ ] Repo counts accurate
- [ ] Monetization potential shown

### Test 10.2: Account Breakdown
**Objective:** Show per-account stats
**Steps:**
1. Click "Account Breakdown"

**Expected:** Shows table with accounts and repo counts

**Pass Criteria:**
- [ ] All accounts listed
- [ ] Public/private counts correct
- [ ] Total size calculated

---

## EXECUTION CHECKLIST

### Pre-Test Setup
- [ ] Build latest app from source
- [ ] Ensure check_tokens.py works
- [ ] Prepare test tokens (1 with scope, 1 without)
- [ ] Clear test download directory

### Test Execution Order
1. Token Scope Tests (1.1 - 1.2)
2. Download Tests (2.1 - 2.4)
3. Git Operations (3.1 - 3.3)
4. UI/UX Tests (4.1 - 4.3)
5. Search Tests (5.1 - 5.2)
6. Rate Limit Tests (6.1 - 6.2)
7. Error Handling (7.1 - 7.3)
8. Settings Tests (8.1 - 8.2)
9. Performance Tests (9.1 - 9.2)
10. Monetization Features (10.1 - 10.2)

### Post-Test
- [ ] Review debug.log for errors
- [ ] Check token_report.json
- [ ] Document any failures
- [ ] Create GitHub issues for bugs

---

## TEST RESULTS TEMPLATE

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| 1.1 | Token Validation | | |
| 1.2 | Diagnostic Script | | |
| 2.1 | Single Account Download | | |
| 2.2 | Multi-Account Download | | |
| 2.3 | Selective Download | | |
| 2.4 | Batch Download | | |
| 3.1 | Git Pull | | |
| 3.2 | Git Push | | |
| 3.3 | Branch Operations | | |
| 4.1 | Theme Switching | | |
| 4.2 | Tab Navigation | | |
| 4.3 | System Tray | | |
| 5.1 | GitHub Search | | |
| 5.2 | Repo Preview | | |
| 6.1 | Rate Limit Display | | |
| 6.2 | Account Auto-Switch | | |
| 7.1 | Invalid Token | | |
| 7.2 | Network Failure | | |
| 7.3 | Invalid URL | | |
| 8.1 | Settings Persistence | | |
| 8.2 | Recent Downloads | | |
| 9.1 | Large Queue | | |
| 9.2 | Concurrent Downloads | | |
| 10.1 | Repo Inventory | | |
| 10.2 | Account Breakdown | | |

---

*Test Plan Version: 1.0*
*Last Updated: 2026-04-22*
