"""
GitHub Repository Downloader/Cloner
Handles downloading and cloning of repositories
"""
import os
import shutil
import subprocess
import requests
import zipfile
import tarfile
from typing import Optional, Dict, List, Callable, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class DownloadMethod(Enum):
    GIT_CLONE = "git_clone"
    DOWNLOAD_ZIP = "download_zip"
    DOWNLOAD_TAR = "download_tar"


class DownloadStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Represents a download task"""
    id: str
    owner: str
    repo: str
    method: DownloadMethod
    output_path: str
    branch: str = "main"
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    current_file: str = ""
    error: str = ""
    size_bytes: int = 0
    files_downloaded: int = 0
    start_time: datetime = None
    end_time: datetime = None


class GitRepoDownloader:
    """Main downloader class"""
    
    def __init__(self, token: str = None, progress_callback: Callable = None):
        self.token = token
        self.progress_callback = progress_callback
        self.active_downloads: Dict[str, DownloadTask] = {}
        self.lock = threading.Lock()
        self.git_executable = self._find_git()
    
    def _find_git(self) -> str:
        """Find git executable"""
        # Check common locations
        git_paths = [
            'git',
            'C:\\Program Files\\Git\\bin\\git.exe',
            'C:\\Program Files (x86)\\Git\\bin\\git.exe',
            'C:\\Program Files\\Git\\cmd\\git.exe',
        ]
        
        for path in git_paths:
            try:
                result = subprocess.run([path, '--version'], 
                                       capture_output=True, timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        return 'git'
    
    def parse_repo_url(self, url: str) -> tuple:
        """Parse GitHub URL to get owner and repo"""
        # Handle various URL formats
        url = url.strip()
        
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        # github.com/owner/repo
        # owner/repo
        
        url = url.replace('https://', '').replace('http://', '')
        url = url.replace('github.com/', '').replace('www.github.com/', '')
        
        if url.endswith('.git'):
            url = url[:-4]
        
        parts = url.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
        
        return None, None
    
    def _get_default_branch(self, owner: str, repo: str) -> str:
        """Get default branch for repository using API"""
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
            
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                return response.json().get('default_branch', 'main')
        except Exception:
            pass
        return 'main'
    
    def create_download_task(self, repo_url: str, output_path: str, 
                            method: DownloadMethod = DownloadMethod.GIT_CLONE,
                            branch: str = "main") -> DownloadTask:
        """Create a download task"""
        import uuid
        owner, repo = self.parse_repo_url(repo_url)
        
        if not owner or not repo:
            raise ValueError(f"Invalid repository URL: {repo_url}")
        
        task_id = str(uuid.uuid4())
        
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        task = DownloadTask(
            id=task_id,
            owner=owner,
            repo=repo,
            method=method,
            output_path=output_path,
            branch=branch,
            start_time=datetime.now()
        )
        
        with self.lock:
            self.active_downloads[task_id] = task
        
        return task
    
    def update_progress(self, task_id: str, progress: float = None, 
                       current_file: str = None, files_downloaded: int = None):
        """Update download progress"""
        with self.lock:
            if task_id in self.active_downloads:
                task = self.active_downloads[task_id]
                if progress is not None:
                    task.progress = progress
                if current_file is not None:
                    task.current_file = current_file
                if files_downloaded is not None:
                    task.files_downloaded = files_downloaded
        
        if self.progress_callback:
            with self.lock:
                if task_id in self.active_downloads:
                    self.progress_callback(self.active_downloads[task_id])
    
    def download_via_git(self, task: DownloadTask) -> bool:
        """Clone repository using git"""
        repo_url = f"https://github.com/{task.owner}/{task.repo}.git"
        
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'  # Don't prompt for credentials
        
        if self.token:
            # Use x-access-token for GitHub PATs
            repo_url = f"https://x-access-token:{self.token}@github.com/{task.owner}/{task.repo}.git"
        
        target_dir = os.path.join(task.output_path, task.repo)
        
        # Remove existing directory if present
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        cmd = [self.git_executable, 'clone', '--progress']
        
        if task.branch and task.branch != 'main':
            cmd.extend(['--branch', task.branch])
        
        cmd.extend([repo_url, target_dir])
        
        try:
            self.update_progress(task.id, progress=5.0, current_file="Starting clone...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env
            )
            
            # Parse progress output
            total_size_estimated = False
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                line = line.strip()
                
                # Parse git progress
                if 'Receiving objects' in line:
                    try:
                        # Extract percentage
                        if '%' in line:
                            percent = float(line.split('%')[0].split()[-1])
                            self.update_progress(task.id, progress=10 + percent * 0.8, 
                                               current_file=line)
                    except (ValueError, IndexError):
                        pass
                elif 'Updating files' in line or 'Checking out files' in line:
                    self.update_progress(task.id, progress=95, current_file=line)
            
            return_code = process.wait()
            
            if return_code == 0:
                task.status = DownloadStatus.COMPLETED
                task.progress = 100.0
                task.end_time = datetime.now()
                return True
            else:
                task.error = f"Git clone failed with exit code {return_code}"
                task.status = DownloadStatus.FAILED
                return False
                
        except Exception as e:
            task.error = str(e)
            task.status = DownloadStatus.FAILED
            return False
    
    def download_as_zip(self, task: DownloadTask) -> bool:
        """Download repository as ZIP archive"""
        import urllib.parse
        
        repo_url = f"https://github.com/{task.owner}/{task.repo}"
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        # Get default branch
        default_branch = self._get_default_branch(task.owner, task.repo)
        branch = task.branch if task.branch and task.branch != 'main' else default_branch
        
        # Download ZIP
        zip_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
        
        target_path = os.path.join(task.output_path, f"{task.repo}-{branch}.zip")
        
        try:
            self.update_progress(task.id, progress=10, current_file="Downloading ZIP...")
            
            response = requests.get(zip_url, headers=headers, stream=True)
            
            if response.status_code != 200:
                task.error = f"Download failed: {response.status_code}"
                task.status = DownloadStatus.FAILED
                return False
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.update_progress(task.id, progress=10 + percent * 0.8, 
                                               current_file=f"Downloaded {downloaded}/{total_size}")
            
            # Extract ZIP
            self.update_progress(task.id, progress=95, current_file="Extracting...")
            
            with zipfile.ZipFile(target_path, 'r') as zip_ref:
                zip_ref.extractall(task.output_path)
            
            # Rename extracted folder to match repo name
            extracted_folder = os.path.join(task.output_path, f"{task.repo}-{branch}")
            if os.path.exists(extracted_folder):
                # Check if target already exists and remove
                target_folder = os.path.join(task.output_path, task.repo)
                if os.path.exists(target_folder):
                    shutil.rmtree(target_folder)
                shutil.move(extracted_folder, target_folder)
            
            task.status = DownloadStatus.COMPLETED
            task.progress = 100.0
            task.end_time = datetime.now()
            
            # Clean up ZIP file
            os.remove(target_path)
            
            return True
            
        except Exception as e:
            task.error = str(e)
            task.status = DownloadStatus.FAILED
            return False
    
    def download_as_tar(self, task: DownloadTask) -> bool:
        """Download repository as TAR archive"""
        repo_url = f"https://github.com/{task.owner}/{task.repo}"
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        # Get default branch
        default_branch = self._get_default_branch(task.owner, task.repo)
        branch = task.branch if task.branch and task.branch != 'main' else default_branch
        
        # Download TAR
        tar_url = f"{repo_url}/archive/refs/heads/{branch}.tar.gz"
        
        target_path = os.path.join(task.output_path, f"{task.repo}-{branch}.tar.gz")
        
        try:
            self.update_progress(task.id, progress=10, current_file="Downloading TAR...")
            
            response = requests.get(tar_url, headers=headers, stream=True)
            
            if response.status_code != 200:
                task.error = f"Download failed: {response.status_code}"
                task.status = DownloadStatus.FAILED
                return False
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.update_progress(task.id, progress=10 + percent * 0.8, 
                                               current_file=f"Downloaded {downloaded}/{total_size}")
            
            # Extract TAR
            self.update_progress(task.id, progress=95, current_file="Extracting...")
            
            with tarfile.open(target_path, 'r:gz') as tar_ref:
                tar_ref.extractall(task.output_path)
            
            # Rename extracted folder
            extracted_folder = os.path.join(task.output_path, f"{task.repo}-{branch}")
            if os.path.exists(extracted_folder):
                target_folder = os.path.join(task.output_path, task.repo)
                if os.path.exists(target_folder):
                    shutil.rmtree(target_folder)
                shutil.move(extracted_folder, target_folder)
            
            task.status = DownloadStatus.COMPLETED
            task.progress = 100.0
            task.end_time = datetime.now()
            
            # Clean up TAR file
            os.remove(target_path)
            
            return True
            
        except Exception as e:
            task.error = str(e)
            task.status = DownloadStatus.FAILED
            return False
    
    def start_download(self, task_id: str) -> bool:
        """Start a download task"""
        with self.lock:
            if task_id not in self.active_downloads:
                return False
            task = self.active_downloads[task_id]
        
        task.status = DownloadStatus.IN_PROGRESS
        
        if task.method == DownloadMethod.GIT_CLONE:
            return self.download_via_git(task)
        elif task.method == DownloadMethod.DOWNLOAD_ZIP:
            return self.download_as_zip(task)
        elif task.method == DownloadMethod.DOWNLOAD_TAR:
            return self.download_as_tar(task)
        
        return False
    
    def cancel_download(self, task_id: str) -> bool:
        """Cancel a download task"""
        with self.lock:
            if task_id not in self.active_downloads:
                return False
            task = self.active_downloads[task_id]
        
        if task.status == DownloadStatus.IN_PROGRESS:
            task.status = DownloadStatus.CANCELLED
            task.end_time = datetime.now()
            return True
        
        return False
    
    def get_download_status(self, task_id: str) -> Optional[DownloadTask]:
        """Get download task status"""
        with self.lock:
            return self.active_downloads.get(task_id)
    
    def get_all_downloads(self) -> List[DownloadTask]:
        """Get all download tasks"""
        with self.lock:
            return list(self.active_downloads.values())
    
    def get_download_path(self, task_id: str) -> Optional[str]:
        """Get the local path of a completed download"""
        with self.lock:
            if task_id not in self.active_downloads:
                return None
            task = self.active_downloads[task_id]
        
        if task.status == DownloadStatus.COMPLETED:
            return os.path.join(task.output_path, task.repo)
        return None


class BatchDownloader:
    """Handles batch downloads with parallel processing"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.downloader = GitRepoDownloader()
        self.results: Dict[str, bool] = {}
    
    def download_multiple(self, repo_list: List[Dict], output_base: str,
                         method: DownloadMethod = DownloadMethod.GIT_CLONE) -> Dict[str, bool]:
        """Download multiple repositories in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for repo_info in repo_list:
                repo_url = repo_info['url']
                branch = repo_info.get('branch', 'main')
                
                task = self.downloader.create_download_task(
                    repo_url, output_base, method, branch
                )
                
                future = executor.submit(self.downloader.start_download, task.id)
                futures[future] = task.id
            
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    results[task_id] = future.result()
                except Exception as e:
                    results[task_id] = False
        
        return results
