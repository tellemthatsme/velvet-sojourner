import sys
import argparse
import os
from ..user_auth import UserDatabase
from ..github_api import GitHubAPIClient
from ..downloader import GitRepoDownloader, DownloadMethod, DownloadTask

class CLIMode:
    """Command line interface for GitHub Downloader with proper authentication"""
    
    def __init__(self, user_auth):
        self.user_auth = user_auth

    def parse_args(self):
        parser = argparse.ArgumentParser(description="GitHub Repo Downloader CLI")
        parser.add_argument('--cli', action='store_true', help='Enable CLI mode')
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Download command
        dl_parser = subparsers.add_parser('download', help='Download a repository')
        dl_parser.add_argument('--url', '-u', required=True, help='Repository URL (https://github.com/owner/repo or owner/repo)')
        dl_parser.add_argument('--output', '-o', help='Output directory (default: ~/Downloads)')
        dl_parser.add_argument('--method', default='git', choices=['git', 'zip', 'tar'], help='Download method')
        dl_parser.add_argument('--branch', help='Branch name (default: main)')
        dl_parser.add_argument('--token', '-t', help='GitHub Token (overrides saved accounts)')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List repositories')
        list_parser.add_argument('--user', help='GitHub username (default: authenticated user)')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search repositories')
        search_parser.add_argument('--query', '-q', required=True, help='Search query')
        
        # Sync command
        sync_parser = subparsers.add_parser('sync', help='Sync local repositories')
        sync_parser.add_argument('--path', required=True, help='Local repositories path')
        
        return parser.parse_args()

    def get_token(self, args_token=None):
        """Get best available token: Argument -> Env Var -> Saved Account"""
        if args_token:
            return args_token
            
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            return token
            
        try:
            users = self.user_auth.get_all_users()
            if users:
                # Use first available user
                user_id = users[0]['id']
                creds = self.user_auth.get_github_credentials(user_id)
                if creds:
                    return creds['access_token']
        except Exception:
            pass
            
        return None

    def run(self):
        args = self.parse_args()
        
        if not args.command:
            print("GitHub Downloader CLI v2.0")
            print("Use --help for usage information")
            return 0
            
        if args.command == 'download':
            return self.cmd_download(args)
        elif args.command == 'list':
            return self.cmd_list(args)
        elif args.command == 'search':
            return self.cmd_search(args)
        elif args.command == 'sync':
            return self.cmd_sync(args)
            
        return 0

    def cmd_download(self, args):
        print(f"Working on {args.url}...")
        
        method_map = {
            'git': DownloadMethod.GIT_CLONE,
            'zip': DownloadMethod.DOWNLOAD_ZIP,
            'tar': DownloadMethod.DOWNLOAD_TAR
        }
        method = method_map.get(args.method, DownloadMethod.GIT_CLONE)
        output = args.output or os.path.join(os.path.expanduser("~"), "Downloads")
        
        token = self.get_token(args.token)
        if not token:
            print("⚠️  Warning: No GitHub token found. Rate limits will be restricted.")
            print("   Using unauthenticated access.")
        
        downloader = GitRepoDownloader(token)
        try:
            print(f"Starting download to: {output}")
            task = downloader.create_download_task(args.url, output, method, args.branch or "main")
            
            # Simple progress text
            def progress_callback(t):
                if t.status == "Downloading":
                    sys.stdout.write(f"\rDownloading... {t.progress:.1f}%")
                    sys.stdout.flush()
            
            success = downloader.start_download(task.id, progress_callback)
            print() # Newline
            
            if success:
                print(f"✅ Successfully downloaded {task.repo}")
                return 0
            else:
                print(f"❌ Download failed: {task.error}")
                return 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def cmd_list(self, args):
        token = self.get_token()
        client = GitHubAPIClient(token)
        
        target_user = args.user
        if not target_user and not token:
            print("Error: --user required when not authenticated")
            return 1
            
        print(f"Listing repositories for {target_user or 'authenticated user'}...")
        try:
            repos = client.get_user_repos(target_user)
            print(f"Found {len(repos)} repositories:")
            for repo in repos:
                desc = (repo.get('description') or 'No description')[:50]
                if len(repo.get('description') or '') > 50: desc += "..."
                print(f"- {repo['name']:<30} | ⭐ {repo['stargazers_count']:<4} | {desc}")
        except Exception as e:
            print(f"Error listing repos: {e}")
            return 1

    def cmd_search(self, args):
        print(f"Searching for '{args.query}'...")
        token = self.get_token()
        client = GitHubAPIClient(token)
        
        try:
            results = client.search_repos(args.query)
            print(f"Found {len(results)} matches:")
            for repo in results:
                print(f"- {repo['full_name']:<40} | ⭐ {repo['stargazers_count']}")
        except Exception as e:
            print(f"Search failed: {e}")
            return 1

    def cmd_sync(self, args):
        print(f"Syncing repositories in {args.path}...")
        # Placeholder for sync logic reuse from SyncManager if refactored to be cleaner dependency
        print("Note: Use GUI for full sync functionality currently.")
        return 0
