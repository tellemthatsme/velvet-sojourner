#!/usr/bin/env python3
"""
RESUMABLE BULK DOWNLOAD - All 5 Accounts
Picks up where it left off, downloads everything
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

APP_DATA = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader")
ACCOUNTS_FILE = os.path.join(APP_DATA, "accounts.json")
REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
LOG_FILE = Path("download_progress.log")

class ResumableDownloader:
    def __init__(self):
        self.load_accounts()
        self.repos_dir = REPOS_DIR
        self.repos_dir.mkdir(exist_ok=True)
        self.stats = {
            'downloaded': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
    def load_accounts(self):
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)
        
        self.accounts = []
        for acc_id, acc in accounts.items():
            self.accounts.append(acc)
        
        print(f"Loaded {len(self.accounts)} accounts")
        
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        
    def get_all_repos(self, account):
        import requests
        
        username = account["username"]
        token = account["token"]
        
        self.log(f"\nFetching repo list for {username}...")
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"https://api.github.com/user/repos?per_page={per_page}&page={page}&type=all"
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                if resp.status_code != 200:
                    self.log(f"  API error: {resp.status_code}")
                    break
                
                data = resp.json()
                if not data:
                    break
                
                repos.extend(data)
                self.log(f"  Page {page}: +{len(data)} repos")
                page += 1
                
                # Rate limit handling
                remaining = int(resp.headers.get("X-RateLimit-Remaining", 0))
                if remaining < 5:
                    reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
                    wait = max(reset_time - time.time(), 0) + 5
                    self.log(f"  Rate limit! Waiting {wait:.0f}s...")
                    time.sleep(wait)
                    
            except Exception as e:
                self.log(f"  Error fetching: {e}")
                break
        
        self.log(f"  Total repos for {username}: {len(repos)}")
        return repos
    
    def process_repo(self, repo, token):
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
            try:
                result = subprocess.run(
                    ["git", "-C", str(target_dir), "pull", "--depth", "1"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    self.stats['updated'] += 1
                    return "updated"
            except:
                pass
            self.stats['skipped'] += 1
            return "skipped"
        
        # Clone new
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(target_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                self.stats['downloaded'] += 1
                return "downloaded"
            else:
                self.stats['failed'] += 1
                return "failed"
        except Exception as e:
            self.stats['failed'] += 1
            return "error"
    
    def download_account(self, account):
        username = account["username"]
        token = account["token"]
        
        self.log(f"\n{'='*70}")
        self.log(f"ACCOUNT: {username}")
        self.log(f"{'='*70}")
        
        repos = self.get_all_repos(account)
        if not repos:
            self.log("No repos found!")
            return
        
        self.log(f"Processing {len(repos)} repositories...\n")
        
        for i, repo in enumerate(repos, 1):
            name = repo["name"]
            owner = repo["owner"]["login"]
            private_mark = "[PRIVATE]" if repo.get("private") else "[public]"
            
            status = self.process_repo(repo, token)
            
            if status == "downloaded":
                self.log(f"  [{i}/{len(repos)}] [OK] DOWNLOADED {owner}/{name} {private_mark}")
            elif status == "updated":
                self.log(f"  [{i}/{len(repos)}] [UPDATE] {owner}/{name}")
            elif status == "failed":
                self.log(f"  [{i}/{len(repos)}] [FAIL] {owner}/{name}")
            
            # Small delay
            time.sleep(0.2)
        
        self.log(f"\n[OK] Account {username} complete!")
    
    def run(self):
        self.log("=" * 70)
        self.log("RESUMABLE BULK DOWNLOAD - All Accounts")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 70)
        
        for account in self.accounts:
            self.download_account(account)
        
        # Summary
        self.log("\n" + "=" * 70)
        self.log("ALL DOWNLOADS COMPLETE!")
        self.log("=" * 70)
        self.log(f"New downloads: {self.stats['downloaded']}")
        self.log(f"Updated:       {self.stats['updated']}")
        self.log(f"Failed:        {self.stats['failed']}")
        self.log(f"Skipped:       {self.stats['skipped']}")
        self.log(f"Completed:     {datetime.now().strftime('%H:%M:%S')}")
        self.log("=" * 70)

if __name__ == "__main__":
    import requests
    dl = ResumableDownloader()
    dl.run()
    print("\nDone! Press ENTER...")
    input()
