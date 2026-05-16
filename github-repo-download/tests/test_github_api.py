import unittest
import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from github_downloader.github_api import GitHubRateLimitHandler, RateLimitInfo, GitHubTermsCompliance

class TestGitHubAPI(unittest.TestCase):
    def test_rate_limit_parsing(self):
        handler = GitHubRateLimitHandler()
        headers = {
            'X-RateLimit-Limit': '5000',
            'X-RateLimit-Remaining': '4999',
            'X-RateLimit-Reset': '1600000000'
        }
        
        # Test default authenticated=False (this was the bug we fixed)
        info = handler.check_rate_limit(headers)
        self.assertEqual(info.limit, 5000)
        self.assertEqual(info.remaining, 4999)
        
    def test_should_wait(self):
        handler = GitHubRateLimitHandler()
        
        # Mock rate limit info - plenty remaining
        info = RateLimitInfo(
            limit=5000,
            remaining=4000,
            reset_time=datetime.now() + timedelta(hours=1),
            reset_timestamp=0
        )
        
        should_wait, _ = handler.should_wait(info)
        self.assertFalse(should_wait)
        
    def test_compliance_check(self):
        compliance = GitHubTermsCompliance()
        
        # Test valid file size
        valid, msg = compliance.check_download_terms("owner/repo", 1024)
        self.assertTrue(valid)
        self.assertIsNone(msg)
        
        # Test too large file (>100MB)
        large_size = 100 * 1024 * 1024 + 1
        valid, msg = compliance.check_download_terms("owner/repo", large_size)
        self.assertFalse(valid)
        self.assertIn("File too large", msg)

if __name__ == '__main__':
    unittest.main()
