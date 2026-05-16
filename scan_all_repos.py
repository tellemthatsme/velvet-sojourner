"""
Phase 1: Comprehensive Repo Scanner & Classifier
Scans all repos, scores quality, classifies A/B/C tiers
"""
import os
import json
import re
from datetime import datetime
from collections import Counter

REPOS_DIR = r'C:\temp\velvet-sojourner\repos'
OUTPUT_FILE = os.path.join(REPOS_DIR, '_SCAN_ALL_RESULTS.json')
SUMMARY_FILE = r'C:\temp\velvet-sojourner\REPO_CLASSIFICATION.md'

CLONE_INDICATORS = [
    r'^v0-', r'^woodsai69rme_', r'clone', r'bolt$', r'bolt\d',
    r'^\w-\d+$', r'-clone', r'-copy', r'-duplicate',
]


def scan_repo(repo_name, repo_path):
    info = {
        'name': repo_name,
        'path': repo_path,
        'size_mb': 0,
        'file_count': 0,
        'dir_count': 0,
        'has_readme': False,
        'readme_length': 0,
        'has_license': False,
        'has_git': False,
        'has_gitignore': False,
        'has_dockerfile': False,
        'has_docker_compose': False,
        'has_ci': False,
        'has_tests': False,
        'has_makefile': False,
        'has_package_json': False,
        'has_requirements': False,
        'has_pyproject': False,
        'has_cargo': False,
        'has_go_mod': False,
        'has_composer': False,
        'languages': [],
        'has_python': False,
        'has_js_ts': False,
        'has_go': False,
        'has_rust': False,
        'has_solidity': False,
        'has_html': False,
        'has_css': False,
        'top_files': [],
        'description': '',
        'is_likely_clone': False,
        'clone_type': '',
        'error': '',
        'score': 0,
    }

    try:
        if not os.path.isdir(repo_path):
            return None

        info['has_git'] = os.path.isdir(os.path.join(repo_path, '.git'))

        top_items = set()
        try:
            top_items = set(os.listdir(repo_path))
        except PermissionError:
            info['error'] = 'permission denied'
            return info

        info['top_files'] = sorted(top_items)[:20]

        total_size = 0
        file_count = 0
        dir_count = 0
        all_extensions = []

        for dp, dn, fn in os.walk(repo_path):
            if '.git' in dp.split(os.sep):
                continue
            dir_count += len(dn)
            for f in fn:
                try:
                    fp = os.path.join(dp, f)
                    if os.path.isfile(fp):
                        total_size += os.path.getsize(fp)
                        file_count += 1
                        ext = os.path.splitext(f)[1].lower()
                        if ext:
                            all_extensions.append(ext)
                except (OSError, PermissionError):
                    pass

        info['size_mb'] = round(total_size / 1024 / 1024, 1)
        info['file_count'] = file_count
        info['dir_count'] = dir_count

        ext_counts = Counter(all_extensions)
        info['extensions'] = dict(ext_counts.most_common(10))

        info['has_readme'] = any(f.lower().startswith('readme') for f in top_items)
        if info['has_readme']:
            for f in top_items:
                if f.lower().startswith('readme'):
                    try:
                        with open(os.path.join(repo_path, f), 'r', encoding='utf-8', errors='ignore') as rf:
                            content = rf.read()
                            info['readme_length'] = len(content)
                            first_lines = content.strip().split('\n')[:10]
                            for line in first_lines:
                                line = line.strip()
                                if line and not line.startswith('#') and not line.startswith('![') and len(line) > 10:
                                    info['description'] = line[:300]
                                    break
                            if not info['description']:
                                for line in first_lines:
                                    line = line.strip()
                                    if line and len(line) > 5:
                                        info['description'] = line[:300]
                                        break
                    except:
                        pass

        info['has_license'] = any(f.lower().startswith('license') or f.lower().startswith('licence') for f in top_items)
        info['has_gitignore'] = '.gitignore' in top_items
        info['has_dockerfile'] = 'Dockerfile' in top_items
        info['has_docker_compose'] = ('docker-compose.yml' in top_items or
                                      'docker-compose.yaml' in top_items)
        info['has_ci'] = (os.path.isdir(os.path.join(repo_path, '.github')) or
                          'Jenkinsfile' in top_items or
                          '.gitlab-ci.yml' in top_items)
        info['has_makefile'] = 'Makefile' in top_items or 'makefile' in top_items
        info['has_package_json'] = 'package.json' in top_items
        info['has_requirements'] = 'requirements.txt' in top_items
        info['has_pyproject'] = 'pyproject.toml' in top_items
        info['has_cargo'] = 'Cargo.toml' in top_items
        info['has_go_mod'] = 'go.mod' in top_items
        info['has_composer'] = 'composer.json' in top_items

        for f in top_items:
            if f.endswith('.py'):
                info['has_python'] = True
            if f.endswith(('.js', '.jsx', '.ts', '.tsx', '.mjs')):
                info['has_js_ts'] = True
            if f.endswith('.go'):
                info['has_go'] = True
            if f.endswith('.rs'):
                info['has_rust'] = True
            if f.endswith('.sol'):
                info['has_solidity'] = True
            if f.endswith(('.html', '.htm')):
                info['has_html'] = True
            if f.endswith('.css'):
                info['has_css'] = True

        for dp, dn, fn in os.walk(repo_path):
            if '.git' in dp.split(os.sep):
                continue
            for d in dn:
                if d in ('tests', 'test', 'spec', '__tests__', 'testing'):
                    info['has_tests'] = True
                    break
            if info['has_tests']:
                break
            for f in fn:
                if re.match(r'^test_.*\.py$', f) or re.match(r'^.*_test\.(py|js|ts)$', f) or f.endswith('.spec.ts'):
                    info['has_tests'] = True
                    break

        langs = []
        if info['has_python'] or info['has_requirements'] or info['has_pyproject']:
            langs.append('Python')
        if info['has_js_ts'] or info['has_package_json']:
            langs.append('JS/TS')
        if info['has_go'] or info['has_go_mod']:
            langs.append('Go')
        if info['has_rust'] or info['has_cargo']:
            langs.append('Rust')
        if info['has_solidity']:
            langs.append('Solidity')
        if info['has_html']:
            langs.append('HTML')
        if info['has_composer']:
            langs.append('PHP')
        if not langs:
            langs.append('Unknown')
        info['languages'] = langs

        for pattern in CLONE_INDICATORS:
            if re.search(pattern, repo_name, re.IGNORECASE):
                info['is_likely_clone'] = True
                info['clone_type'] = pattern
                break

        score = 0
        if info['has_readme']:
            score += 10
            if info['readme_length'] > 500:
                score += 5
            if info['readme_length'] > 2000:
                score += 5
        if info['has_license']:
            score += 10
        if info['has_git']:
            score += 5
        if info['has_gitignore']:
            score += 5
        if info['has_dockerfile']:
            score += 10
        if info['has_docker_compose']:
            score += 5
        if info['has_tests']:
            score += 15
        if info['has_ci']:
            score += 10
        if info['has_makefile']:
            score += 3
        if info['file_count'] > 10:
            score += 5
        if info['file_count'] > 50:
            score += 5
        if info['file_count'] > 200:
            score += 5
        if info['readme_length'] > 100:
            score += 3
        if info['has_requirements'] or info['has_package_json'] or info['has_pyproject']:
            score += 10
        if info['has_go_mod'] or info['has_cargo']:
            score += 5
        if info['description']:
            score += 5
        if info['is_likely_clone']:
            score -= 20
        if info['file_count'] == 0:
            score = 0
        if info['size_mb'] < 0.01 and info['file_count'] < 3:
            score = max(0, score - 30)

        if 'v0-' in repo_name or re.match(r'^\w-\d+$', repo_name):
            score = max(0, score - 10)

        info['score'] = max(0, score)

        if info['score'] >= 50:
            info['tier'] = 'A'
        elif info['score'] >= 25:
            info['tier'] = 'B'
        else:
            info['tier'] = 'C'

        return info
    except Exception as e:
        info['error'] = str(e)
        info['tier'] = 'C'
        info['score'] = 0
        return info


