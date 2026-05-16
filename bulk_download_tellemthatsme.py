#!/usr/bin/env python3
"""
BULK REPO DOWNLOADER - For tellemthatsme
Downloads ALL repos (public + private) using the working token
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
        self.load_account()
        self.repos_dir = REPOS_DIR
        self.repos_dir.mkdir(exist_ok=True)
        self.downloaded = 0
        self.failed = 0
        self.existing = 0
        
    def load_account(self):
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)
        
        # Find tellemthatsme
        self.account = None
        for acc_id, acc in accounts.items():
            if acc["username"] == "tellemthatsme":
                self.account = acc
                self.token = acc["token"]
                break
        
        if not self.account:
            print("ERROR: tellemthatsme account not found!")
            sys.exit(1)
            
        print(f"Loaded account: tellemthatsme")
        print(f"Token: {self.token[:20]}...{self.token[-10:]}")
    
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    
    def get_all_repos(self):
        """Fetch all repos for tellemthatsme"""
        import requests
        
        self.log("Fetching repository list from GitHub API...")
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"https://api.github.com/user/repos?per_page={per_page}&page={page}&type=all"
            resp = requests.get(url, headers=headers, timeout=30)
            
            if resp.status_code != 200:
                self.log(f"ERROR: API returned {resp.status_code}")
                break
            
            data = resp.json()
            if not data:
                break
            
            repos.extend(data)
            self.log(f"  Fetched page {page}: {len(data)} repos (total: {len(repos)})")
            page += 1
            
            # Rate limit check
            remaining = int(resp.headers.get("X-RateLimit-Remaining", 0))
            if remaining < 5:
                reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset_time - time.time(), 0) + 5
                self.log(f"  Rate limit approaching. Waiting {wait:.0f} seconds...")
                time.sleep(wait)
        
        self.log(f"Total repositories found: {len(repos)}")
        return repos
    
    def clone_repo(self, repo):
        """Clone or update a single repo"""
        name = repo["name"]
        owner = repo["owner"]["login"]
        clone_url = repo["clone_url"]
        private = repo.get("private", False)
        
        # Use token in URL for private repos
        if private:
            clone_url = f"https://{self.token}@github.com/{owner}/{name}.git"
        
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
                    self.log(f"  [UPDATED] {owner}/{name}")
                    self.existing += 1
                    return True
                else:
                    self.log(f"  [UPDATE FAILED] {owner}/{name}: {result.stderr[:100]}")
            except Exception as e:
                self.log(f"  [UPDATE ERROR] {owner}/{name}: {e}")
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
                self.log(f"  [DOWNLOADED] {owner}/{name}")
                self.downloaded += 1
                return True
            else:
                self.log(f"  [FAILED] {owner}/{name}: {result.stderr[:100]}")
                self.failed += 1
                return False
        except Exception as e:
            self.log(f"  [ERROR] {owner}/{name}: {e}")
            self.failed += 1
            return False
    
    def run(self):
        self.log("=" * 70)
        self.log("BULK REPO DOWNLOADER - Starting")
        self.log("Account: tellemthatsme")
        self.log("=" * 70)
        
        # Get list of repos
        repos = self.get_all_repos()
        
        if not repos:
            self.log("No repositories found!")
            return
        
        self.log(f"\nStarting download of {len(repos)} repositories...")
        self.log(f"Target directory: {self.repos_dir}")
        self.log("")
        
        # Download each repo
        for i, repo in enumerate(repos, 1):
            name = repo["name"]
            owner = repo["owner"]["login"]
            private = "(PRIVATE)" if repo.get("private") else "(public)"
            
            self.log(f"[{i}/{len(repos)}] Processing {owner}/{name} {private}")
            self.clone_repo(repo)
            
            # Small delay to be nice to GitHub
            time.sleep(0.5)
        
        # Summary
        self.log("")
        self.log("=" * 70)
        self.log("DOWNLOAD COMPLETE")
        self.log("=" * 70)
        self.log(f"Total repos:     {len(repos)}")
        self.log(f"Downloaded:      {self.downloaded}")
        self.log(f"Updated:         {self.existing}")
        self.log(f"Failed:          {self.failed}")
        self.log(f"Success rate:    {((self.downloaded + self.existing) / len(repos) * 100):.1f}%")
        self.log("=" * 70)

if __name__ == "__main__":
    import requests
    downloader = BulkDownloader()
    downloader.run()
    print("\nDone! Press ENTER to exit...")
    input()
