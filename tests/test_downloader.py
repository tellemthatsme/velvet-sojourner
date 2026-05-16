import unittest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from github_downloader.downloader import GitRepoDownloader, DownloadMethod

class TestDownloader(unittest.TestCase):
    def setUp(self):
        self.downloader = GitRepoDownloader()

    def test_parse_repo_url_https(self):
        owner, repo = self.downloader.parse_repo_url('https://github.com/owner/repo')
        self.assertEqual(owner, 'owner')
        self.assertEqual(repo, 'repo')

    def test_parse_repo_url_short(self):
        owner, repo = self.downloader.parse_repo_url('owner/repo')
        self.assertEqual(owner, 'owner')
        self.assertEqual(repo, 'repo')

    def test_parse_repo_url_git_extension(self):
        owner, repo = self.downloader.parse_repo_url('https://github.com/owner/repo.git')
        self.assertEqual(owner, 'owner')
        self.assertEqual(repo, 'repo')

    def test_parse_invalid_url(self):
        owner, repo = self.downloader.parse_repo_url('invalid-url')
        self.assertIsNone(owner)
        self.assertIsNone(repo)

    def test_create_download_task(self):
        task = self.downloader.create_download_task(
            'https://github.com/owner/repo', 
            '/tmp', 
            DownloadMethod.DOWNLOAD_ZIP,
            'dev'
        )
        
        self.assertEqual(task.owner, 'owner')
        self.assertEqual(task.repo, 'repo')
        self.assertEqual(task.method, DownloadMethod.DOWNLOAD_ZIP)
        self.assertEqual(task.branch, 'dev')
        self.assertIsNotNone(task.id)

if __name__ == '__main__':
    unittest.main()
