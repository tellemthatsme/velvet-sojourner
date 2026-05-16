"""
Step 2: Master Repo Directory + Git Update Check + Missing Docs Generator
"""
import os
import json
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

REPOS_DIR = r'C:\temp\velvet-sojourner\repos'
MASTER_INDEX = r'C:\temp\velvet-sojourner\MASTER_REPO_DIRECTORY.md'
GIT_STATUS_FILE = r'C:\temp\velvet-sojourner\GIT_UPDATE_STATUS.md'
DOCS_OUT_DIR = r'C:\temp\velvet-sojourner\docs\repo-docs'
os.makedirs(DOCS_OUT_DIR, exist_ok=True)


def check_git_updates(repo_name, repo_path):
    """Check if a git repo has updates available"""
    result = {
        'name': repo_name,
        'has_remote': False,
        'behind_count': 0,
        'ahead_count': 0,
        'has_uncommitted': False,
        'last_fetch': '',
        'error': '',
        'remote_url': '',
    }

    git_dir = os.path.join(repo_path, '.git')
    if not os.path.isdir(git_dir):
        result['error'] = 'not a git repo'
        return result

    try:
        remote = subprocess.run(
            ['git', 'remote', '-v'],
            capture_output=True, text=True, timeout=15,
            cwd=repo_path
        )
        if remote.returncode == 0 and remote.stdout.strip():
            result['has_remote'] = True
            urls = [l.split()[1] for l in remote.stdout.strip().split('\n') if l]
            if urls:
                result['remote_url'] = urls[0]

        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, timeout=15,
            cwd=repo_path
        )
        if status.returncode == 0:
            result['has_uncommitted'] = bool(status.stdout.strip())

        fetch = subprocess.run(
            ['git', 'remote', 'update'],
            capture_output=True, text=True, timeout=30,
            cwd=repo_path
        )

        revlist = subprocess.run(
            ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'],
            capture_output=True, text=True, timeout=15,
            cwd=repo_path
        )
        if revlist.returncode == 0 and revlist.stdout.strip():
            parts = revlist.stdout.strip().split()
            if len(parts) >= 2:
                result['ahead_count'] = int(parts[0])
                result['behind_count'] = int(parts[1])

    except subprocess.TimeoutExpired:
        result['error'] = 'timeout'
    except Exception as e:
        result['error'] = str(e)

    return result


