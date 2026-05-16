"""
GitHub Repo Downloader - Enhanced Features Module v2.1.0
Adds batch download, verification, stats, progress bars, env config
"""
import os
import json
import csv
import sys
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


def download_from_file(file_path: str, output_dir: str, token: str = None,
                       method: str = "git", max_concurrent: int = 3):
    """Download multiple repos from a file (one URL or owner/repo per line)"""
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return

    from .downloader import GitRepoDownloader, BatchDownloader, DownloadMethod

    method_map = {
        'git': DownloadMethod.GIT_CLONE,
        'zip': DownloadMethod.DOWNLOAD_ZIP,
        'tar': DownloadMethod.DOWNLOAD_TAR,
    }
    dl_method = method_map.get(method, DownloadMethod.GIT_CLONE)

    urls = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)

    print(f"Loaded {len(urls)} repos from {file_path}")
    downloader = GitRepoDownloader(token=token)
    batch = BatchDownloader(max_workers=max_concurrent)

    repo_list = [{'url': url, 'branch': 'main'} for url in urls]
    results = batch.download_multiple(repo_list, output_dir, dl_method)

    success = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    print(f"Done: {success} succeeded, {failed} failed")
    return results


def verify_download(repo_path: str) -> Dict:
    """Verify a downloaded repository's integrity"""
    info = {
        'path': repo_path,
        'exists': os.path.exists(repo_path),
        'file_count': 0,
        'total_size_mb': 0,
        'has_readme': False,
        'has_git': False,
        'has_license': False,
        'is_valid': False,
        'issues': [],
    }
    if not info['exists']:
        info['issues'].append('Path does not exist')
        return info

    try:
        info['has_git'] = os.path.isdir(os.path.join(repo_path, '.git'))
        top = os.listdir(repo_path)

        if not top:
            info['issues'].append('Empty directory')
            return info

        info['has_readme'] = any(f.lower().startswith('readme') for f in top)
        info['has_license'] = any(f.lower().startswith('license') for f in top)

        total_size = 0
        file_count = 0
        for dp, dn, fn in os.walk(repo_path):
            if '.git' in dp.split(os.sep):
                continue
            for f in fn:
                try:
                    total_size += os.path.getsize(os.path.join(dp, f))
                    file_count += 1
                except (OSError, PermissionError):
                    pass

        info['file_count'] = file_count
        info['total_size_mb'] = round(total_size / 1024 / 1024, 1)

        if file_count == 0:
            info['issues'].append('No files found')
        if not info['has_readme']:
            info['issues'].append('No README')
        if not info['has_git'] and file_count < 5:
            info['issues'].append('Sparse download (no .git, few files)')

        info['is_valid'] = len(info['issues']) == 0 or file_count > 0
    except Exception as e:
        info['issues'].append(str(e))

    return info


def verify_all_downloads(repos_dir: str, output_file: str = None):
    """Verify all downloaded repos and generate report"""
    print(f"Verifying downloads in: {repos_dir}")
    results = []
    total = 0
    valid = 0
    issues_found = 0

    for repo_name in sorted(os.listdir(repos_dir)):
        repo_path = os.path.join(repos_dir, repo_name)
        if not os.path.isdir(repo_path) or repo_name.startswith('_'):
            continue
        total += 1
        info = verify_download(repo_path)
        info['name'] = repo_name
        results.append(info)
        if info['is_valid']:
            valid += 1
        if info['issues']:
            issues_found += 1

    report = {
        'scan_date': datetime.now().isoformat(),
        'total_repos': total,
        'valid_repos': valid,
        'repos_with_issues': issues_found,
        'total_size_mb': round(sum(r['total_size_mb'] for r in results), 1),
        'total_files': sum(r['file_count'] for r in results),
        'results': results,
    }

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {output_file}")

    print(f"\nVerification complete:")
    print(f"  Total repos: {total}")
    print(f"  Valid: {valid}")
    print(f"  With issues: {issues_found}")
    print(f"  Total size: {report['total_size_mb']} MB")
    print(f"  Total files: {report['total_files']:,}")
    return report


