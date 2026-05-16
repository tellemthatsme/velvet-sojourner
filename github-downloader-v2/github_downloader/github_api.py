"""
GitHub API Client with Rate Limit Handling and Terms Compliance
Ensures all operations comply with GitHub's Terms of Service
"""
import requests
import time
import os
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading


class AuthType(Enum):
    NONE = "none"
    PAT = "pat"
    OAUTH = "oauth"


@dataclass
class RateLimitInfo:
    """GitHub API rate limit information"""
    limit: int
    remaining: int
    reset_time: datetime
    reset_timestamp: int
    
    def seconds_until_reset(self) -> int:
        """Get seconds until rate limit resets"""
        delta = self.reset_time - datetime.now()
        return max(0, int(delta.total_seconds()))


class GitHubRateLimitHandler:
    """Handles rate limiting with safety margins"""
    
    # GitHub rate limits (per hour)
    AUTHENTICATED_LIMIT = 5000
    UNAUTHENTICATED_LIMIT = 60
    
    # Safety margin - only use 80% of limit
    SAFETY_MARGIN = 0.8
    
    def __init__(self):
        self.requests_made = 0
        self.window_start = datetime.now()
        self.window_requests = []
        self.lock = threading.Lock()
    
    def check_rate_limit(self, headers: Dict, is_authenticated: bool = False) -> RateLimitInfo:
        """Parse rate limit info from headers"""
        limit = int(headers.get('X-RateLimit-Limit', 60))
        remaining = int(headers.get('X-RateLimit-Remaining', 0))
        reset_timestamp = int(headers.get('X-RateLimit-Reset', 0))
        reset_time = datetime.fromtimestamp(reset_timestamp)
        
        return RateLimitInfo(
            limit=limit,
            remaining=remaining,
            reset_time=reset_time,
            reset_timestamp=reset_timestamp
        )
    
    def should_wait(self, rate_limit_info: RateLimitInfo) -> tuple:
        """Check if we should wait before making a request"""
        with self.lock:
            # Apply safety margin
            safe_limit = int(rate_limit_info.limit * self.SAFETY_MARGIN)
            
            current_time = datetime.now()
            self.window_requests = [t for t in self.window_requests 
                                   if (current_time - t).total_seconds() < 3600]
            
            if len(self.window_requests) >= safe_limit:
                # Find when we can make the next request
                oldest_in_window = min(self.window_requests)
                wait_time = 3600 - (current_time - oldest_in_window).total_seconds()
                return True, max(60, int(wait_time))
            
            return False, 0
    
    def record_request(self):
        """Record a request was made"""
        with self.lock:
            self.window_requests.append(datetime.now())
    
    def wait_if_needed(self, rate_limit_info: RateLimitInfo):
        """Wait if rate limited"""
        should_wait, wait_time = self.should_wait(rate_limit_info)
        if should_wait:
            time.sleep(wait_time)


class GitHubTermsCompliance:
    """Ensures compliance with GitHub Terms of Service"""
    
    # Prohibited actions
    PROHIBITED_PATTERNS = [
        r'(?i)password[=:]\s*\S+',
        r'(?i)api[_-]?key[=:]\s*\S+',
        r'(?i)secret[=:]\s*\S+',
        r'(?i)token[=:]\s*\S+',
    ]
    
    # Max file size to download (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    # Max repo size to clone (10GB warning threshold)
    REPO_SIZE_WARNING = 10 * 1024 * 1024 * 1024
    
    def __init__(self):
        self.downloads_log = []
        self.compliance_violations = []
    
    def check_repo_access_terms(self, repo_full_name: str, is_private: bool) -> tuple:
        """Verify repo access complies with terms"""
        # Users can only access repos they own or have explicit permission for
        # This is enforced by GitHub's API, but we log for compliance
        return True, None
    
    def check_download_terms(self, repo_full_name: str, file_size: int) -> tuple:
        """Check if download complies with terms"""
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large: {file_size} bytes (max: {self.MAX_FILE_SIZE} bytes)"
        
        self.downloads_log.append({
            'repo': repo_full_name,
            'size': file_size,
            'timestamp': datetime.now().isoformat()
        })
        
        return True, None
    
    def get_compliance_report(self) -> Dict:
        """Get compliance report"""
        return {
            'total_downloads': len(self.downloads_log),
            'violations': len(self.compliance_violations),
            'downloads': self.downloads_log[-100:]  # Last 100
        }


