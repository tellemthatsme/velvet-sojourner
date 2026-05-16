#!/usr/bin/env python3
"""
Re-download failed/empty repos from all 5 GitHub accounts.
Maps repo names to owners and clones with appropriate tokens.
"""
import json
import os
import subprocess
import time
import sys
from pathlib import Path

REPOS_DIR = r"C:\temp\velvet-sojourner\repos"
ACCOUNTS_FILE = r"C:\Users\karma\AppData\Roaming\GitHubDownloader\accounts.json"
FAILED_LIST = r"C:\temp\velvet-sojourner\failed_repos.txt"
LOG_FILE = r"C:\temp\velvet-sojourner\redownload_log.txt"

# Load accounts
with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
    accounts = json.load(f)

# Build token map by username
token_map = {}
for key, acc in accounts.items():
    token_map[acc['username']] = acc['token']

# Load failed repo list (strip BOM if present)
with open(FAILED_LIST, 'r', encoding='utf-8-sig') as f:
    failed_repos = [line.strip() for line in f if line.strip()]

# Determine owner from repo name prefix
def get_owner(repo_name):
    prefixes = {
        'tellemthatsme_': 'tellemthatsme',
        'leahmfoots_': 'leahmfoots',
        'acidlink_': 'acidlink',
        'Ashlee69r_': 'Ashlee69r',
        'woodsai69rme_': 'woodsai69rme',
    }
    for prefix, owner in prefixes.items():
        if repo_name.startswith(prefix):
            return owner, repo_name[len(prefix):]
    # No prefix — try all accounts via API later
    return None, repo_name

# Try to find repo on GitHub using tokens
def find_repo_owner(repo_name, token_map):
    import urllib.request
    for username, token in token_map.items():
        url = f"https://api.github.com/repos/{username}/{repo_name}"
        req = urllib.request.Request(url, headers={
            'Authorization': f'token {token}',
            'User-Agent': 'GitHubDownloader'
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return username
        except Exception:
            continue
    return None

# Clone repo
def clone_repo(owner, repo_name, token, dest_dir):
    import shutil
    if os.path.exists(dest_dir):
        # Force remove existing directory completely
        shutil.rmtree(dest_dir, ignore_errors=True)
        # Wait a moment for filesystem
        time.sleep(0.2)

    clone_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
    cmd = ['git', 'clone', '--depth=1', clone_url, dest_dir]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return True, "OK"
        else:
            return False, result.stderr[:200]
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)[:200]

# Main loop
results = {'success': [], 'failed': [], 'skipped': []}
log_lines = []

print(f"Re-downloading {len(failed_repos)} failed repos...")
print(f"Accounts available: {list(token_map.keys())}")
print("=" * 60)

for i, repo_name in enumerate(failed_repos, 1):
    owner, actual_name = get_owner(repo_name)

    if owner is None:
        # Try to find owner via API
        owner = find_repo_owner(repo_name, token_map)
        actual_name = repo_name

    if owner is None:
        msg = f"[{i}/{len(failed_repos)}] SKIP: Cannot determine owner for {repo_name}"
        print(msg)
        log_lines.append(msg)
        results['skipped'].append(repo_name)
        continue

    if owner not in token_map:
        msg = f"[{i}/{len(failed_repos)}] SKIP: No token for owner {owner} ({repo_name})"
        print(msg)
        log_lines.append(msg)
        results['skipped'].append(repo_name)
        continue

    dest = os.path.join(REPOS_DIR, repo_name)
    token = token_map[owner]

    msg = f"[{i}/{len(failed_repos)}] Cloning {owner}/{actual_name} -> {repo_name} ..."
    print(msg, end=' ')
    log_lines.append(msg)

    success, info = clone_repo(owner, actual_name, token, dest)

    if success:
        # Count files
        file_count = sum(1 for _, _, files in os.walk(dest) for _ in files)
        msg = f"OK ({file_count} files)"
        results['success'].append((repo_name, file_count))
    else:
        msg = f"FAILED: {info}"
        results['failed'].append((repo_name, info))

    print(msg)
    log_lines.append(msg)

    # Rate limit safety
    time.sleep(0.5)

# Summary
summary = []
summary.append("\n" + "=" * 60)
summary.append(f"RE-DOWNLOAD COMPLETE")
summary.append(f"Success: {len(results['success'])}")
summary.append(f"Failed:  {len(results['failed'])}")
summary.append(f"Skipped: {len(results['skipped'])}")
summary.append("=" * 60)

if results['failed']:
    summary.append("\nFAILED REPOS:")
    for repo, err in results['failed']:
        summary.append(f"  - {repo}: {err}")

if results['skipped']:
    summary.append("\nSKIPPED REPOS (no owner found):")
    for repo in results['skipped']:
        summary.append(f"  - {repo}")

summary_text = "\n".join(summary)
print(summary_text)

# Save log
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write("\n".join(log_lines) + "\n" + summary_text)

print(f"\nLog saved to: {LOG_FILE}")
