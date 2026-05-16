#!/usr/bin/env python3
"""
BULK REPO DOWNLOADER - Multi-Account
Downloads ALL repos from working accounts (tellemthatsme + woodsai69rme)
Run this while fixing other tokens in parallel
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Configuration
APP_DATA = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader")
ACCOUNTS_FILE = os.path.join(APP_DATA, "accounts.json")
REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
LOG_FILE = Path("download_progress.log")

class BulkDownloader:
    def __init__(self):
        self.load_accounts()
        self.repos_dir = REPOS_DIR
        self.repos_dir.mkdir(exist_ok=True)
        self.downloaded = 0
        self.failed = 0
        self.existing = 0
        self.total_repos = 0
        
    def load_accounts(self):
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)
        
        # Find working accounts (tellemthatsme + woodsai69rme)
        self.working_accounts = []
        for acc_id, acc in accounts.items():
            if acc["username"] in ["tellemthatsme", "woodsai69rme"]:
                self.working_accounts.append(acc)
        
        if not self.working_accounts:
            print("ERROR: No working accounts found!")
            sys.exit(1)
            
        print(f"Loaded {len(self.working_accounts)} working accounts:")
        for acc in self.working_accounts:
            print(f"  - {acc['username']}")
    
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    
    def get_all_repos(self, account):
        """Fetch all repos for an account"""
        import requests
        
        username = account["username"]
        token = account["token"]
        
        self.log(f"\nFetching repositories for {username}...")
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"https://api.github.com/user/repos?per_page={per_page}&page={page}&type=all"
            resp = requests.get(url, headers=headers, timeout=30)
            
            if resp.status_code != 200:
                self.log(f"  ERROR: API returned {resp.status_code}")
                break
            
            data = resp.json()
            if not data:
                break
            
            repos.extend(data)
            self.log(f"  Page {page}: +{len(data)} repos (total so far: {len(repos)})")
            page += 1
            
            # Rate limit check
            remaining = int(resp.headers.get("X-RateLimit-Remaining", 0))
            if remaining < 5:
                reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset_time - time.time(), 0) + 5
                self.log(f"  Rate limit approaching. Waiting {wait:.0f} seconds...")
                time.sleep(wait)
        
        self.log(f"  Total for {username}: {len(repos)} repositories")
        return repos
    
    def clone_repo(self, repo, token):
        """Clone or update a single repo"""
        name = repo["name"]
        owner = repo["owner"]["login"]
        clone_url = repo["clone_url"]
        private = repo.get("private", False)
        
        # Use token in URL for private repos
        if private:
            clone_url = f"https://{token}@github.com/{owner}/{name}.git"
        
        target_dir = self.repos_dir / f"{owner}_{name}"
        
        # Check if already exists
        if target_dir.exists():
            # Try to pull updates
            try:
                result = subprocess.run(
                    ["git", "-C", str(target_dir), "pull"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    self.log(f"    [UPDATED] {owner}/{name}")
                    self.existing += 1
                    return True
                else:
                    # Might be a public repo that was cloned before
                    pass
            except:
                pass
            return False
        
        # Clone new repo
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(target_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                self.log(f"    [DOWNLOADED] {owner}/{name}")
                self.downloaded += 1
                return True
            else:
                error = result.stderr[:80] if result.stderr else "Unknown error"
                self.log(f"    [FAILED] {owner}/{name}: {error}")
                self.failed += 1
                return False
        except Exception as e:
            self.log(f"    [ERROR] {owner}/{name}: {str(e)[:80]}")
            self.failed += 1
            return False
    
    def download_account(self, account):
        """Download all repos for one account"""
        username = account["username"]
        token = account["token"]
        
        self.log(f"\n{'='*70}")
        self.log(f"PROCESSING ACCOUNT: {username}")
        self.log(f"{'='*70}")
        
        repos = self.get_all_repos(account)
        
        if not repos:
            self.log(f"No repositories found for {username}")
            return
        
        self.log(f"Downloading {len(repos)} repositories...")
        
        for i, repo in enumerate(repos, 1):
            name = repo["name"]
            owner = repo["owner"]["login"]
            private = "PRIVATE" if repo.get("private") else "public"
            
            self.log(f"  [{i}/{len(repos)}] {owner}/{name} ({private})")
            self.clone_repo(repo, token)
            
            # Small delay to be nice to GitHub
            time.sleep(0.3)
        
        self.log(f"Account {username} complete!")
    
    def run(self):
        self.log("=" * 70)
        self.log("BULK REPO DOWNLOADER - Multi-Account")
        self.log(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 70)
        
        # Process each working account
        for account in self.working_accounts:
            self.download_account(account)
        
        # Final summary
        self.log("")
        self.log("=" * 70)
        self.log("DOWNLOAD COMPLETE")
        self.log("=" * 70)
        self.log(f"Total downloaded:  {self.downloaded}")
        self.log(f"Total updated:     {self.existing}")
        self.log(f"Total failed:      {self.failed}")
        self.log(f"Time completed:    {datetime.now().strftime('%H:%M:%S')}")
        self.log("=" * 70)
        self.log("")
        self.log("You can now:")
        self.log("1. Continue fixing remaining tokens (leahmfoots, acidlink, Ashlee69r)")
        self.log("2. Run: python github_export_processor.py")
        self.log("3. Launch your product!")

if __name__ == "__main__":
    import requests
    downloader = BulkDownloader()
    downloader.run()
    print("\nDone! Press ENTER to exit...")
    input()
