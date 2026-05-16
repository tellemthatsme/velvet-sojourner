import os
import json

repos_dir = r'C:\temp\velvet-sojourner\repos'
repos_info = []

for repo_name in sorted(os.listdir(repos_dir)):
    repo_path = os.path.join(repos_dir, repo_name)
    if not os.path.isdir(repo_path):
        continue
    if repo_name.startswith('_'):
        continue

    info = {
        'name': repo_name,
        'size_mb': 0,
        'has_readme': False,
        'has_package_json': False,
        'has_requirements': False,
        'has_docker': False,
        'has_ci': False,
        'languages': [],
        'file_count': 0,
        'dirs': [],
        'description': ''
    }

    try:
        total_size = 0
        file_count = 0
        for dp, dn, fn in os.walk(repo_path):
            for f in fn:
                try:
                    total_size += os.path.getsize(os.path.join(dp, f))
                    file_count += 1
                except:
                    pass
        info['size_mb'] = round(total_size / 1024 / 1024, 1)
        info['file_count'] = file_count

        top_items = os.listdir(repo_path)
        info['dirs'] = [d for d in top_items if os.path.isdir(os.path.join(repo_path, d)) and not d.startswith('.')][:10]

        info['has_readme'] = any(f.lower().startswith('readme') for f in top_items)
        info['has_package_json'] = 'package.json' in top_items
        info['has_requirements'] = any(f in ['requirements.txt', 'requirements.in'] for f in top_items)
        info['has_docker'] = any(f in ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'] for f in top_items)
        info['has_ci'] = os.path.exists(os.path.join(repo_path, '.github')) or os.path.exists(os.path.join(repo_path, '.gitlab-ci.yml'))

        if info['has_package_json']:
            info['languages'].append('JavaScript/TypeScript')
        if info['has_requirements']:
            info['languages'].append('Python')
        for f in top_items:
            if f.endswith('.py'):
                info['languages'].append('Python')
                break
        for f in top_items:
            if f.endswith('.go'):
                info['languages'].append('Go')
                break
        for f in top_items:
            if f.endswith('.rs'):
                info['languages'].append('Rust')
                break
        for f in top_items:
            if f.endswith('.sol'):
                info['languages'].append('Solidity')
                break
        if not info['languages']:
            info['languages'].append('Unknown')

        if info['has_readme']:
            for f in top_items:
                if f.lower().startswith('readme'):
                    try:
                        with open(os.path.join(repo_path, f), 'r', encoding='utf-8', errors='ignore') as rf:
                            lines = rf.readlines()
                            for line in lines[:30]:
                                line = line.strip()
                                if line and not line.startswith('#') and not line.startswith('![') and len(line) > 10:
                                    info['description'] = line[:200]
                                    break
                    except:
                        pass

        repos_info.append(info)
    except Exception as e:
        print(f'Error scanning {repo_name}: {e}')

output_path = os.path.join(repos_dir, '_SCAN_RESULTS.json')
with open(output_path, 'w') as f:
    json.dump(repos_info, f, indent=2)

print(f'Scanned {len(repos_info)} repos')
print(f'Total size: {sum(r["size_mb"] for r in repos_info):.0f} MB')
print(f'Total files: {sum(r["file_count"] for r in repos_info)}')
print(f'With README: {sum(1 for r in repos_info if r["has_readme"])}')
print(f'With package.json: {sum(1 for r in repos_info if r["has_package_json"])}')
print(f'With requirements.txt: {sum(1 for r in repos_info if r["has_requirements"])}')
print(f'With Docker: {sum(1 for r in repos_info if r["has_docker"])}')
print(f'With CI: {sum(1 for r in repos_info if r["has_ci"])}')