def export_metadata(repos_dir: str, output_file: str, format: str = 'json'):
    """Export repo metadata to JSON or CSV"""
    repos = []
    for repo_name in sorted(os.listdir(repos_dir)):
        repo_path = os.path.join(repos_dir, repo_name)
        if not os.path.isdir(repo_path) or repo_name.startswith('_'):
            continue

        info = {
            'name': repo_name,
            'size_mb': 0,
            'file_count': 0,
            'has_readme': False,
            'has_license': False,
            'has_git': os.path.isdir(os.path.join(repo_path, '.git')),
            'has_docker': os.path.exists(os.path.join(repo_path, 'Dockerfile')),
        }
        try:
            top = os.listdir(repo_path)
            info['has_readme'] = any(f.lower().startswith('readme') for f in top)
            info['has_license'] = any(f.lower().startswith('license') for f in top)

            total_size = 0
            file_count = 0
            for dp, dn, fn in os.walk(repo_path):
                if '.git' in dp.split(os.sep):
                    continue
                for f in fn:
                    try:
                        total_size += os.path.getsize(os.path.join(dp, f))
                        file_count += 1
                    except (OSError, PermissionError):
                        pass
            info['size_mb'] = round(total_size / 1024 / 1024, 1)
            info['file_count'] = file_count
        except Exception:
            pass
        repos.append(info)

    if format == 'csv':
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=repos[0].keys())
            writer.writeheader()
            writer.writerows(repos)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(repos, f, indent=2)

    print(f"Exported {len(repos)} repos to {output_file}")
    return repos


def load_config_from_env() -> Dict:
    """Load configuration from environment variables"""
    config = {}
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        config['token'] = token

    output = os.environ.get('GITHUB_DOWNLOAD_DIR')
    if output:
        config['output_dir'] = output

    max_conc = os.environ.get('GITHUB_MAX_CONCURRENT')
    if max_conc:
        try:
            config['max_concurrent'] = int(max_conc)
        except ValueError:
            pass

    method = os.environ.get('GITHUB_DOWNLOAD_METHOD', 'git')
    if method in ('git', 'zip', 'tar'):
        config['method'] = method

    config_file = os.environ.get('GITHUB_CONFIG_FILE')
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config['config'] = json.load(f)

    return config


def setup_package():
    """Generate pyproject.toml for the downloader"""
    return """[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "github-repo-downloader"
version = "2.1.0"
description = "Download GitHub repositories with GUI, CLI, and batch support"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
dependencies = [
    "requests>=2.31.0",
    "PyGithub>=1.59.0",
    "gitpython>=3.1.40",
    "cryptography>=41.0.0",
]
optional-dependencies = {
    "gui": ["PyQt6>=6.6.0"],
    "webhook": ["flask>=2.0.0"],
    "all": ["PyQt6>=6.6.0", "flask>=2.0.0"],
}

[project.urls]
Homepage = "https://github.com/agentforge/github-downloader"

[project.scripts]
github-downloader = "github_downloader.__main__:main"
"""


class ProgressBar:
    """Simple CLI progress bar"""
    def __init__(self, total: int, prefix: str = '', width: int = 50):
        self.total = total
        self.prefix = prefix
        self.width = width
        self.start_time = time.time()

    def update(self, current: int):
        elapsed = time.time() - self.start_time
        pct = current / self.total if self.total > 0 else 0
        filled = int(self.width * pct)
        bar = '█' * filled + '░' * (self.width - filled)
        eta = elapsed / pct - elapsed if pct > 0 else 0
        sys.stdout.write(f'\r{self.prefix} |{bar}| {pct*100:5.1f}%  ETA: {eta:5.1f}s')
        sys.stdout.flush()
        if current >= self.total:
            print()


def check_downloader_health(repos_dir: str) -> Dict:
    """Health check of the downloader system"""
    health = {
        'status': 'unknown',
        'repos_dir': repos_dir,
        'dir_exists': os.path.exists(repos_dir),
        'disk_free_gb': 0,
        'total_repos': 0,
        'empty_repos': 0,
        'corrupt_repos': 0,
        'largest_repo_mb': 0,
        'oldest_repo_days': 0,
    }

    if health['dir_exists']:
        import shutil
        total, used, free = shutil.disk_usage(repos_dir)
        health['disk_free_gb'] = round(free / (1024**3), 1)

        now = time.time()
        for repo_name in os.listdir(repos_dir):
            repo_path = os.path.join(repos_dir, repo_name)
            if not os.path.isdir(repo_path) or repo_name.startswith('_'):
                continue
            health['total_repos'] += 1

            try:
                top = os.listdir(repo_path)
                if not top:
                    health['empty_repos'] += 1
                    continue

                total_size = 0
                for dp, dn, fn in os.walk(repo_path):
                    if '.git' in dp.split(os.sep):
                        continue
                    for f in fn:
                        try:
                            total_size += os.path.getsize(os.path.join(dp, f))
                        except (OSError, PermissionError):
                            pass
                size_mb = total_size / 1024 / 1024
                if size_mb > health['largest_repo_mb']:
                    health['largest_repo_mb'] = round(size_mb, 1)

                mtime = os.path.getmtime(repo_path)
                age_days = (now - mtime) / 86400
                if age_days > health['oldest_repo_days']:
                    health['oldest_repo_days'] = int(age_days)

            except Exception:
                health['corrupt_repos'] += 1

        health['status'] = 'healthy'

    return health
