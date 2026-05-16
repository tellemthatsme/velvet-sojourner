#!/usr/bin/env python3
"""
GitHub Sync Tool - Slow Repo Synchronization
=============================================
Rate-limited GitHub repository puller with token auth and update detection.

Features:
- Supports public and private repositories
- Rate-limited requests to avoid API limits
- Branch and release detection
- Incremental updates (only new commits)
- Release notes generation
- Organization and user repos support

Usage:
    python sync.py                                    # Sync configured repos
    python sync.py --repo owner/repo                  # Sync specific repo
    python sync.py --user username                    # Sync all user repos
    python sync.py --org organization                 # Sync all org repos
    python sync.py --output ~/backup                  # Custom output dir
    python sync.py --verbose                          # Verbose output

Configuration:
    Set GITHUB_TOKEN in .env file or environment variable.
    Configure repos in config.json or pass via command line.
"""

import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import requests

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
REPOS_DIR = BASE_DIR / "repos"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "sync.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class RepoInfo:
    """Repository information."""
    owner: str
    name: str
    full_name: str
    default_branch: str
    description: Optional[str] = None
    updated_at: Optional[str] = None
    clone_url: str = ""
    html_url: str = ""
    private: bool = False


@dataclass
class SyncConfig:
    """Sync configuration."""
    token: str = ""
    repos: List[str] = field(default_factory=list)
    output_dir: Path = REPOS_DIR
    rate_limit_delay: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    include_releases: bool = True
    include_wiki: bool = False


