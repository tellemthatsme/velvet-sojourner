import subprocess, os, sys
from urllib.parse import urlparse, urlunparse

sys.stdout.reconfigure(encoding='utf-8')
REPOS_DIR = r'C:\temp\velvet-sojourner\repos'

fixed = 0
no_token = 0
errors = 0

for name in sorted(os.listdir(REPOS_DIR)):
    path = os.path.join(REPOS_DIR, name)
    if not os.path.isdir(path) or name.startswith('_'):
        continue
    try:
        r = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, timeout=10, cwd=path)
        for line in r.stdout.split('\n'):
            parts = line.split()
            if len(parts) >= 2 and parts[0] == 'origin':
                url = parts[1]
                # Check for token patterns
                if 'ghp_' in url or 'gho_' in url or 'github_pat_' in url:
                    parsed = urlparse(url)
                    # Reconstruct without userinfo
                    netloc = parsed.hostname or ''
                    if parsed.port:
                        netloc = f'{netloc}:{parsed.port}'
                    clean_url = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
                    subprocess.run(['git', 'remote', 'set-url', 'origin', clean_url],
                                   capture_output=True, text=True, timeout=10, cwd=path)
                    print(f'FIXED {name}: token stripped')
                    fixed += 1
                else:
                    no_token += 1
                break
    except subprocess.TimeoutExpired:
        errors += 1
    except Exception as e:
        msg = str(e).split('\n')[0][:40]
        print(f'ERR {name}: {msg}')
        errors += 1

print(f'\nDone. Fixed: {fixed}, No token: {no_token}, Errors: {errors}')
