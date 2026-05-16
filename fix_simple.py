import subprocess, os, sys
sys.stdout.reconfigure(encoding='utf-8')

REPOS_DIR = r'C:\temp\velvet-sojourner\repos'

# These have real GitHub repos with tokens
targets = {
    'my-life-verified': 'https://github.com/tellemthatsme/my-life-verified.git',
    'legacy-video-forge': 'https://github.com/tellemthatsme/legacy-video-forge.git',
    'vidmuse-studio': 'https://github.com/tellemthatsme/vidmuse-studio.git',
    'ai-music-director': 'https://github.com/unknown/ai-music-director.git',
}

for name, correct_url in targets.items():
    path = os.path.join(REPOS_DIR, name)
    if not os.path.isdir(path):
        print(f'MISS {name}')
        continue

    # Get current remote
    r = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, timeout=10, cwd=path)
    for line in r.stdout.split('\n'):
        if 'origin' in line and 'fetch' in line:
            old_url = line.split()[1]
            print(f'{name}: {old_url[:60]}')
            # Set URL without token
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(old_url)
            clean = urlunparse(parsed._replace(netloc=parsed.hostname))
            print(f'  -> clean: {clean[:60]}')
            subprocess.run(['git', 'remote', 'set-url', 'origin', clean], capture_output=True, text=True, timeout=10, cwd=path)
            # Pull
            p = subprocess.run(['git', 'pull', '--ff-only'], capture_output=True, text=True, timeout=60, cwd=path)
            if p.returncode == 0:
                print(f'  -> PULL OK')
            elif 'could not resolve host' in (p.stderr + p.stdout).lower():
                print(f'  -> SKIP (no network)')
            else:
                show = (p.stderr[:100] if p.stderr else p.stdout[:100]).replace('\n',' ')
                print(f'  -> FAIL: {show}')
            break

print('\nDone.')
