#!/usr/bin/env python3
"""
FINISH DOWNLOAD - woodsai69rme remaining repos
Picks up where it left off
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
LOG_FILE = Path("download_finish.log")

class FinishDownloader:
    def __init__(self):
        self.load_account()
        self.repos_dir = REPOS_DIR
        self.stats = {'downloaded': 0, 'failed': 0, 'skipped': 0}
        
    def load_account(self):
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)
        
        # Only woodsai69rme
        self.account = None
        for acc_id, acc in accounts.items():
            if acc["username"] == "woodsai69rme":
                self.account = acc
                self.token = acc["token"]
                break
        
        if not self.account:
            print("ERROR: woodsai69rme not found!")
            sys.exit(1)
            
        print(f"Loaded account: woodsai69rme")
        
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        
    def get_all_repos(self):
        import requests
        
        self.log("Fetching repo list for woodsai69rme...")
        headers = {
            "Authorization": f"token {self.token}",
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
                
                remaining = int(resp.headers.get("X-RateLimit-Remaining", 0))
                if remaining < 5:
                    reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
                    wait = max(reset_time - time.time(), 0) + 5
                    self.log(f"  Rate limit! Waiting {wait:.0f}s...")
                    time.sleep(wait)
                    
            except Exception as e:
                self.log(f"  Error: {e}")
                break
        
        self.log(f"  Total repos: {len(repos)}")
        return repos
    
    def clone_repo(self, repo):
        name = repo["name"]
        owner = repo["owner"]["login"]
        clone_url = repo["clone_url"]
        private = repo.get("private", False)
        
        if private:
            clone_url = f"https://{self.token}@github.com/{owner}/{name}.git"
        
        target_dir = self.repos_dir / f"{owner}_{name}"
        
        if target_dir.exists():
            self.stats['skipped'] += 1
            return "skipped"
        
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
                error = result.stderr[:80] if result.stderr else "Unknown"
                self.log(f"    [FAIL] {owner}/{name}: {error}")
                self.stats['failed'] += 1
                return "failed"
        except Exception as e:
            self.log(f"    [ERROR] {owner}/{name}: {str(e)[:80]}")
            self.stats['failed'] += 1
            return "error"
    
    def run(self):
        self.log("=" * 70)
        self.log("FINISHING woodsai69rme DOWNLOAD")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 70)
        
        repos = self.get_all_repos()
        if not repos:
            self.log("No repos found!")
            return
        
        self.log(f"Processing {len(repos)} repos (skipping existing)...")
        
        for i, repo in enumerate(repos, 1):
            name = repo["name"]
            owner = repo["owner"]["login"]
            private = "[PRIVATE]" if repo.get("private") else "[public]"
            
            target_dir = self.repos_dir / f"{owner}_{name}"
            
            if target_dir.exists():
                self.stats['skipped'] += 1
                continue
            
            self.log(f"  [{i}/{len(repos)}] Downloading {owner}/{name} {private}")
            
            status = self.clone_repo(repo)
            if status == "downloaded":
                self.log(f"    [OK] Downloaded!")
            
            time.sleep(0.2)
        
        self.log("\n" + "=" * 70)
        self.log("DOWNLOAD COMPLETE")
        self.log("=" * 70)
        self.log(f"New downloads: {self.stats['downloaded']}")
        self.log(f"Failed:        {self.stats['failed']}")
        self.log(f"Skipped:       {self.stats['skipped']}")
        self.log(f"Completed:     {datetime.now().strftime('%H:%M:%S')}")
        self.log("=" * 70)

if __name__ == "__main__":
    import requests
    dl = FinishDownloader()
    dl.run()
    print("\nDone! Press ENTER...")
    input()
