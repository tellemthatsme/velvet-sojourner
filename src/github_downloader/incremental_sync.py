"""
GitHub Repo Downloader - Incremental Sync
Only download changed files since last sync
"""
import os
import json
import hashlib
import subprocess
import shutil
import tempfile
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import sqlite3


class SyncStrategy(Enum):
    """Sync strategy options"""
    FULL = "full"           # Full download every time
    INCREMENTAL = "incremental"  # Only changed files
    SMART = "smart"         # Auto-detect best strategy


@dataclass
class FileState:
    """State of a file in the repository"""
    path: str
    sha: str
    size: int
    last_modified: datetime
    synced_at: datetime


@dataclass
class SyncResult:
    """Result of a sync operation"""
    success: bool
    files_downloaded: int
    files_updated: int
    files_removed: int
    bytes_transferred: int
    errors: List[str]
    duration_seconds: float
    strategy_used: SyncStrategy
    details: Dict = field(default_factory=dict)


class SyncStateManager:
    """
    Manages sync state for repositories
    Tracks which files have been synced and their states
    """
    
    def __init__(self, state_file: str = None):
        self.state_dir = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', 'sync_state'
        )
        os.makedirs(self.state_dir, exist_ok=True)
        
        self.state_file = state_file or os.path.join(
            self.state_dir, 'sync_state.db'
        )
        self._init_db()
    
    def _init_db(self):
        """Initialize sync state database"""
        conn = sqlite3.connect(self.state_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repo_sync_state (
                repo_url TEXT PRIMARY KEY,
                last_sync TEXT,
                last_commit_sha TEXT,
                strategy TEXT,
                total_files INTEGER,
                total_size INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_sync_state (
                repo_url TEXT,
                file_path TEXT,
                sha TEXT,
                size INTEGER,
                last_modified TEXT,
                synced_at TEXT,
                PRIMARY KEY (repo_url, file_path)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_repo_state(self, repo_url: str) -> Optional[Dict]:
        """Get sync state for a repository"""
        conn = sqlite3.connect(self.state_file)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM repo_sync_state WHERE repo_url = ?',
            (repo_url,)
        )
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'repo_url': row[0],
                'last_sync': row[1],
                'last_commit_sha': row[2],
                'strategy': row[3],
                'total_files': row[4],
                'total_size': row[5]
            }
        return None
    
    def save_repo_state(self, repo_url: str, commit_sha: str, 
                        strategy: SyncStrategy, files: List[FileState]):
        """Save sync state for a repository"""
        conn = sqlite3.connect(self.state_file)
        cursor = conn.cursor()
        
        total_files = len(files)
        total_size = sum(f.size for f in files)
        
        cursor.execute('''
            INSERT OR REPLACE INTO repo_sync_state 
            (repo_url, last_sync, last_commit_sha, strategy, total_files, total_size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            repo_url,
            datetime.now().isoformat(),
            commit_sha,
            strategy.value,
            total_files,
            total_size
        ))
        
        # Save file states
        for file_state in files:
            cursor.execute('''
                INSERT OR REPLACE INTO file_sync_state 
                (repo_url, file_path, sha, size, last_modified, synced_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                repo_url,
                file_state.path,
                file_state.sha,
                file_state.size,
                file_state.last_modified.isoformat(),
                file_state.synced_at.isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_file_states(self, repo_url: str) -> Dict[str, FileState]:
        """Get file states for a repository"""
        conn = sqlite3.connect(self.state_file)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM file_sync_state WHERE repo_url = ?',
            (repo_url,)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        return {
            row[1]: FileState(
                path=row[1],
                sha=row[2],
                size=row[3],
                last_modified=datetime.fromisoformat(row[4]),
                synced_at=datetime.fromisoformat(row[5])
            )
            for row in rows
        }
    
    def remove_repo(self, repo_url: str):
        """Remove sync state for a repository"""
        conn = sqlite3.connect(self.state_file)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM file_sync_state WHERE repo_url = ?',
            (repo_url,)
        )
        cursor.execute(
            'DELETE FROM repo_sync_state WHERE repo_url = ?',
            (repo_url,)
        )
        
        conn.commit()
        conn.close()


class IncrementalDownloader:
    """
    Handles incremental repository downloads using git
    """
    
    def __init__(self, output_base: str, state_manager: SyncStateManager = None):
        self.output_base = output_base
        self.state_manager = state_manager or SyncStateManager()
    
    def get_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL"""
        return repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    
    def get_local_path(self, repo_url: str) -> str:
        """Get local path for repository"""
        repo_name = self.get_repo_name(repo_url)
        return os.path.join(self.output_base, repo_name)
    
    def check_git_available(self) -> bool:
        """Check if git is available"""
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def sync_repository(self, repo_url: str, token: str = None,
                        strategy: SyncStrategy = SyncStrategy.SMART,
                        progress_callback: Callable = None
                        ) -> SyncResult:
        """
        Sync repository using the specified strategy
        
        Args:
            repo_url: Repository URL
            token: Optional authentication token
            strategy: Sync strategy to use
            progress_callback: Optional callback for progress updates
        
        Returns:
            SyncResult with details of the sync operation
        """
        start_time = datetime.now()
        local_path = self.get_local_path(repo_url)
        errors = []
        
        # Determine actual strategy
        actual_strategy = self._determine_strategy(repo_url, local_path, strategy)
        
        try:
            if actual_strategy == SyncStrategy.INCREMENTAL:
                return self._incremental_sync(
                    repo_url, local_path, token, progress_callback, start_time
                )
            else:
                return self._full_sync(
                    repo_url, local_path, token, progress_callback, start_time
                )
        except Exception as e:
            errors.append(str(e))
            return SyncResult(
                success=False,
                files_downloaded=0,
                files_updated=0,
                files_removed=0,
                bytes_transferred=0,
                errors=errors,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                strategy_used=actual_strategy
            )
    
    def _determine_strategy(self, repo_url: str, local_path: str,
                            preferred: SyncStrategy) -> SyncStrategy:
        """Determine which sync strategy to use"""
        if preferred == SyncStrategy.FULL:
            return SyncStrategy.FULL
        
        if preferred == SyncStrategy.SMART:
            # Check if repo exists and is a git repo
            if not os.path.exists(os.path.join(local_path, '.git')):
                return SyncStrategy.FULL
            
            # Check if we've synced before
            state = self.state_manager.get_repo_state(repo_url)
            if not state:
                return SyncStrategy.FULL
            
            return SyncStrategy.INCREMENTAL
        
        return preferred
    
    def _incremental_sync(self, repo_url: str, local_path: str,
                          token: str, progress_callback: Callable,
                          start_time: datetime) -> SyncResult:
        """Perform incremental sync using git fetch and reset"""
        files_downloaded = 0
        files_updated = 0
        files_removed = 0
        bytes_transferred = 0
        errors = []
        
        # Environment for git to prevent prompts
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'
        
        # Ensure repo exists and is git-initialized
        if not os.path.exists(local_path):
            os.makedirs(local_path, exist_ok=True)
            subprocess.run(['git', 'init'], cwd=local_path, capture_output=True, env=env)
        
        # Use authenticated URL if token provided
        remote_url = repo_url
        if token:
            if 'github.com' in remote_url:
                remote_url = remote_url.replace('https://', f'https://x-access-token:{token}@')
        
        # Set or update remote
        subprocess.run(['git', 'remote', 'remove', 'origin'], cwd=local_path, capture_output=True, env=env)
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=local_path, capture_output=True, env=env)
        
        # Fetch changes
        result = subprocess.run(
            ['git', 'fetch', 'origin'],
            cwd=local_path,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode != 0:
            errors.append(f"Git fetch failed: {result.stderr}")
            return SyncResult(
                success=False,
                files_downloaded=0,
                files_updated=0,
                files_removed=0,
                bytes_transferred=0,
                errors=errors,
                duration_seconds=0,
                strategy_used=SyncStrategy.INCREMENTAL
            )
        
        # Get changed files before resetting
        changed_files = self._get_changed_files(local_path)
        
        # Reset to origin/HEAD (usually main or master)
        # Determine default branch
        branch_result = subprocess.run(
            ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'],
            cwd=local_path,
            capture_output=True,
            text=True,
            env=env
        )
        remote_head = "origin/main" # Fallback
        if branch_result.returncode == 0:
            remote_head = branch_result.stdout.strip().replace('refs/remotes/', '')
        else:
            # Try to Guess
            for b in ["origin/main", "origin/master"]:
                if subprocess.run(['git', 'rev-parse', '--verify', b], cwd=local_path, capture_output=True).returncode == 0:
                    remote_head = b
                    break

        reset_result = subprocess.run(
            ['git', 'reset', '--hard', remote_head],
            cwd=local_path,
            capture_output=True,
            text=True,
            env=env
        )
        
        if reset_result.returncode != 0:
            errors.append(f"Git reset failed: {reset_result.stderr}")
        
        # Get current commit SHA
        commit_sha = self._get_current_commit(local_path)
        
        # Update metrics
        files_updated = len(changed_files.get('modified', []))
        files_downloaded = len(changed_files.get('added', []))
        files_removed = len(changed_files.get('deleted', []))
        
        # Update state
        file_states = self._get_file_states(local_path)
        self.state_manager.save_repo_state(
            repo_url, commit_sha, SyncStrategy.INCREMENTAL, list(file_states.values())
        )
        
        return SyncResult(
            success=len(errors) == 0,
            files_downloaded=files_downloaded,
            files_updated=files_updated,
            files_removed=files_removed,
            bytes_transferred=bytes_transferred,
            errors=errors,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            strategy_used=SyncStrategy.INCREMENTAL,
            details={
                'changed_files': changed_files,
                'commit_sha': commit_sha
            }
        )
    
    def _full_sync(self, repo_url: str, local_path: str,
                   token: str, progress_callback: Callable,
                   start_time: datetime) -> SyncResult:
        """Perform full repository clone/sync"""
        files_downloaded = 0
        bytes_transferred = 0
        errors = []
        
        # Remove existing if strategy is full
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        
        os.makedirs(local_path, exist_ok=True)
        
        # Clone command
        clone_cmd = ['git', 'clone', '--progress', '--verbose']
        if token:
            repo_url_with_auth = repo_url.replace(
                'https://', f'https://{token}@'
            )
            clone_cmd.append(repo_url_with_auth)
        else:
            clone_cmd.append(repo_url)
        
        clone_cmd.append(local_path)
        
        result = subprocess.run(
            clone_cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            errors.append(f"Git clone failed: {result.stderr}")
            return SyncResult(
                success=False,
                files_downloaded=0,
                files_updated=0,
                files_removed=0,
                bytes_transferred=0,
                errors=errors,
                duration_seconds=0,
                strategy_used=SyncStrategy.FULL
            )
        
        # Get file count and size
        files_downloaded = self._count_files(local_path)
        
        # Update state
        commit_sha = self._get_current_commit(local_path)
        file_states = self._get_file_states(local_path)
        self.state_manager.save_repo_state(
            repo_url, commit_sha, SyncStrategy.FULL, list(file_states.values())
        )
        
        return SyncResult(
            success=True,
            files_downloaded=files_downloaded,
            files_updated=0,
            files_removed=0,
            bytes_transferred=bytes_transferred,
            errors=errors,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            strategy_used=SyncStrategy.FULL,
            details={'commit_sha': commit_sha}
        )
    
    def _get_changed_files(self, local_path: str) -> Dict[str, List[str]]:
        """Get list of changed files since last sync"""
        state = self.state_manager.get_repo_state(local_path)
        last_commit = state['last_commit_sha'] if state else None
        
        changed = {'modified': [], 'added': [], 'deleted': []}
        
        if last_commit:
            # Get modified and added files
            result = subprocess.run(
                ['git', 'diff', '--name-only', last_commit + '..HEAD'],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                changed['modified'] = result.stdout.strip().split('\n')
            
            # Get new files
            result = subprocess.run(
                ['git', 'ls-files', '--others', '--exclude-standard'],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                changed['added'] = [
                    f for f in result.stdout.strip().split('\n') if f
                ]
            
            # Get deleted files
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=D', 
                 last_commit + '..HEAD'],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                changed['deleted'] = [
                    f for f in result.stdout.strip().split('\n') if f
                ]
        
        return changed
    
    def _checkout_file(self, local_path: str, file_path: str) -> Tuple[bool, int]:
        """Checkout a single file from git"""
        result = subprocess.run(
            ['git', 'checkout', 'HEAD', '--', file_path],
            cwd=local_path,
            capture_output=True
        )
        
        size = 0
        full_path = os.path.join(local_path, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
        
        return result.returncode == 0, size
    
    def _get_current_commit(self, local_path: str) -> str:
        """Get current commit SHA"""
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=local_path,
            capture_output=True,
            text=True
        )
        
        return result.stdout.strip() if result.returncode == 0 else ""
    
    def _get_file_states(self, local_path: str) -> Dict[str, FileState]:
        """Get all file states in the repository"""
        file_states = {}
        
        # Get all tracked files with their info
        result = subprocess.run(
            ['git', 'ls-files', '-z'],
            cwd=local_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return file_states
        
        files = result.stdout.strip().split('\n')
        
        for file_path in files:
            if not file_path:
                continue
            
            # Get SHA for each file
            sha_result = subprocess.run(
                ['git', 'ls-files', '-s', file_path],
                cwd=local_path,
                capture_output=True,
                text=True
            )
            
            if sha_result.returncode == 0:
                parts = sha_result.stdout.strip().split()
                if len(parts) >= 2:
                    sha = parts[1]
                    full_path = os.path.join(local_path, file_path)
                    size = os.path.getsize(full_path) if os.path.exists(full_path) else 0
                    
                    file_states[file_path] = FileState(
                        path=file_path,
                        sha=sha,
                        size=size,
                        last_modified=datetime.now(),
                        synced_at=datetime.now()
                    )
        
        return file_states
    
    def _count_files(self, local_path: str) -> int:
        """Count files in directory"""
        count = 0
        for _, _, filenames in os.walk(local_path):
            count += len(filenames)
        return count
    
    def detect_changes(self, repo_url: str, token: str = None) -> Dict:
        """
        Detect changes without downloading
        
        Returns dict with:
        - has_changes: bool
        - changed_files: list of changed files
        - commit_ahead: number of commits ahead
        - new_releases: list of new releases
        """
        local_path = self.get_local_path(repo_url)
        state = self.state_manager.get_repo_state(repo_url)
        
        if not os.path.exists(os.path.join(local_path, '.git')):
            return {'has_changes': True, 'reason': 'not_synced'}
        
        # Fetch latest
        subprocess.run(
            ['git', 'fetch'],
            cwd=local_path,
            capture_output=True
        )
        
        # Get commit count ahead
        result = subprocess.run(
            ['git', 'rev-list', '--count', '--left-right', 
             'HEAD...origin/HEAD'],
            cwd=local_path,
            capture_output=True,
            text=True
        )
        
        commits_ahead = 0
        if result.returncode == 0:
            try:
                commits_ahead = int(result.stdout.strip())
            except:
                pass
        
        # Get changed files
        changed = self._get_changed_files(local_path)
        total_changed = len(changed.get('modified', [])) + \
                       len(changed.get('added', [])) + \
                       len(changed.get('deleted', []))
        
        return {
            'has_changes': commits_ahead > 0 or total_changed > 0,
            'commits_ahead': commits_ahead,
            'changed_files': changed,
            'local_commit': self._get_current_commit(local_path),
            'last_sync': state['last_sync'] if state else None
        }


class SelectiveSyncManager:
    """
    Manages selective sync options
    Allows syncing only specific paths/branches/tags
    """
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', 'sync_config'
        )
        os.makedirs(self.config_dir, exist_ok=True)
    
    def save_sync_config(self, repo_url: str, config: Dict):
        """Save sync configuration for a repository"""
        config_file = os.path.join(
            self.config_dir, 
            hashlib.md5(repo_url.encode()).hexdigest() + '.json'
        )
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_sync_config(self, repo_url: str) -> Optional[Dict]:
        """Get sync configuration for a repository"""
        config_file = os.path.join(
            self.config_dir, 
            hashlib.md5(repo_url.encode()).hexdigest() + '.json'
        )
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return None
    
    def configure_branch_sync(self, repo_url: str, branches: List[str]):
        """Configure sync for specific branches only"""
        self.save_sync_config(repo_url, {
            'type': 'branch',
            'branches': branches
        })
    
    def configure_path_sync(self, repo_url: str, paths: List[str]):
        """Configure sync for specific paths only"""
        self.save_sync_config(repo_url, {
            'type': 'path',
            'paths': paths
        })
    
    def configure_tag_sync(self, repo_url: str, tags: List[str]):
        """Configure sync for specific tags only"""
        self.save_sync_config(repo_url, {
            'type': 'tag',
            'tags': tags
        })