def main():
    print("=" * 60)
    print("AGENTFORGE - PHASE 1: REPO SCANNER")
    print("=" * 60)
    print(f"Scanning: {REPOS_DIR}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    all_repos = sorted(os.listdir(REPOS_DIR))
    results = []
    errors = []
    count = 0
    total = len(all_repos)

    for repo_name in all_repos:
        repo_path = os.path.join(REPOS_DIR, repo_name)
        if not os.path.isdir(repo_path):
            continue
        if repo_name.startswith('_'):
            continue

        count += 1
        if count % 50 == 0:
            print(f"  Progress: {count}/{total} ({count * 100 // total}%)")

        info = scan_repo(repo_name, repo_path)
        if info:
            results.append(info)
            if info.get('error'):
                errors.append(info)

    a_tier = [r for r in results if r['tier'] == 'A']
    b_tier = [r for r in results if r['tier'] == 'B']
    c_tier = [r for r in results if r['tier'] == 'C']
    clones = [r for r in results if r['is_likely_clone']]

    total_size = sum(r['size_mb'] for r in results)
    total_files = sum(r['file_count'] for r in results)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'scan_date': datetime.now().isoformat(),
            'total_repos': len(results),
            'total_size_mb': round(total_size, 1),
            'total_files': total_files,
            'summary': {
                'a_tier': len(a_tier),
                'b_tier': len(b_tier),
                'c_tier': len(c_tier),
                'clones': len(clones),
                'with_readme': sum(1 for r in results if r['has_readme']),
                'with_license': sum(1 for r in results if r['has_license']),
                'with_tests': sum(1 for r in results if r['has_tests']),
                'with_docker': sum(1 for r in results if r['has_dockerfile']),
                'with_docker_compose': sum(1 for r in results if r['has_docker_compose']),
                'with_ci': sum(1 for r in results if r['has_ci']),
                'with_git': sum(1 for r in results if r['has_git']),
                'with_requirements': sum(1 for r in results if r['has_requirements']),
                'with_package_json': sum(1 for r in results if r['has_package_json']),
            },
            'repos': results,
        }, f, indent=2)

    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write("# REPO CLASSIFICATION REPORT\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Scanned:** {len(results)}\n\n")
        f.write("## Summary\n\n")
        f.write(f"| Tier | Count | Description |\n")
        f.write(f"|------|-------|-------------|\n")
        f.write(f"| **A** | {len(a_tier)} | Deep-work worthy (scored 50+) |\n")
        f.write(f"| **B** | {len(b_tier)} | Light fixes needed |\n")
        f.write(f"| **C** | {len(c_tier)} | Leave as-is / clones |\n")
        f.write(f"| Clones | {len(clones)} | Likely duplicate/clone repos |\n\n")
        f.write("## Quality Metrics\n\n")
        f.write(f"| Metric | Count | Pct |\n")
        f.write(f"|--------|-------|-----|\n")
        s = {k: v for k, v in json.load(open(OUTPUT_FILE))['summary'].items() if k != 'total_repos'}
        for k, v in s.items():
            f.write(f"| {k} | {v} | {v * 100 // len(results)}% |\n")
        f.write(f"\n## A-Tier Repos ({len(a_tier)})\n\n")
        f.write("| # | Repo | Size | Files | Score | Lang | README | Tests | Docker |\n")
        f.write("|---|------|------|-------|-------|------|--------|-------|--------|\n")
        for i, r in enumerate(sorted(a_tier, key=lambda x: -x['score']), 1):
            f.write(f"| {i} | {r['name']} | {r['size_mb']}MB | {r['file_count']} | {r['score']} | {','.join(r['languages'])} | {'Y' if r['has_readme'] else ''} | {'Y' if r['has_tests'] else ''} | {'Y' if r['has_dockerfile'] else ''} |\n")

        f.write(f"\n## B-Tier Repos ({len(b_tier)})\n\n")
        f.write("| # | Repo | Size | Files | Score | Lang | README |\n")
        f.write("|---|------|------|-------|-------|------|--------|\n")
        for i, r in enumerate(sorted(b_tier, key=lambda x: -x['score']), 1):
            f.write(f"| {i} | {r['name']} | {r['size_mb']}MB | {r['file_count']} | {r['score']} | {','.join(r['languages'])} | {'Y' if r['has_readme'] else ''} |\n")

    print()
    print("=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)
    print(f"Total repos scanned: {len(results)}")
    print(f"Total size: {total_size:.0f} MB ({total_size / 1024:.1f} GB)")
    print(f"Total files: {total_files:,}")
    print(f"A-Tier (deep work): {len(a_tier)}")
    print(f"B-Tier (light fixes): {len(b_tier)}")
    print(f"C-Tier (leave as-is): {len(c_tier)}")
    print(f"Likely clones: {len(clones)}")
    print(f"\nWith README: {sum(1 for r in results if r['has_readme'])}")
    print(f"With LICENSE: {sum(1 for r in results if r['has_license'])}")
    print(f"With Tests: {sum(1 for r in results if r['has_tests'])}")
    print(f"With Dockerfile: {sum(1 for r in results if r['has_dockerfile'])}")
    print(f"With CI/CD: {sum(1 for r in results if r['has_ci'])}")
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"Summary: {SUMMARY_FILE}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors[:10]:
            print(f"  - {e['name']}: {e['error']}")


if __name__ == '__main__':
    main()