def generate_doc_for_repo(repo_name, repo_info):
    """Generate a documentation file for a repo"""
    name_clean = repo_name.replace('/', '-').replace('\\', '-')
    doc_path = os.path.join(DOCS_OUT_DIR, f"{name_clean}.md")

    if os.path.exists(doc_path):
        return False

    desc = repo_info.get('description', '') or repo_name
    langs = ', '.join(repo_info.get('languages', ['Unknown']))
    readme_q = repo_info.get('readme_quality', 'unknown')

    content = f"""# {repo_name}

## Overview

{desc}

## Details

| Field | Value |
|-------|-------|
| Name | {repo_name} |
| Languages | {langs} |
| README Quality | {readme_q} |
| Size | {repo_info.get('size_mb', '?')} MB |
| Files | {repo_info.get('file_count', '?')} |
| Has Tests | {'Yes' if repo_info.get('has_tests', False) else 'No'} |
| Has Dockerfile | {'Yes' if repo_info.get('has_dockerfile', False) else 'No'} |
| Has License | {'Yes' if repo_info.get('has_license', False) else 'No'} |
| Tier | {repo_info.get('tier', 'C')} |

## Contents

This repository is part of the AgentForge curated collection.

## Usage

See the README in the repository for usage instructions.

## Related Repos

- [Back to Index](../MASTER_REPO_DIRECTORY.md)
"""

    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def main():
    print("Loading scan data...")
    scan_file = os.path.join(REPOS_DIR, '_SCAN_ALL_RESULTS.json')
    if os.path.exists(scan_file):
        with open(scan_file, 'r', encoding='utf-8') as f:
            scan_data = json.load(f)['repos']
    else:
        scan_data = []

    repo_map = {r['name']: r for r in scan_data}

    print("Loading docs inventory...")
    docs_file = os.path.join(REPOS_DIR, '_DOCS_INVENTORY.json')
    if os.path.exists(docs_file):
        with open(docs_file, 'r', encoding='utf-8') as f:
            docs_data = json.load(f)['all_repos']
    else:
        docs_data = []

    docs_map = {r['name']: r for r in docs_data}

    print("Scanning repos and checking git status...")
    all_repos = sorted(os.listdir(REPOS_DIR))
    repo_list = [r for r in all_repos if os.path.isdir(os.path.join(REPOS_DIR, r)) and not r.startswith('_')]

    git_results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for repo_name in repo_list:
            repo_path = os.path.join(REPOS_DIR, repo_name)
            future = executor.submit(check_git_updates, repo_name, repo_path)
            futures[future] = repo_name

        for i, future in enumerate(as_completed(futures)):
            repo_name = futures[future]
            try:
                git_results[repo_name] = future.result()
            except Exception as e:
                git_results[repo_name] = {'name': repo_name, 'error': str(e)}
            if (i + 1) % 100 == 0:
                print(f"  Git check: {i+1}/{len(repo_list)}")

    repos_with_remotes = [r for r in git_results.values() if r.get('has_remote')]
    repos_behind = [r for r in git_results.values() if r.get('behind_count', 0) > 0]
    repos_ahead = [r for r in git_results.values() if r.get('ahead_count', 0) > 0]
    repos_uncommitted = [r for r in git_results.values() if r.get('has_uncommitted')]
    repos_no_git = [r for r in git_results.values() if r.get('error') == 'not a git repo']

    print("\nGenerating missing docs...")
    docs_generated = 0
    for repo_name in repo_list:
        info = repo_map.get(repo_name, {})
        if generate_doc_for_repo(repo_name, info):
            docs_generated += 1

    print("\nGenerating master directory...")
    tier_map = {}
    for r in scan_data:
        t = r.get('tier', 'C')
        tier_map.setdefault(t, []).append(r)

    with open(MASTER_INDEX, 'w', encoding='utf-8') as f:
        f.write("# AgentForge — Master Repo Directory\n\n")
        f.write(f"**Total repos:** {len(repo_list)}\n")
        f.write(f"**Total size:** {sum(r.get('size_mb', 0) for r in scan_data):.0f} MB ({sum(r.get('size_mb', 0) for r in scan_data)/1024:.1f} GB)\n")
        f.write(f"**Total files:** {sum(r.get('file_count', 0) for r in scan_data):,}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Quick Stats\n\n")
        f.write(f"| Category | Count |\n")
        f.write(f"|----------|-------|\n")
        f.write(f"| A-Tier (high quality) | {len(tier_map.get('A', []))} |\n")
        f.write(f"| B-Tier (medium quality) | {len(tier_map.get('B', []))} |\n")
        f.write(f"| C-Tier (basic) | {len(tier_map.get('C', []))} |\n")
        f.write(f"| With docs/ directory | {len([r for r in docs_data if r.get('has_docs_dir')])} |\n")
        f.write(f"| With remote (GitHub) | {len(repos_with_remotes)} |\n")
        f.write(f"| Behind remote (needs pull) | {len(repos_behind)} |\n")
        f.write(f"| Ahead of remote (unpushed) | {len(repos_ahead)} |\n")
        f.write(f"| Uncommitted changes | {len(repos_uncommitted)} |\n")
        f.write(f"| Not a git repo | {len(repos_no_git)} |\n\n")

        for tier in ['A', 'B', 'C']:
            repos_in_tier = sorted(tier_map.get(tier, []), key=lambda x: -x.get('score', 0))

            f.write(f"---\n\n## {tier}-Tier Repos ({len(repos_in_tier)})\n\n")
            f.write("| # | Repo | Size | Files | Score | Lang | README | Docs | License | Docker | Tests | Updated |\n")
            f.write("|---|------|------|-------|-------|------|--------|------|---------|--------|-------|---------|\n")

            for i, r in enumerate(repos_in_tier, 1):
                name = r['name']
                size = r.get('size_mb', 0)
                files = r.get('file_count', 0)
                score = r.get('score', 0)
                langs = ','.join(r.get('languages', ['?']))
                readme_q = docs_map.get(name, {}).get('readme_quality', '?')
                has_docs = 'Y' if docs_map.get(name, {}).get('has_docs_dir') else ('R' if readme_q != 'none' else '')
                has_license = 'Y' if r.get('has_license') else ''
                has_docker = 'Y' if r.get('has_dockerfile') else ''
                has_tests = 'Y' if r.get('has_tests') else ''

                gi = git_results.get(name, {})
                if gi.get('behind_count', 0) > 0:
                    updated = f"⚠ behind {gi['behind_count']}"
                elif gi.get('has_uncommitted'):
                    updated = '⚠ dirty'
                elif gi.get('ahead_count', 0) > 0:
                    updated = f"⚠ ahead {gi['ahead_count']}"
                elif gi.get('has_remote'):
                    updated = 'ok'
                elif gi.get('error') == 'not a git repo':
                    updated = 'no git'
                else:
                    updated = 'no remote'

                f.write(f"| {i} | [{name}](repo-docs/{name}.md) | {size}MB | {files} | {score} | {langs[:20]} | {readme_q[:8]} | {has_docs} | {has_license} | {has_docker} | {has_tests} | {updated} |\n")

    print("\nGenerating git update status...")
    with open(GIT_STATUS_FILE, 'w', encoding='utf-8') as f:
        f.write("# Git Update Status Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total repos:** {len(repo_list)}\n\n")

        f.write("## Summary\n\n")
        f.write(f"| Status | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Repos with remote | {len(repos_with_remotes)} |\n")
        f.write(f"| Behind remote (needs `git pull`) | {len(repos_behind)} |\n")
        f.write(f"| Ahead of remote (needs `git push`) | {len(repos_ahead)} |\n")
        f.write(f"| Uncommitted changes | {len(repos_uncommitted)} |\n")
        f.write(f"| Not a git repo | {len(repos_no_git)} |\n")
        f.write(f"| No remote configured | {len(repo_list) - len(repos_with_remotes)} |\n\n")

        if repos_behind:
            f.write("## Repos Behind Remote (NEED `git pull`)\n\n")
            f.write("| # | Repo | Behind Count | Ahead Count | Remote URL |\n")
            f.write("|---|------|-------------|-------------|------------|\n")
            for i, r in enumerate(sorted(repos_behind, key=lambda x: -x['behind_count']), 1):
                f.write(f"| {i} | {r['name']} | {r['behind_count']} | {r['ahead_count']} | {r.get('remote_url', '')[:60]} |\n")

        if repos_ahead:
            f.write("\n## Repos Ahead of Remote (NEED `git push`)\n\n")
            f.write("| # | Repo | Ahead Count | Remote URL |\n")
            f.write("|---|------|-------------|------------|\n")
            for i, r in enumerate(sorted(repos_ahead, key=lambda x: -x['ahead_count']), 1):
                f.write(f"| {i} | {r['name']} | {r['ahead_count']} | {r.get('remote_url', '')[:60]} |\n")

        if repos_uncommitted:
            f.write("\n## Repos With Uncommitted Changes\n\n")
            for r in sorted(repos_uncommitted, key=lambda x: x['name']):
                f.write(f"- {r['name']}\n")

    print(f"\n{'='*60}")
    print(f"ALL COMPLETE")
    print(f"{'='*60}")
    print(f"Master directory: {MASTER_INDEX}")
    print(f"Git status: {GIT_STATUS_FILE}")
    print(f"Missing docs generated: {docs_generated}")
    print(f"Total docs in repo-docs/: {len(os.listdir(DOCS_OUT_DIR))}")
    print(f"\nGit Summary:")
    print(f"  Repos with remotes: {len(repos_with_remotes)}")
    print(f"  Need git pull: {len(repos_behind)}")
    print(f"  Need git push: {len(repos_ahead)}")
    print(f"  Uncommitted changes: {len(repos_uncommitted)}")
    print(f"  Not git repos: {len(repos_no_git)}")


if __name__ == '__main__':
    main()
