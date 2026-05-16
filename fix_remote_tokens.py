"""
Fix remote URLs in behind repos — strip exposed tokens
"""
import subprocess, os

REPOS_DIR = r'C:\temp\velvet-sojourner\repos'
# Skip repos with these patterns (likely private forks)
EXPOSED = ['woodsai69rme_']

fixed = []
skipped = []

for repo_name in sorted(os.listdir(REPOS_DIR)):
    repo_path = os.path.join(REPOS_DIR, repo_name)
    if not os.path.isdir(repo_path) or repo_name.startswith('_'):
        continue

    # Check if this is a skip target
    skip = any(repo_name.startswith(p) for p in EXPOSED)

    try:
        r = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, timeout=10, cwd=repo_path)
        for line in r.stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 2 and parts[0] == 'origin':
                url = parts[1]
                if 'ghp_' in url or 'gho_' in url:
                    # Strip token
                    from urllib.parse import urlparse, urlunparse
                    parsed = urlparse(url)
                    clean_url = urlunparse(parsed._replace(netloc=parsed.hostname))
                    print(f'{repo_name}: token → {clean_url[:60]}')
                    subprocess.run(['git', 'remote', 'set-url', 'origin', clean_url],
                                   capture_output=True, text=True, timeout=10, cwd=repo_path)
                    if not skip:
                        subprocess.run(['git', 'remote', 'update'], capture_output=True, text=True, timeout=30, cwd=repo_path)
                        pull = subprocess.run(['git', 'pull', '--ff-only'], capture_output=True, text=True, timeout=60, cwd=repo_path)
                        if pull.returncode == 0:
                            fixed.append(repo_name)
                        else:
                            skipped.append(f'{repo_name} (pull failed: {pull.stderr[:60]})')
                    else:
                        skipped.append(f'{repo_name} (exposed-pattern, skipped pull)')
                break
    except Exception as e:
        skipped.append(f'{repo_name} ({str(e)[:40]})')

print(f'\nFixed: {len(fixed)}')
for f in fixed: print(f'  OK  {f}')
print(f'\nSkipped: {len(skipped)}')
for s in skipped: print(f'  SKIP {s}')
