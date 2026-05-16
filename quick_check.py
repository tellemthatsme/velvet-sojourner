import json
import requests
from pathlib import Path
from datetime import datetime

ACCOUNTS_FILE = Path("C:/Users/karma/AppData/Roaming/GitHubDownloader/accounts.json")
REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")

def load_accounts():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

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
                    repos.append(item["name"])
            if len(data) < 100:
                break
            page += 1
        except:
            break
    return repos

def main():
    print("=" * 70)
    print("QUICK REPO CHECK")
    print("=" * 70)
    
    accounts = load_accounts()
    
    # Get all API repos
    all_api = set()
    by_account = {}
    for key, data in accounts.items():
        username = data["username"]
        token = data["token"]
        print(f"\nFetching repos for {username}...")
        repos = get_all_repos(username, token)
        by_account[username] = repos
        all_api.update(repos)
        print(f"  Found: {len(repos)} repos")
    
    print(f"\nTotal unique repos across all accounts: {len(all_api)}")
    
    # Get local repos
    local = set(d.name for d in REPOS_DIR.iterdir() if d.is_dir())
    print(f"Local repo folders: {len(local)}")
    
    # Compare
    missing = all_api - local
    extra = local - all_api
    
    print(f"\n=== RESULTS ===")
    print(f"Repos in API but NOT local: {len(missing)}")
    print(f"Repos local but NOT in API: {len(extra)}")
    print(f"Repos in BOTH: {len(all_api & local)}")
    
    if missing:
        print(f"\n=== MISSING REPOS ({len(missing)}) ===")
        for name in sorted(missing)[:50]:
            for acc, repos in by_account.items():
                if name in repos:
                    print(f"  {name} (from {acc})")
                    break
        if len(missing) > 50:
            print(f"  ... and {len(missing) - 50} more")
        
        with open("missing_repos.json", "w") as f:
            json.dump(sorted(list(missing)), f, indent=2)
        print(f"\nSaved to: missing_repos.json")
    
    if extra:
        print(f"\n=== EXTRA LOCAL REPOS ({len(extra)}) ===")
        for name in sorted(extra)[:20]:
            print(f"  {name}")
        if len(extra) > 20:
            print(f"  ... and {len(extra) - 20} more")
    
    print("\n=== BY ACCOUNT ===")
    for acc, repos in by_account.items():
        have = len(set(repos) & local)
        miss = len(set(repos) - local)
        print(f"{acc:20}: {have}/{len(repos)} downloaded ({miss} missing)")

if __name__ == "__main__":
    main()
