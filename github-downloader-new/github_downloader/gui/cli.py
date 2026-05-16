"""
Enhanced CLI Mode - v2.1.0
Adds batch, verify, export, health, config commands
"""
import sys
import argparse
import os
from ..user_auth import UserDatabase
from ..github_api import GitHubAPIClient
from ..downloader import GitRepoDownloader, DownloadMethod
from ..enhancements import (
    download_from_file, verify_download, verify_all_downloads,
    export_metadata, load_config_from_env, check_downloader_health,
    ProgressBar
)


class CLIMode:
    """Enhanced command line interface"""

    def __init__(self, user_auth):
        self.user_auth = user_auth

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="GitHub Repo Downloader CLI v2.1.0",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  download a single repo:
    github-downloader download --url owner/repo --output ./downloads

  batch download from file:
    github-downloader batch --file repos.txt --output ./downloads

  verify all downloads:
    github-downloader verify --path ./downloads

  export metadata:
    github-downloader export --path ./downloads --format csv --output report.csv

  health check:
    github-downloader health --path ./downloads

  load config from env:
    export GITHUB_TOKEN=ghp_xxx
    export GITHUB_DOWNLOAD_DIR=./downloads
    github-downloader download --url owner/repo
            """
        )
        parser.add_argument('--json', action='store_true', help='JSON output')

        subparsers = parser.add_subparsers(dest='command', help='Commands')

        # Download
        dl = subparsers.add_parser('download', help='Download a repository')
        dl.add_argument('--url', '-u', required=True, help='Repository URL (owner/repo)')
        dl.add_argument('--output', '-o', help='Output directory')
        dl.add_argument('--method', default='git', choices=['git', 'zip', 'tar'], help='Download method')
        dl.add_argument('--branch', default='main', help='Branch name')
        dl.add_argument('--token', help='GitHub token (or set GITHUB_TOKEN env)')

        # Batch
        bt = subparsers.add_parser('batch', help='Batch download from file')
        bt.add_argument('--file', '-f', required=True, help='File with repo URLs (one per line)')
        bt.add_argument('--output', '-o', default='./downloads', help='Output directory')
        bt.add_argument('--method', default='git', choices=['git', 'zip', 'tar'], help='Download method')
        bt.add_argument('--concurrent', type=int, default=3, help='Max concurrent downloads')
        bt.add_argument('--token', help='GitHub token')

        # Verify
        vr = subparsers.add_parser('verify', help='Verify downloaded repos')
        vr.add_argument('--path', required=True, help='Repositories directory')
        vr.add_argument('--repo', help='Specific repo to verify')
        vr.add_argument('--output', help='Save verification report to JSON file')

        # Export
        ex = subparsers.add_parser('export', help='Export repo metadata')
        ex.add_argument('--path', required=True, help='Repositories directory')
        ex.add_argument('--format', default='json', choices=['json', 'csv'], help='Export format')
        ex.add_argument('--output', '-o', required=True, help='Output file')

        # Health
        hl = subparsers.add_parser('health', help='Downloader health check')
        hl.add_argument('--path', default='./repos', help='Repositories directory')

        # Config
        cf = subparsers.add_parser('config', help='Show environment config')
        cf.add_argument('--show', action='store_true', help='Show current config')

        # List
        ls = subparsers.add_parser('list', help='List user repos from GitHub')
        ls.add_argument('--user', required=True, help='GitHub username')
        ls.add_argument('--token', help='GitHub token')

        # Search
        sh = subparsers.add_parser('search', help='Search GitHub repos')
        sh.add_argument('--query', '-q', required=True, help='Search query')
        sh.add_argument('--token', help='GitHub token')

        return parser.parse_args()

    def run(self):
        args = self.parse_args()
        env_config = load_config_from_env()

        # Merge env config into args
        if not getattr(args, 'token', None) and 'token' in env_config:
            args.token = env_config['token']
        if not getattr(args, 'output', None) and 'output_dir' in env_config:
            args.output = env_config['output_dir']

        commands = {
            'download': self.cmd_download,
            'batch': self.cmd_batch,
            'verify': self.cmd_verify,
            'export': self.cmd_export,
            'health': self.cmd_health,
            'config': self.cmd_config,
            'list': self.cmd_list,
            'search': self.cmd_search,
        }

        handler = commands.get(args.command)
        if handler:
            result = handler(args)
            if args.json and result:
                import json
                print(json.dumps(result, indent=2, default=str))
        else:
            print("Use --help for usage information")
        return 0

    def cmd_download(self, args):
        from ..downloader import DownloadMethod
        method_map = {
            'git': DownloadMethod.GIT_CLONE,
            'zip': DownloadMethod.DOWNLOAD_ZIP,
            'tar': DownloadMethod.DOWNLOAD_TAR,
        }
        method = method_map.get(args.method, DownloadMethod.GIT_CLONE)
        output = args.output or os.path.expanduser("~/Downloads")

        downloader = GitRepoDownloader(args.token)
        try:
            task = downloader.create_download_task(args.url, output, method, args.branch)
            print(f"Downloading {args.url} to {output}...")
            success = downloader.start_download(task.id)

            result = {
                'url': args.url,
                'output': os.path.join(output, task.repo),
                'success': success,
                'method': args.method,
                'file_count': task.files_downloaded,
            }

            if success:
                print(f"  OK: Downloaded to {output}/{task.repo}")
            else:
                result['error'] = task.error
                print(f"  FAILED: {task.error}")

            return result
        except Exception as e:
            print(f"Error: {e}")
            return {'error': str(e)}

    def cmd_batch(self, args):
        from ..downloader import DownloadMethod
        method_map = {
            'git': DownloadMethod.GIT_CLONE,
            'zip': DownloadMethod.DOWNLOAD_ZIP,
            'tar': DownloadMethod.DOWNLOAD_TAR,
        }
        output = args.output or './downloads'
        os.makedirs(output, exist_ok=True)

        results = download_from_file(
            file_path=args.file,
            output_dir=output,
            token=args.token,
            method=args.method,
            max_concurrent=args.concurrent,
        )
        return results

    def cmd_verify(self, args):
        if args.repo:
            repo_path = os.path.join(args.path, args.repo)
            if not os.path.exists(repo_path):
                print(f"Repo not found: {repo_path}")
                return {'error': 'not found'}
            info = verify_download(repo_path)
            info['name'] = args.repo
            print(f"\nVerification for {args.repo}:")
            print(f"  Valid: {info['is_valid']}")
            print(f"  Files: {info['file_count']}")
            print(f"  Size: {info['total_size_mb']} MB")
            if info['has_readme']:
                print(f"  README: yes")
            if info['has_license']:
                print(f"  License: yes")
            if info['has_git']:
                print(f"  Git repo: yes")
            if info['issues']:
                print(f"  Issues: {', '.join(info['issues'])}")
            return info
        else:
            return verify_all_downloads(args.path, args.output)

    def cmd_export(self, args):
        return export_metadata(args.path, args.output, args.format)

    def cmd_health(self, args):
        health = check_downloader_health(args.path)
        print(f"\nDownloader Health Check:")
        print(f"  Status: {health['status']}")
        print(f"  Repos directory: {health['repos_dir']}")
        print(f"  Directory exists: {health['dir_exists']}")
        if health['dir_exists']:
            print(f"  Total repos: {health['total_repos']}")
            print(f"  Empty repos: {health['empty_repos']}")
            print(f"  Corrupt repos: {health['corrupt_repos']}")
            print(f"  Largest repo: {health['largest_repo_mb']} MB")
            print(f"  Oldest repo: {health['oldest_repo_days']} days")
            print(f"  Disk free: {health['disk_free_gb']} GB")
        return health

    def cmd_config(self, args):
        env_config = load_config_from_env()
        if args.show:
            print(f"\nEnvironment Configuration:")
            print(f"  GITHUB_TOKEN: {'SET' if 'token' in env_config else 'NOT SET'}")
            print(f"  GITHUB_DOWNLOAD_DIR: {env_config.get('output_dir', 'NOT SET')}")
            print(f"  GITHUB_MAX_CONCURRENT: {env_config.get('max_concurrent', 'NOT SET')}")
            print(f"  GITHUB_DOWNLOAD_METHOD: {env_config.get('method', 'NOT SET')}")
            print(f"  GITHUB_CONFIG_FILE: {'SET' if 'config' in env_config else 'NOT SET'}")
        return env_config

    def cmd_list(self, args):
        print(f"Repositories for {args.user}:")
        client = GitHubAPIClient(token=args.token)
        repos = client.get_user_repos(args.user)
        results = []
        for repo in repos:
            name = repo.get('name', '?')
            desc = repo.get('description', '') or ''
            stars = repo.get('stargazers_count', 0)
            print(f"  {name:40s} {'★' + str(stars):10s} {desc[:50]}")

            parsed = {
                'name': repo.get('name'),
                'full_name': repo.get('full_name'),
                'description': repo.get('description'),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language'),
                'url': repo.get('html_url'),
                'private': repo.get('private', False),
            }
            results.append(parsed)

        print(f"\nTotal: {len(repos)} repos")
        return results

    def cmd_search(self, args):
        print(f"Searching for: {args.query}")
        client = GitHubAPIClient(token=args.token)
        results = client.search_repos(args.query)
        for repo in results:
            name = repo.get('full_name', '?')
            stars = repo.get('stargazers_count', 0)
            desc = repo.get('description', '') or ''
            print(f"  {name:45s} {'★' + str(stars):10s} {desc[:50]}")
        print(f"\nTotal: {len(results)} results")
        return results
