import json
import requests
import subprocess
from pathlib import Path
from datetime import datetime

ACCOUNTS_FILE = Path("C:/Users/karma/AppData/Roaming/GitHubDownloader/accounts.json")
REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
LOG_FILE = Path("C:/temp/velvet-sojourner/repo_check_log.txt")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_accounts():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_token(token):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            scopes = r.headers.get("X-OAuth-Scopes", "")
            return True, data.get("login"), data.get("public_repos", 0), data.get("total_private_repos", 0), scopes
        return False, None, 0, 0, f"HTTP {r.status_code}"
    except Exception as e:
        return False, None, 0, 0, str(e)

def get_all_repos(username, token):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/user/repos?type=all&per_page=100&page={page}"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                break
            data = r.json()
            if not data:
                break
            for item in data:
                if item["owner"]["login"].lower() == username.lower():
                    repos.append({
                        "name": item["name"],
                        "full_name": item["full_name"],
                        "private": item["private"],
                        "html_url": item["html_url"],
                        "updated_at": item["updated_at"],
                        "pushed_at": item["pushed_at"],
                        "size": item["size"],
                        "stars": item["stargazers_count"],
                        "language": item["language"] or "",
                        "description": item["description"] or "",
                        "fork": item["fork"],
                    })
            if len(data) < 100:
                break
            page += 1
        except:
            break
    return repos

def check_local_repo(repo_name):
    path = REPOS_DIR / repo_name
    if not path.exists():
        return "MISSING", 0
    git_dir = path / ".git"
    if not git_dir.exists():
        return "NO_GIT", 0
    
    # Get local size
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "count-objects", "-vH"],
            capture_output=True, text=True, timeout=10
        )
        size_line = [l for l in result.stdout.split("\n") if "size-pack:" in l]
        size = size_line[0].split(":")[1].strip() if size_line else "unknown"
    except:
        size = "unknown"
    
    # Check if up to date
    try:
        subprocess.run(["git", "-C", str(path), "fetch", "--depth", "1"], 
                      capture_output=True, timeout=15)
        result = subprocess.run(
            ["git", "-C", str(path), "rev-list", "HEAD..origin/HEAD", "--count"],
            capture_output=True, text=True, timeout=10
        )
        behind = int(result.stdout.strip())
        if behind > 0:
            return f"BEHIND_{behind}", size
        return "CURRENT", size
    except:
        return "ERROR", size

def main():
    log("=" * 70)
    log("COMPLETE GITHUB REPO CHECK")
    log("=" * 70)
    
    accounts = load_accounts()
    
    # Phase 1: Test tokens
    log("\n[PHASE 1] Testing all tokens...")
    valid_accounts = {}
    for key, data in accounts.items():
        username = data["username"]
        token = data["token"]
        valid, login, public, private, scopes = test_token(token)
        if valid:
            log(f"  [OK] {username}: VALID")
            log(f"       Public repos: {public}, Private repos: {private}")
            log(f"       Scopes: {scopes}")
            valid_accounts[username] = {"token": token, "login": login, "public": public, "private": private}
        else:
            log(f"  [FAIL] {username}: {scopes}")
    
    if not valid_accounts:
        log("No valid tokens! Exiting.")
        return
    
    # Phase 2: Fetch all repos from API
    log("\n[PHASE 2] Fetching all repos from GitHub API...")
    all_api_repos = {}
    for username, info in valid_accounts.items():
        log(f"  Fetching repos for {username}...")
        repos = get_all_repos(info["login"], info["token"])
        all_api_repos[username] = repos
        log(f"  Found: {len(repos)} repos")
    
    total_api = sum(len(r) for r in all_api_repos.values())
    log(f"\nTotal repos across all accounts: {total_api}")
    
    # Phase 3: Check local status
    log("\n[PHASE 3] Checking local repositories...")
    local_repos = {d.name: d for d in REPOS_DIR.iterdir() if d.is_dir()}
    log(f"Local repo folders: {len(local_repos)}")
    
    # Phase 4: Compare
    log("\n[PHASE 4] Comparing API vs Local...")
    
    missing_from_local = []
    needs_update = []
    extra_locally = []
    
    for username, repos in all_api_repos.items():
        for repo in repos:
            name = repo["name"]
            status, size = check_local_repo(name)
            if status == "MISSING":
                missing_from_local.append({"name": name, "account": username, "private": repo["private"]})
            elif status.startswith("BEHIND"):
                behind = int(status.split("_")[1])
                needs_update.append({"name": name, "account": username, "behind": behind})
    
    # Check for repos that exist locally but not in API
    api_names = set()
    for repos in all_api_repos.values():
        for r in repos:
            api_names.add(r["name"])
    
    for local_name in local_repos.keys():
        if local_name not in api_names:
            extra_locally.append(local_name)
    
    log(f"\nRepos missing locally: {len(missing_from_local)}")
    log(f"Repos needing update: {len(needs_update)}")
    log(f"Extra repos locally (not in API): {len(extra_locally)}")
    
    # Phase 5: Summary report
    log("\n" + "=" * 70)
    log("SUMMARY REPORT")
    log("=" * 70)
    
    for username, info in valid_accounts.items():
        repos = all_api_repos[username]
        private_count = sum(1 for r in repos if r["private"])
        public_count = len(repos) - private_count
        log(f"\n{username}:")
        log(f"  Total repos: {len(repos)}")
        log(f"  Public: {public_count}")
        log(f"  Private: {private_count}")
        log(f"  Stars (total): {sum(r['stars'] for r in repos)}")
        
        # Top 5 repos by stars
        top = sorted(repos, key=lambda x: x["stars"], reverse=True)[:5]
        log(f"  Top repos:")
        for r in top:
            log(f"    {r['name']} ({r['stars']} stars)")
    
    log(f"\nOverall:")
    log(f"  Total API repos: {total_api}")
    log(f"  Total local repos: {len(local_repos)}")
    log(f"  Missing: {len(missing_from_local)}")
    log(f"  Need update: {len(needs_update)}")
    log(f"  Extra local: {len(extra_locally)}")
    
    # Save missing list
    if missing_from_local:
        with open("C:/temp/velvet-sojourner/missing_repos.json", "w") as f:
            json.dump(missing_from_local, f, indent=2)
        log(f"\nSaved missing repos to: missing_repos.json")
    
    if needs_update:
        with open("C:/temp/velvet-sojourner/needs_update.json", "w") as f:
            json.dump(needs_update, f, indent=2)
        log(f"Saved update list to: needs_update.json")
    
    log("\nCheck complete!")

if __name__ == "__main__":
    main()
