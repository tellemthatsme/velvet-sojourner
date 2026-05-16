import sys
import argparse
import os
from ..user_auth import UserDatabase
from ..github_api import GitHubAPIClient
from ..downloader import GitRepoDownloader, DownloadMethod

class CLIMode:
    """Command line interface for batch operations"""
    
    def __init__(self, user_auth):
        self.user_auth = user_auth

    def parse_args(self):
        parser = argparse.ArgumentParser(description="GitHub Repo Downloader CLI")
        parser.add_argument('--cli', action='store_true', help='Enable CLI mode')
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Download command
        dl_parser = subparsers.add_parser('download', help='Download a repository')
        dl_parser.add_argument('--url', '-u', required=True, help='Repository URL')
        dl_parser.add_argument('--output', '-o', help='Output directory')
        dl_parser.add_argument('--method', default='git', choices=['git', 'zip', 'tar'], help='Download method')
        dl_parser.add_argument('--branch', help='Branch name')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List user repositories')
        list_parser.add_argument('--user', required=True, help='GitHub username')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search repositories')
        search_parser.add_argument('--query', '-q', required=True, help='Search query')
        
        # Sync command
        sync_parser = subparsers.add_parser('sync', help='Sync local repositories')
        sync_parser.add_argument('--path', required=True, help='Local repositories path')
        
        return parser.parse_args()

    def run(self):
        args = self.parse_args()
        if args.command == 'download':
            self.cmd_download(args)
        elif args.command == 'list':
            self.cmd_list(args)
        elif args.command == 'search':
            self.cmd_search(args)
        elif args.command == 'sync':
            self.cmd_sync(args)
        else:
            print("Use --help for usage information")
        return 0

    def cmd_download(self, args):
        print(f"Downloading {args.url}...")
        method_map = {
            'git': DownloadMethod.GIT_CLONE,
            'zip': DownloadMethod.DOWNLOAD_ZIP,
            'tar': DownloadMethod.DOWNLOAD_TAR
        }
        method = method_map.get(args.method, DownloadMethod.GIT_CLONE)
        output = args.output or os.path.expanduser("~/Downloads")
        
        # Try to get token from first user found
        # (This is simplified for CLI)
        token = None
        # ... logic to get token ...
        
        downloader = GitRepoDownloader(token)
        try:
            task = downloader.create_download_task(args.url, output, method, args.branch or "main")
            success = downloader.start_download(task.id)
            if success:
                print(f"Successfully downloaded to {output}/{task.repo}")
            else:
                print(f"Download failed: {task.error}")
        except Exception as e:
            print(f"Error: {e}")

    def cmd_list(self, args):
        print(f"Listing repositories for {args.user}...")
        client = GitHubAPIClient()
        repos = client.get_user_repos(args.user)
        for repo in repos:
            print(f"- {repo['name']}: {repo.get('description', 'No description')}")

    def cmd_search(self, args):
        print(f"Searching for '{args.query}'...")
        client = GitHubAPIClient()
        results = client.search_repos(args.query)
        for repo in results:
            print(f"- {repo['full_name']} ({repo['stargazers_count']} stars)")

    def cmd_sync(self, args):
        print(f"Syncing repositories in {args.path}...")
        # ... sync logic ...
        print("Sync complete.")