class GitHubSync:
    """GitHub repository synchronization tool."""

    BASE_API_URL = "https://api.github.com"
    RATE_LIMIT_REMAINING = 0

    def __init__(self, config: SyncConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Automation-Sync/1.0",
        })

    def _api_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Optional[requests.Response]:
        """Make API request with rate limiting and retries."""
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    timeout=self.config.timeout,
                )

                # Update rate limit info
                remaining = response.headers.get("X-RateLimit-Remaining", "N/A")
                GitHubSync.RATE_LIMIT_REMAINING = remaining
                reset_time = response.headers.get("X-RateLimit-Reset", "N/A")

                if response.status_code == 403:
                    # Rate limited
                    try:
                        reset_ts = int(reset_time)
                        wait_time = max(0, reset_ts - int(time.time()))
                        logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                        time.sleep(min(wait_time + 5, 3600))
                        continue
                    except (ValueError, TypeError):
                        logger.warning("Rate limited. Waiting 60 seconds...")
                        time.sleep(60)
                        continue

                if response.status_code == 429:
                    logger.warning("Too many requests. Waiting 5 seconds...")
                    time.sleep(5)
                    continue

                if response.status_code >= 400:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    return None

                return response

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.config.max_retries})")
                time.sleep(2 ** attempt)

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                time.sleep(2 ** attempt)

        logger.error(f"Max retries exceeded for {url}")
        return None

    def get_repo(self, owner: str, name: str) -> Optional[RepoInfo]:
        """Get repository information."""
        url = f"{self.BASE_API_URL}/repos/{owner}/{name}"
        response = self._api_request("GET", url)

        if response and response.status_code == 200:
            data = response.json()
            return RepoInfo(
                owner=owner,
                name=name,
                full_name=data.get("full_name", ""),
                default_branch=data.get("default_branch", "main"),
                description=data.get("description"),
                updated_at=data.get("updated_at"),
                clone_url=data.get("clone_url", ""),
                html_url=data.get("html_url", ""),
                private=data.get("private", False),
            )
        return None

    def list_user_repos(self, username: str, include_orgs: bool = True) -> List[str]:
        """List all repositories for a user."""
        repos = []

        # Get user repos
        page = 1
        while True:
            url = f"{self.BASE_API_URL}/users/{username}/repos"
            params = {"type": "all", "per_page": 100, "page": page}
            response = self._api_request("GET", url, params=params)

            if not response or response.status_code != 200:
                break

            data = response.json()
            if not data:
                break

            for repo in data:
                full_name = repo.get("full_name", "")
                if full_name:
                    repos.append(full_name)

            page += 1

        # Get org repos if requested
        if include_orgs:
            orgs = self.list_orgs(username)
            for org in orgs:
                org_repos = self.list_org_repos(org)
                repos.extend(org_repos)

        return list(set(repos))

    def list_orgs(self, username: str) -> List[str]:
        """List organizations for a user."""
        url = f"{self.BASE_API_URL}/users/{username}/orgs"
        response = self._api_request("GET", url)

        if not response or response.status_code != 200:
            return []

        return [org.get("login") for org in response.json()]

    def list_org_repos(self, org: str) -> List[str]:
        """List all repositories in an organization."""
        repos = []

        page = 1
        while True:
            url = f"{self.BASE_API_URL}/orgs/{org}/repos"
            params = {"type": "all", "per_page": 100, "page": page}
            response = self._api_request("GET", url, params=params)

            if not response or response.status_code != 200:
                break

            data = response.json()
            if not data:
                break

            for repo in data:
                full_name = repo.get("full_name", "")
                if full_name:
                    repos.append(full_name)

            page += 1

        return repos

    def get_release_notes(self, owner: str, name: str, since_tag: Optional[str] = None) -> str:
        """Generate release notes for new commits."""
        url = f"{self.BASE_API_URL}/repos/{owner}/{name}/releases"
        params = {"per_page": 10}
        response = self._api_request("GET", url, params=params)

        if not response or response.status_code != 200:
            return ""

        releases = response.json()
        notes = []

        for release in releases:
            if release.get("draft", False):
                continue

            tag = release.get("tag_name", "")
            if since_tag and tag <= since_tag:
                continue

            notes.append(f"## {release.get('name', tag)}")
            notes.append(release.get("body", ""))
            notes.append("")

        return "\n".join(notes)

    def sync_repo(self, repo_full_name: str) -> bool:
        """Synchronize a single repository."""
        owner, name = repo_full_name.split("/")

        # Get repo info
        repo_info = self.get_repo(owner, name)
        if not repo_info:
            logger.error(f"Could not fetch repo info: {repo_full_name}")
            return False

        logger.info(f"Syncing {repo_full_name}...")

        # Create output directory
        repo_dir = self.config.output_dir / owner / name
        repo_dir.mkdir(parents=True, exist_ok=True)

        # Check if repo already cloned
        git_dir = repo_dir / ".git"
        if git_dir.exists():
            return self.update_repo(repo_dir, repo_info)
        else:
            return self.clone_repo(repo_dir, repo_info)

    def clone_repo(self, repo_dir: Path, repo_info: RepoInfo) -> bool:
        """Clone a repository."""
        logger.info(f"Cloning {repo_info.full_name}...")

        try:
            # Clone with depth 1 for faster cloning
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_info.clone_url, str(repo_dir)],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Clone failed: {result.stderr}")
                return False

            # Save repo info
            self._save_repo_info(repo_dir, repo_info)

            logger.info(f"✅ Cloned {repo_info.full_name}")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Clone timed out for {repo_info.full_name}")
            return False
        except Exception as e:
            logger.error(f"Clone error: {e}")
            return False

    def update_repo(self, repo_dir: Path, repo_info: RepoInfo) -> bool:
        """Update an existing repository."""
        logger.info(f"Updating {repo_info.full_name}...")

        try:
            # Get current state
            original_hash = self._get_current_commit_hash(repo_dir)

            # Fetch updates
            result = subprocess.run(
                ["git", "fetch", "--depth", "1", "origin", repo_info.default_branch],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                logger.warning(f"Fetch failed: {result.stderr}")

            # Reset to latest
            result = subprocess.run(
                ["git", "reset", "--hard", f"origin/{repo_info.default_branch}"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"Reset failed: {result.stderr}")
                return False

            new_hash = self._get_current_commit_hash(repo_dir)

            if original_hash != new_hash:
                logger.info(f"✅ Updated {repo_info.full_name} ({original_hash[:7]} → {new_hash[:7]})")
                self._save_repo_info(repo_dir, repo_info)

                # Generate release notes if configured
                if self.config.include_releases:
                    notes = self.get_release_notes(repo_info.owner, repo_info.name)
                    if notes:
                        notes_file = repo_dir / "RELEASE_NOTES.md"
                        with open(notes_file, "w") as f:
                            f.write(f"# Release Notes\n\nGenerated: {datetime.now().isoformat()}\n\n")
                            f.write(notes)
            else:
                logger.info(f"ℹ️  No changes in {repo_info.full_name}")

            return True

        except Exception as e:
            logger.error(f"Update error: {e}")
            return False

    def _get_current_commit_hash(self, repo_dir: Path) -> str:
        """Get current commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    def _save_repo_info(self, repo_dir: Path, repo_info: RepoInfo):
        """Save repository info to JSON."""
        info_file = repo_dir / ".repo_info.json"
        with open(info_file, "w") as f:
            json.dump({
                "owner": repo_info.owner,
                "name": repo_info.name,
                "full_name": repo_info.full_name,
                "default_branch": repo_info.default_branch,
                "description": repo_info.description,
                "updated_at": repo_info.updated_at,
                "html_url": repo_info.html_url,
                "private": repo_info.private,
                "last_synced": datetime.now().isoformat(),
            }, f, indent=2)


def load_config(config_file: Path) -> Dict:
    """Load configuration from file."""
    if config_file.exists():
        with open(config_file, "r") as f:
            return json.load(f)
    return {}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub Sync Tool - Synchronize repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync.py                              Sync configured repos
  python sync.py --repo owner/repo            Sync specific repo
  python sync.py --user username              Sync all user repos
  python sync.py --org organization           Sync all org repos
  python sync.py --output ~/github-backup     Custom output directory
  python sync.py --verbose                    Verbose output
        """,
    )

    parser.add_argument("--repo", help="Specific repository (owner/repo)")
    parser.add_argument("--user", help="Sync all repos for a user")
    parser.add_argument("--org", help="Sync all repos for an organization")
    parser.add_argument("--output", type=Path, default=REPOS_DIR, help="Output directory")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-releases",
        action="store_true",
        help="Don't include release notes",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load config
    config_data = load_config(CONFIG_FILE)

    # Get token
    token = args.token or os.getenv("GITHUB_TOKEN") or config_data.get("github_token", "")
    if not token:
        logger.error("GitHub token required. Set GITHUB_TOKEN env or use --token")
        sys.exit(1)

    # Determine repos to sync
    repos_to_sync = []

    if args.repo:
        repos_to_sync = [args.repo]
    elif args.user:
        config = SyncConfig(token=token, output_dir=args.output, include_releases=not args.no_releases)
        sync = GitHubSync(config)
        repos_to_sync = sync.list_user_repos(args.user)
    elif args.org:
        config = SyncConfig(token=token, output_dir=args.output, include_releases=not args.no_releases)
        sync = GitHubSync(config)
        repos_to_sync = sync.list_org_repos(args.org)
    else:
        repos_to_sync = config_data.get("repos", [])
        if not repos_to_sync:
            logger.error("No repos specified. Use --repo, --user, --org or config.json")
            sys.exit(1)

    # Create sync config
    sync_config = SyncConfig(
        token=token,
        repos=repos_to_sync,
        output_dir=args.output,
        include_releases=not args.no_releases,
    )

    # Create output directory
    sync_config.output_dir.mkdir(parents=True, exist_ok=True)

    # Run sync
    sync = GitHubSync(sync_config)

    logger.info("=" * 60)
    logger.info("GitHub Sync Started")
    logger.info(f"Syncing {len(repos_to_sync)} repositories...")
    logger.info(f"Output: {sync_config.output_dir}")
    logger.info("=" * 60)

    success_count = 0
    fail_count = 0

    for repo in repos_to_sync:
        logger.info(f"\n[{success_count + fail_count + 1}/{len(repos_to_sync)}] ", end="")

        if sync.sync_repo(repo):
            success_count += 1
        else:
            fail_count += 1

        # Rate limiting
        time.sleep(sync_config.rate_limit_delay)

    logger.info("\n" + "=" * 60)
    logger.info(f"GitHub Sync Complete")
    logger.info(f"✅ Success: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
