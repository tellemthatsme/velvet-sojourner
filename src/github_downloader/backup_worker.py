"""
GitHub Repo Downloader - Backup Worker
Handles downloading issues, PRs, releases, wikis, gists, starred repos, etc.
"""

import os
import json
import time
import subprocess
import urllib.request
import platform
from typing import Dict, List, Optional, Callable
from datetime import datetime

CREATE_NO_WINDOW = 0x08000000 if platform.system() == "Windows" else 0


class BackupWorker:
    """Handles backup of additional GitHub data beyond just the repo"""

    def __init__(self, github_api, token: str = None, download_dir: str = None):
        self.github_api = github_api
        self.token = token
        self.download_dir = download_dir or "."
        self.progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback

    def _log(self, message: str):
        """Log progress"""
        if self.progress_callback:
            self.progress_callback(message)
        print(f"[Backup] {message}")

    def backup_issues(
        self, owner: str, repo: str, output_dir: str, state: str = "all"
    ) -> bool:
        """Download issues as JSON"""
        self._log(f"Downloading issues for {owner}/{repo}...")
        try:
            issues = self.github_api.get_issues(owner, repo, state)
            if not issues:
                self._log(f"No issues found for {owner}/{repo}")
                return True

            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "issues.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(issues, f, indent=2, ensure_ascii=False)
            self._log(f"Downloaded {len(issues)} issues to {output_file}")
            return True
        except Exception as e:
            self._log(f"Failed to download issues: {e}")
            return False

    def backup_pull_requests(
        self, owner: str, repo: str, output_dir: str, state: str = "all"
    ) -> bool:
        """Download pull requests as JSON"""
        self._log(f"Downloading PRs for {owner}/{repo}...")
        try:
            prs = self.github_api.get_pull_requests(owner, repo, state)
            if not prs:
                self._log(f"No PRs found for {owner}/{repo}")
                return True

            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "pull_requests.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(prs, f, indent=2, ensure_ascii=False)
            self._log(f"Downloaded {len(prs)} PRs to {output_file}")
            return True
        except Exception as e:
            self._log(f"Failed to download PRs: {e}")
            return False

    def backup_releases(
        self, owner: str, repo: str, output_dir: str, download_assets: bool = True
    ) -> bool:
        """Download releases with optional assets"""
        self._log(f"Downloading releases for {owner}/{repo}...")
        try:
            releases = self.github_api.get_releases(owner, repo)
            if not releases:
                self._log(f"No releases found for {owner}/{repo}")
                return True

            releases_dir = os.path.join(output_dir, "releases")
            os.makedirs(releases_dir, exist_ok=True)

            releases_file = os.path.join(releases_dir, "releases.json")
            with open(releases_file, "w", encoding="utf-8") as f:
                json.dump(releases, f, indent=2, ensure_ascii=False)
            self._log(f"Downloaded {len(releases)} releases metadata")

            if download_assets:
                for release in releases:
                    tag = release.get("tag_name", "unknown").replace("/", "_")
                    release_assets_dir = os.path.join(releases_dir, f"release_{tag}")
                    os.makedirs(release_assets_dir, exist_ok=True)
                    self._download_release_assets(
                        release.get("assets", []), release_assets_dir
                    )
            return True
        except Exception as e:
            self._log(f"Failed to download releases: {e}")
            return False

    def _download_release_assets(self, assets: List[Dict], output_dir: str):
        """Download release asset files"""
        for asset in assets:
            asset_name = asset.get("name", "unknown")
            download_url = asset.get("browser_download_url")
            if not download_url:
                continue
            self._log(f"  Downloading asset: {asset_name}")
            try:
                output_path = os.path.join(output_dir, asset_name)
                headers = {}
                if self.token:
                    headers["Authorization"] = f"token {self.token}"
                req = urllib.request.Request(download_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    with open(output_path, "wb") as f:
                        total_size = int(response.headers.get("content-length", 0))
                        downloaded = 0
                        chunk_size = 8192
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                self._log(f"  {asset_name}: {percent:.1f}%")
                self._log(f"  Downloaded: {asset_name}")
            except Exception as e:
                self._log(f"  Failed to download {asset_name}: {e}")

    @staticmethod
    def _create_askpass_script(token: str) -> str:
        import tempfile

        script_path = os.path.join(tempfile.gettempdir(), "gh_askpass_bk.bat")
        with open(script_path, "w") as f:
            f.write("@echo off\necho %s\n" % token)
        return script_path

    def backup_wiki(self, owner: str, repo: str, output_dir: str) -> bool:
        """Clone repository wiki"""
        self._log(f"Downloading wiki for {owner}/{repo}...")
        try:
            wiki_url = f"https://github.com/{owner}/{repo}.wiki.git"
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            askpass_path = None
            if self.token:
                wiki_url = f"https://x-access-token@github.com/{owner}/{repo}.wiki.git"
                askpass_path = self._create_askpass_script(self.token)
                env["GIT_ASKPASS"] = askpass_path

            wiki_dir = os.path.join(output_dir, "wiki")
            if os.path.exists(wiki_dir):
                self._log("Wiki already exists, skipping")
                if askpass_path:
                    try:
                        os.remove(askpass_path)
                    except OSError:
                        pass
                return True

            cmd = ["git", "clone", "--progress", wiki_url, wiki_dir]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                universal_newlines=True,
                creationflags=CREATE_NO_WINDOW,
            )
            output, _ = process.communicate()

            if askpass_path:
                try:
                    os.remove(askpass_path)
                except OSError:
                    pass

            if process.returncode == 0:
                self._log(f"Wiki cloned to {wiki_dir}")
                return True
            else:
                self._log(f"Wiki not available (may not exist): {output[:200]}")
                return True
        except Exception as e:
            self._log(f"Failed to clone wiki: {e}")
            return False

    def backup_gists(self, username: str, output_dir: str) -> bool:
        """Download user's gists"""
        self._log(f"Downloading gists for {username}...")
        try:
            gists = self.github_api.get_gists(username)
            if not gists:
                self._log(f"No gists found for {username}")
                return True

            gists_dir = os.path.join(output_dir, "gists")
            os.makedirs(gists_dir, exist_ok=True)

            gists_file = os.path.join(gists_dir, "gists.json")
            with open(gists_file, "w", encoding="utf-8") as f:
                json.dump(gists, f, indent=2, ensure_ascii=False)
            self._log(f"Downloaded {len(gists)} gists metadata")

            for gist in gists:
                gist_id = gist.get("id")
                gist_files = gist.get("files", {})
                for filename, file_data in gist_files.items():
                    gist_file_dir = os.path.join(gists_dir, gist_id)
                    os.makedirs(gist_file_dir, exist_ok=True)
                    file_path = os.path.join(gist_file_dir, filename)
                    content = file_data.get("content", "")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    self._log(f"  Saved gist: {filename}")
            return True
        except Exception as e:
            self._log(f"Failed to download gists: {e}")
            return False

    def backup_starred(self, username: str, output_dir: str) -> bool:
        """Download user's starred repositories"""
        self._log(f"Downloading starred repos for {username}...")
        try:
            starred = self.github_api.get_starred(username)
            if not starred:
                self._log(f"No starred repos for {username}")
                return True

            starred_dir = os.path.join(output_dir, "starred")
            os.makedirs(starred_dir, exist_ok=True)

            starred_file = os.path.join(starred_dir, "starred.json")
            with open(starred_file, "w", encoding="utf-8") as f:
                json.dump(starred, f, indent=2, ensure_ascii=False)
            self._log(f"Downloaded {len(starred)} starred repos")

            askpass_path = None
            if self.token:
                askpass_path = self._create_askpass_script(self.token)

            for repo in starred:
                full_name = repo.get("full_name", "")
                clone_url = repo.get("clone_url", "")
                if not full_name or not clone_url:
                    continue
                target_dir = os.path.join(starred_dir, full_name.replace("/", "_"))
                if os.path.exists(target_dir):
                    self._log(f"  Already exists: {full_name}")
                    continue
                self._log(f"  Cloning: {full_name}")
                try:
                    env = os.environ.copy()
                    env["GIT_TERMINAL_PROMPT"] = "0"
                    if self.token and "github.com" in clone_url:
                        repo_path = clone_url.split("github.com/")[-1].rstrip("/")
                        if repo_path.endswith(".git"):
                            repo_path = repo_path[:-4]
                        clone_url = f"https://x-access-token@github.com/{repo_path}"
                        env["GIT_ASKPASS"] = askpass_path
                    cmd = ["git", "clone", "--progress", clone_url, target_dir]
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,
                        creationflags=CREATE_NO_WINDOW,
                    )
                    process.communicate(timeout=300)
                    self._log(f"  Cloned: {full_name}")
                except subprocess.TimeoutExpired:
                    process.kill()
                    self._log(f"  Timeout: {full_name}")
                except Exception as e:
                    self._log(f"  Failed: {full_name} - {e}")

            if askpass_path:
                try:
                    os.remove(askpass_path)
                except OSError:
                    pass
            return True
        except Exception as e:
            self._log(f"Failed to download starred repos: {e}")
            return False

    def full_backup(
        self,
        owner: str,
        repo: str,
        output_dir: str,
        include_issues: bool = False,
        include_prs: bool = False,
        include_releases: bool = False,
        include_wiki: bool = False,
        include_gists: bool = False,
        include_starred: bool = False,
    ) -> Dict:
        """Run full backup with all selected options"""
        results = {
            "issues": False,
            "prs": False,
            "releases": False,
            "wiki": False,
            "gists": False,
            "starred": False,
        }
        if include_issues:
            results["issues"] = self.backup_issues(owner, repo, output_dir)
        if include_prs:
            results["prs"] = self.backup_pull_requests(owner, repo, output_dir)
        if include_releases:
            results["releases"] = self.backup_releases(owner, repo, output_dir)
        if include_wiki:
            results["wiki"] = self.backup_wiki(owner, repo, output_dir)
        if include_gists:
            results["gists"] = self.backup_gists(owner, output_dir)
        if include_starred:
            results["starred"] = self.backup_starred(owner, output_dir)
        return results
