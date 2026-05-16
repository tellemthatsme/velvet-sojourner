"""
Fix the 17 repos behind remote by stripping tokens from URLs and pulling.
"""
import os, subprocess, json

REPOS_DIR = r'repos'

# Read which repos are behind from the scan
with open('repos/_SCAN_ALL_RESULTS.json') as f:
    scan = json.load(f)

repos = {r['name']: r for r in scan['repos']}

# Check all repos for behind status
behind = []
for repo_name in sorted(os.listdir(REPOS_DIR)):
    repo_path = os.path.join(REPOS_DIR, repo_name)
    if not os.path.isdir(repo_path) or repo_name.startswith('_'):
        continue
    try:
        subprocess.run(['git', 'remote', 'update'], capture_output=True, text=True, timeout=30, cwd=repo_path)
        rev = subprocess.run(
            ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'],
            capture_output=True, text=True, timeout=15, cwd=repo_path
        )
        if rev.returncode == 0 and rev.stdout.strip():
            parts = rev.stdout.strip().split()
            if len(parts) >= 2 and int(parts[1]) > 0:
                behind.append((repo_name, int(parts[1]), int(parts[0])))
    except Exception:
        pass

print(f'Found {len(behind)} repos behind remote:\n')

fixed = 0
skipped = 0
for name, behind_count, ahead_count in sorted(behind, key=lambda x: -x[1]):
    repo_path = os.path.join(REPOS_DIR, name)

    # Get current remote URL
    result = subprocess.run(
        ['git', 'remote', '-v'],
        capture_output=True, text=True, timeout=10, cwd=repo_path
    )
    urls = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 2:
            urls.append(parts[1])

    if not urls:
        print(f'SKIP {name}: no remote URL')
        skipped += 1
        continue

    url = urls[0]

    # Check for token in URL
    if 'ghp_' in url or 'gho_' in url or 'github_pat_' in url:
        # Token found — strip it
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        # The userinfo part has the token
        clean_url = urlunparse(parsed._replace(netloc=parsed.hostname))
        print(f'FIX  {name}: {behind_count} behind, token stripped, pulling...')
        subprocess.run(['git', 'remote', 'set-url', 'origin', clean_url],
                       capture_output=True, text=True, timeout=10, cwd=repo_path)
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, timeout=120, cwd=repo_path)
        if result.returncode == 0:
            print(f'  -> pull OK')
            fixed += 1
        else:
            print(f'  -> pull FAILED: {result.stderr[:100]}')
    else:
        # No token — just pull
        print(f'PULL {name}: {behind_count} behind, no token, pulling...')
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, timeout=120, cwd=repo_path)
        if result.returncode == 0:
            print(f'  -> pull OK')
            fixed += 1
        else:
            print(f'  -> pull FAILED: {result.stderr[:100]}')

print(f'\nDone. Fixed: {fixed}, Skipped: {skipped}')