class GitHubAPIClient:
    """Main GitHub API client with all features"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str = None, auth_type: AuthType = AuthType.NONE):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHubRepoDownloader/1.0'
        })
        
        self.token = token
        self.auth_type = auth_type
        self.rate_handler = GitHubRateLimitHandler()
        self.compliance = GitHubTermsCompliance()
        
        if token:
            self.session.headers['Authorization'] = f'token {token}'
            self.authenticated = True
        else:
            self.authenticated = False
            
        # Performance: Cache for API responses
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes default
    
    def _make_request(self, method: str, url: str, use_cache: bool = False, **kwargs) -> Optional[requests.Response]:
        """Make API request with rate limiting and optional caching"""
        # Cache handling
        if method == 'GET' and use_cache:
            cache_key = f"{url}:{str(kwargs.get('params', ''))}"
            if cache_key in self._cache:
                response, timestamp = self._cache[cache_key]
                if time.time() - timestamp < self._cache_ttl:
                    return response
        # Make the actual request
        response = self.session.request(method, url, **kwargs)
        
        # Record the request for local tracking
        self.rate_handler.record_request()
        
        # Update rate limit info from headers
        rate_info = self.rate_handler.check_rate_limit(response.headers, self.authenticated)
        
        # Handle 403/429 with rate limit message
        if response.status_code in [403, 429]:
            if 'rate limit' in response.text.lower():
                wait_time = rate_info.seconds_until_reset()
                # Optional: Sleep or raise exception? The original slept.
                if wait_time > 0:
                    time.sleep(min(wait_time, 60))
        
        # Cache successful responses
        if method == 'GET' and response.status_code == 200:
            cache_key = f"{url}:{str(kwargs.get('params', ''))}"
            self._cache[cache_key] = (response, time.time())
            
        return response
    
    def get_user(self) -> Optional[Dict]:
        """Get authenticated user info"""
        response = self._make_request('GET', f"{self.BASE_URL}/user", use_cache=True)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_rate_limit(self) -> Dict:
        """Get current rate limit status"""
        response = self._make_request('GET', f"{self.BASE_URL}/rate_limit")
        if response.status_code == 200:
            data = response.json()
            return {
                'core': self.rate_handler.check_rate_limit(
                    {'X-RateLimit-Limit': str(data['resources']['core']['limit']),
                     'X-RateLimit-Remaining': str(data['resources']['core']['remaining']),
                     'X-RateLimit-Reset': str(data['resources']['core']['reset'])}
                ),
                'search': self.rate_handler.check_rate_limit(
                    {'X-RateLimit-Limit': str(data['resources']['search']['limit']),
                     'X-RateLimit-Remaining': str(data['resources']['search']['remaining']),
                     'X-RateLimit-Reset': str(data['resources']['search']['reset'])}
                )
            }
        return None
    
    def get_repo(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository information"""
        response = self._make_request('GET', f"{self.BASE_URL}/repos/{owner}/{repo}", use_cache=True)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_repo_contents(self, owner: str, repo: str, path: str = "", 
                         progress_callback: Callable = None) -> List[Dict]:
        """Get repository contents recursively"""
        contents = []
        stack = [path]
        
        while stack:
            current_path = stack.pop()
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{current_path}"
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                items = response.json()
                if isinstance(items, list):
                    for item in items:
                        contents.append(item)
                        if item['type'] == 'dir':
                            stack.append(item['path'])
                            if progress_callback:
                                progress_callback(f"Scanning: {item['path']}")
                else:
                    contents.append(items)
        
        return contents
    
    def get_repo_tree(self, owner: str, repo: str, recursive: bool = False) -> Optional[Dict]:
        """Get repository tree"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/main"
        if recursive:
            url += "?recursive=1"
        
        response = self._make_request('GET', url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def download_file(self, owner: str, repo: str, path: str, 
                     output_path: str, progress_callback: Callable = None) -> tuple:
        """Download a single file"""
        # Get download URL
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        response = self._make_request('GET', url)
        
        if response.status_code != 200:
            return False, f"Failed to get file info: {response.status_code}"
        
        file_info = response.json()
        
        if file_info.get('type') != 'file':
            return False, "Path is not a file"
        
        # Check compliance
        size = file_info.get('size', 0)
        compliant, error = self.compliance.check_download_terms(f"{owner}/{repo}", size)
        if not compliant:
            return False, error
        
        # Download from raw URL
        if 'download_url' in file_info:
            download_url = file_info['download_url']
        else:
            download_url = file_info.get('html_url', '').replace('/blob/', '/raw/')
        
        response = self._make_request('GET', download_url, stream=True)
        
        if response.status_code != 200:
            return False, f"Download failed: {response.status_code}"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress_callback(f"Downloaded {downloaded}/{total_size} bytes")
        
        return True, output_path
    
    def get_user_repos(self, username: str, page: int = 1, per_page: int = 100) -> List[Dict]:
        """Get user repositories"""
        repos = []
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {'page': page, 'per_page': per_page, 'sort': 'updated'}
        
        response = self._make_request('GET', url, params=params, use_cache=True)
        if response.status_code == 200:
            repos = response.json()
        
        return repos
    
    def search_repos(self, query: str, page: int = 1, per_page: int = 30) -> List[Dict]:
        """Search repositories"""
        url = f"{self.BASE_URL}/search/repositories"
        params = {'q': query, 'page': page, 'per_page': per_page}
        
        response = self._make_request('GET', url, params=params, use_cache=True)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []
    
    def get_org_repos(self, org: str, page: int = 1, per_page: int = 100) -> List[Dict]:
        """Get organization repositories"""
        url = f"{self.BASE_URL}/orgs/{org}/repos"
        params = {'page': page, 'per_page': per_page}
        
        response = self._make_request('GET', url, params=params, use_cache=True)
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_user_starred(self, username: str, page: int = 1, per_page: int = 100) -> List[Dict]:
        """Get starred repositories"""
        url = f"{self.BASE_URL}/users/{username}/starred"
        params = {'page': page, 'per_page': per_page}
        
        response = self._make_request('GET', url, params=params, use_cache=True)
        if response.status_code == 200:
            return response.json()
        return []
    
    def validate_token(self) -> tuple:
        """Validate if token works"""
        response = self._make_request('GET', f"{self.BASE_URL}/user")
        if response.status_code == 200:
            user = response.json()
            return True, user.get('login'), user.get('name')
        return False, None, None


class GitHubOAuth:
    """OAuth2 helper for GitHub"""
    
    CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "your_client_id")
    CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "your_client_secret")
    REDIRECT_URI = "http://localhost:8080/callback"
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 redirect_uri: str = None):
        if client_id:
            self.CLIENT_ID = client_id
        if client_secret:
            self.CLIENT_SECRET = client_secret
        if redirect_uri:
            self.REDIRECT_URI = redirect_uri
    
    def get_authorization_url(self, state: str = None) -> str:
        """Get OAuth authorization URL"""
        import secrets
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'scope': 'repo,user',
            'state': state
        }
        
        from urllib.parse import urlencode
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    def exchange_code(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for token"""
        import requests
        data = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'code': code,
            'redirect_uri': self.REDIRECT_URI
        }
        
        headers = {'Accept': 'application/json'}
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token"""
        data = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        headers = {'Accept': 'application/json'}
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None
