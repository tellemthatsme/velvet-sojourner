import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
MISSING_FILE = Path("C:/temp/velvet-sojourner/missing_repos.json")
LOG_FILE = Path("C:/temp/velvet-sojourner/cleanup_log.txt")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def remove_readonly(func, path, _):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def load_accounts():
    with open("C:/Users/karma/AppData/Roaming/GitHubDownloader/accounts.json", "r", encoding="utf-8") as f:
        return json.load(f)

def find_duplicates():
    """Find prefixed duplicate repos"""
    log("Finding duplicate repos...")
    repos = [d.name for d in REPOS_DIR.iterdir() if d.is_dir()]
    
    # Find prefixed versions (e.g., "Ashlee69r_ai-dev-command" vs "ai-dev-command")
    duplicates = []
    for name in repos:
        # Check if this is a prefixed version
        if "_" in name and not name.startswith("_"):
            parts = name.split("_", 1)
            if len(parts) == 2:
                prefix, base = parts
                # Check if base name exists without prefix
                if base in repos and base != name:
                    duplicates.append(name)
    
    log(f"Found {len(duplicates)} prefixed duplicates")
    return duplicates

def remove_duplicates(duplicates):
    """Remove prefixed duplicate repos"""
    log(f"\nRemoving {len(duplicates)} duplicates...")
    removed = 0
    failed = 0
    
    for name in duplicates:
        path = REPOS_DIR / name
        try:
            if path.exists():
                shutil.rmtree(path, onerror=remove_readonly)
                removed += 1
                log(f"  [OK] Removed: {name}")
        except Exception as e:
            failed += 1
            log(f"  [FAIL] Could not remove {name}: {e}")
    
    log(f"Removed: {removed}, Failed: {failed}")
    return removed

def download_missing():
    """Download missing repos"""
    if not MISSING_FILE.exists():
        log("No missing_repos.json found!")
        return 0
    
    with open(MISSING_FILE, "r") as f:
        missing = json.load(f)
    
    log(f"\nDownloading {len(missing)} missing repos...")
    
    accounts = load_accounts()
    
    # Build token lookup by username
    token_map = {}
    for key, data in accounts.items():
        token_map[data["username"]] = data["token"]
    
    downloaded = 0
    failed = 0
    
    for repo_name in missing:
        # Determine which account this belongs to
        # Check which account has this repo
        account = None
        for username in token_map.keys():
            # We don't know which account, try all
            pass
        
        # Try downloading with each token until one works
        success = False
        for username, token in token_map.items():
            clone_url = f"https://{token}@github.com/{username}/{repo_name}.git"
            dest = REPOS_DIR / repo_name
            
            try:
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", clone_url, str(dest)],
                    capture_output=True, text=True, timeout=120
                )
                if result.returncode == 0:
                    downloaded += 1
                    log(f"  [OK] Downloaded: {repo_name} (from {username})")
                    success = True
                    break
            except:
                pass
        
        if not success:
            failed += 1
            log(f"  [FAIL] Could not download: {repo_name}")
    
    log(f"Downloaded: {downloaded}, Failed: {failed}")
    return downloaded

def main():
    log("=" * 70)
    log("REPO CLEANUP & SYNC")
    log("=" * 70)
    
    # Phase 1: Remove duplicates
    log("\n[PHASE 1] Removing duplicate repos...")
    duplicates = find_duplicates()
    if duplicates:
        log(f"Duplicates to remove: {len(duplicates)}")
        for d in duplicates[:10]:
            log(f"  - {d}")
        if len(duplicates) > 10:
            log(f"  ... and {len(duplicates) - 10} more")
        removed = remove_duplicates(duplicates)
    else:
        log("No duplicates found")
        removed = 0
    
    # Phase 2: Download missing
    log("\n[PHASE 2] Downloading missing repos...")
    downloaded = download_missing()
    
    # Phase 3: Final stats
    log("\n" + "=" * 70)
    log("CLEANUP COMPLETE")
    log("=" * 70)
    
    final_count = len([d for d in REPOS_DIR.iterdir() if d.is_dir()])
    log(f"Repos removed: {removed}")
    log(f"Repos downloaded: {downloaded}")
    log(f"Final repo count: {final_count}")

if __name__ == "__main__":
    import os, stat
    main()
