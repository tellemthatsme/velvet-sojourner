import json
import requests
import subprocess
import os
from pathlib import Path
from datetime import datetime

ACCOUNTS_FILE = Path("C:/Users/karma/AppData/Roaming/GitHubDownloader/accounts.json")
REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
LOG_FILE = Path("C:/temp/velvet-sojourner/sync_log.txt")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_accounts():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_token(token):
    """Test if a GitHub token is valid and has repo scope"""
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            scopes = r.headers.get("X-OAuth-Scopes", "")
            return True, data["login"], scopes
        else:
            return False, None, r.text
    except Exception as e:
        return False, None, str(e)

def get_all_repos_for_user(username, token):
    """Get ALL repos (public + private) for a user using their token"""
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    repos = []
    page = 1
    while True:
        # Use /user/repos to get all repos the token has access to (including private)
        url = f"https://api.github.com/user/repos?type=all&per_page=100&page={page}"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                log(f"  ERROR fetching repos for {username}: {r.status_code} - {r.text[:200]}")
                break
            data = r.json()
            if not data:
                break
            for repo in data:
                if repo["owner"]["login"].lower() == username.lower():
                    repos.append({
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "private": repo["private"],
                        "html_url": repo["html_url"],
                        "clone_url": repo["clone_url"],
                        "updated_at": repo["updated_at"],
                        "pushed_at": repo["pushed_at"],
                        "size": repo["size"],
                        "stargazers_count": repo["stargazers_count"],
                        "language": repo["language"],
                        "description": repo["description"] or "",
                        "fork": repo["fork"]
                    })
            if len(data) < 100:
                break
            page += 1
        except Exception as e:
            log(f"  ERROR: {e}")
            break
    return repos

def repo_exists_locally(repo_name):
    """Check if repo already exists locally"""
    return (REPOS_DIR / repo_name).exists() and (REPOS_DIR / repo_name / ".git").exists()

def get_local_commit_hash(repo_path):
    """Get latest commit hash from local repo"""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def get_remote_commit_hash(clone_url, token):
    """Get latest commit hash from remote"""
    try:
        # Use ls-remote to get latest commit without cloning
        auth_url = clone_url.replace("https://", f"https://{token}@")
        result = subprocess.run(
            ["git", "ls-remote", auth_url, "HEAD"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except:
        pass
    return None

def download_repo(repo, token):
    """Clone a new repo"""
    repo_name = repo["name"]
    clone_url = repo["clone_url"]
    dest = REPOS_DIR / repo_name
    
    # Add token to URL for private repos
    auth_url = clone_url.replace("https://", f"https://{token}@")
    
    log(f"  Downloading: {repo_name} ({'private' if repo['private'] else 'public'})")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", auth_url, str(dest)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            log(f"  [OK] Downloaded: {repo_name}")
            return True
        else:
            log(f"  [FAIL] Failed: {repo_name} - {result.stderr[:200]}")
            return False
    except Exception as e:
        log(f"  [FAIL] Error: {repo_name} - {e}")
        return False

def update_repo(repo_name, token, clone_url):
    """Pull latest changes for existing repo"""
    repo_path = REPOS_DIR / repo_name
    log(f"  Updating: {repo_name}")
    try:
        # Fetch and check if behind
        result = subprocess.run(
            ["git", "-C", str(repo_path), "fetch", "--depth", "1"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            log(f"  ✗ Fetch failed: {repo_name}")
            return False
        
        # Check if local is behind remote
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-list", "HEAD..origin/HEAD", "--count"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            behind = int(result.stdout.strip())
            if behind > 0:
                # Reset to latest (since we use --depth 1)
                subprocess.run(
                    ["git", "-C", str(repo_path), "reset", "--hard", "origin/HEAD"],
                    capture_output=True, text=True, timeout=30
                )
                log(f"  [OK] Updated: {repo_name} ({behind} commits behind)")
                return True
            else:
                log(f"  [OK] Current: {repo_name}")
                return True
    except Exception as e:
        log(f"  [FAIL] Error updating: {repo_name} - {e}")
    return False

def main():
    log("=" * 70)
    log("AGENTFORGE: Full Repo Sync - All Accounts, All Repos")
    log("=" * 70)
    
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    
    accounts = load_accounts()
    
    # Phase 1: Test all tokens
    log("\n[PHASE 1] Testing tokens...")
    valid_accounts = {}
    for key, data in accounts.items():
        username = data["username"]
        token = data["token"]
        valid, login, scopes = test_token(token)
        if valid:
            log(f"  [OK] {username}: VALID (scopes: {scopes})")
            valid_accounts[username] = token
        else:
            log(f"  [FAIL] {username}: INVALID - {login or scopes}")
    
    if not valid_accounts:
        log("No valid tokens found. Exiting.")
        return
    
    # Phase 2: Fetch all repos for each account
    log("\n[PHASE 2] Fetching all repos (public + private)...")
    all_remote_repos = {}
    for username, token in valid_accounts.items():
        log(f"  Fetching repos for {username}...")
        repos = get_all_repos_for_user(username, token)
        all_remote_repos[username] = repos
        log(f"  Found: {len(repos)} repos")
    
    total_remote = sum(len(repos) for repos in all_remote_repos.values())
    log(f"\nTotal repos across all accounts: {total_remote}")
    
    # Phase 3: Compare with local
    log("\n[PHASE 3] Comparing with local repos...")
    existing_repos = {d.name for d in REPOS_DIR.iterdir() if d.is_dir() and (d / ".git").exists()}
    log(f"  Local repos: {len(existing_repos)}")
    
    new_repos = []
    update_candidates = []
    
    for username, repos in all_remote_repos.items():
        for repo in repos:
            name = repo["name"]
            if name in existing_repos:
                update_candidates.append((repo, username))
            else:
                new_repos.append((repo, username))
    
    log(f"  New repos to download: {len(new_repos)}")
    log(f"  Existing repos to check: {len(update_candidates)}")
    
    # Phase 4: Download new repos
    if new_repos:
        log(f"\n[PHASE 4] Downloading {len(new_repos)} new repos...")
        downloaded = 0
        failed = 0
        for repo, username in new_repos:
            token = valid_accounts[username]
            if download_repo(repo, token):
                downloaded += 1
            else:
                failed += 1
        log(f"  Downloaded: {downloaded}, Failed: {failed}")
    else:
        log("\n[PHASE 4] No new repos to download.")
    
    # Phase 5: Update existing repos
    if update_candidates:
        log(f"\n[PHASE 5] Checking {len(update_candidates)} existing repos for updates...")
        updated = 0
        current = 0
        failed = 0
        for repo, username in update_candidates:
            token = valid_accounts[username]
            if update_repo(repo["name"], token, repo["clone_url"]):
                # We already logged success/failure in the function
                pass
        log(f"  Update check complete")
    else:
        log("\n[PHASE 5] No existing repos to check.")
    
    # Final stats
    final_local = len([d for d in REPOS_DIR.iterdir() if d.is_dir() and (d / ".git").exists()])
    log("\n" + "=" * 70)
    log("SYNC COMPLETE")
    log("=" * 70)
    log(f"Final local repo count: {final_local}")
    log(f"Log saved to: {LOG_FILE}")

if __name__ == "__main__":
    main()
