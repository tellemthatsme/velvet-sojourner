#!/usr/bin/env python3
"""
Social Media Post Scheduler - Daily Auto-Poster
=================================================
Reads schedule.json and auto-posts to social media platforms.

Features:
- Daily post scheduling
- Twitter/X API integration
- Bluesky API integration
- Multi-platform support
- Post queue management
- Failure retry logic
- Logging and statistics

Usage:
    python send_posts.py                    # Run scheduled posts for today
    python send_posts.py --dry-run          # Preview posts without publishing
    python send_posts.py --date 2024-01-15  # Run for specific date
    python send_posts.py --force            # Force send pending posts
    python send_posts.py --status           # Show queue status

Configuration:
    Set TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN
    Set BLUESKY_HANDLE, BLUESKY_APP_PASSWORD in .env

Dependencies:
    - tweepy (Twitter)
    - atproto (Bluesky)
"""

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
POSTS_DIR = BASE_DIR / "posts"
SCHEDULE_DIR = BASE_DIR / "schedule"
CONFIG_FILE = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "send_posts.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class Post:
    """Post data from JSON file."""
    content: str
    topic: str
    style: str
    hashtags: List[str]
    thread_index: int = 0
    thread_total: int = 1
    thread_id: Optional[str] = None
    platform: str = "twitter"
    created_at: str = ""
    post_id: Optional[str] = None
    posted_at: Optional[str] = None
    status: str = "pending"  # pending, posted, failed


class TwitterPoster:
    """Post to Twitter/X using Tweepy."""

    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY", "")
        self.api_secret = os.getenv("TWITTER_API_SECRET", "")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        self.client = None

        if self.api_key and self.api_secret:
            self._init_client()

    def _init_client(self):
        """Initialize Twitter API client."""
        try:
            import tweepy

            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(
                self.access_token,
                self.access_token_secret,
            )

            self.client = tweepy.API(auth)
            logger.info("Twitter API initialized")

        except ImportError:
            logger.warning("Tweepy not installed. Twitter posting disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")

    def post(self, content: str, hashtags: List[str] = None) -> Optional[str]:
        """Post a tweet."""
        if not self.client:
            logger.error("Twitter client not initialized")
            return None

        try:
            # Add hashtags if provided
            tweet = content
            if hashtags:
                hashtag_str = " ".join(hashtags)
                if len(tweet) + len(hashtag_str) + 1 <= 280:
                    tweet = f"{tweet}\n\n{hashtag_str}"

            # Post tweet
            tweet_obj = self.client.update_status(tweet)
            tweet_id = str(tweet_obj.id)

            logger.info(f"✅ Posted to Twitter: {tweet_id}")
            return tweet_id

        except Exception as e:
            logger.error(f"Failed to post to Twitter: {e}")
            return None


class BlueskyPoster:
    """Post to Bluesky using atproto."""

    def __init__(self):
        self.handle = os.getenv("BLUESKY_HANDLE", "")
        self.app_password = os.getenv("BLUESKY_APP_PASSWORD", "")
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Bluesky client."""
        try:
            from atproto import Client

            if self.handle and self.app_password:
                self.client = Client()
                self.client.login(self.handle, self.app_password)
                logger.info("Bluesky API initialized")

        except ImportError:
            logger.warning("atproto not installed. Bluesky posting disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Bluesky API: {e}")

    def post(self, content: str, hashtags: List[str] = None) -> Optional[str]:
        """Post to Bluesky."""
        if not self.client:
            logger.error("Bluesky client not initialized")
            return None

        try:
            # Prepare post with hashtags
            post_text = content
            if hashtags:
                hashtag_str = " ".join(f"#{h.replace('#', '')}" for h in hashtags)
                if len(post_text) + len(hashtag_str) + 2 <= 300:
                    post_text = f"{post_text}\n\n{hashtag_str}"

            # Post to Bluesky
            post = self.client.post(post_text)
            post_uri = post.uri

            # Extract post ID from URI
            post_id = post_uri.split("/")[-1] if post_uri else None

            logger.info(f"✅ Posted to Bluesky: {post_id}")
            return post_id

        except Exception as e:
            logger.error(f"Failed to post to Bluesky: {e}")
            return None


class PostScheduler:
    """Manage post scheduling and posting."""

    def __init__(self):
        self.posts_dir = POSTS_DIR
        self.schedule_dir = SCHEDULE_DIR
        self.twitter = TwitterPoster()
        self.bluesky = BlueskyPoster()
        self.posted_log: Dict[str, List[str]] = {}

    def load_schedule(self, date: str) -> List[Post]:
        """Load posts scheduled for a date."""
        posts = []
        date_dir = self.schedule_dir / date

        if not date_dir.exists():
            logger.info(f"No scheduled posts for {date}")
            return []

        for post_file in date_dir.glob("*.json"):
            try:
                with open(post_file, "r") as f:
                    data = json.load(f)

                post = Post(
                    content=data.get("content", ""),
                    topic=data.get("topic", ""),
                    style=data.get("style", ""),
                    hashtags=data.get("hashtags", []),
                    thread_index=data.get("thread_index", 0),
                    thread_total=data.get("thread_total", 1),
                    thread_id=data.get("thread_id"),
                    platform=data.get("platform", "twitter"),
                    created_at=data.get("created_at", ""),
                )
                posts.append(post)

            except Exception as e:
                logger.error(f"Failed to load {post_file}: {e}")

        return sorted(posts, key=lambda p: p.thread_index)

    def load_all_pending(self) -> List[Post]:
        """Load all pending posts from posts directory."""
        posts = []

        for post_file in self.posts_dir.glob("*.json"):
            if "meta" in post_file.name:
                continue

            try:
                with open(post_file, "r") as f:
                    data = json.load(f)

                if data.get("status", "pending") == "pending":
                    post = Post(
                        content=data.get("content", ""),
                        topic=data.get("topic", ""),
                        style=data.get("style", ""),
                        hashtags=data.get("hashtags", []),
                        thread_index=data.get("thread_index", 0),
                        thread_total=data.get("thread_total", 1),
                        thread_id=data.get("thread_id"),
                        platform=data.get("platform", "twitter"),
                        created_at=data.get("created_at", ""),
                    )
                    posts.append(post)

            except Exception as e:
                logger.error(f"Failed to load {post_file}: {e}")

        return posts

    def post_to_platform(self, post: Post, platform: str) -> Optional[str]:
        """Post to specified platform."""
        if platform in ["twitter", "x"]:
            return self.twitter.post(post.content, post.hashtags)
        elif platform == "bluesky":
            return self.bluesky.post(post.content, post.hashtags)
        else:
            logger.warning(f"Unknown platform: {platform}")
            return None

    def update_post_status(self, post: Post, post_id: str, status: str):
        """Update post status in file."""
        # Find the post file
        filename = f"{post.created_at[:19].replace(':', '-').replace('T', '_')}_{post.platform}.json"
        post_file = self.schedule_dir / post.created_at[:10] / filename

        if not post_file.exists():
            post_file = self.posts_dir / filename

        if post_file.exists():
            with open(post_file, "r") as f:
                data = json.load(f)

            data["post_id"] = post_id
            data["posted_at"] = datetime.now().isoformat()
            data["status"] = status

            with open(post_file, "w") as f:
                json.dump(data, f, indent=2)

    def process_posts(self, date: str = None, dry_run: bool = False, force: bool = False):
        """Process and post scheduled posts."""
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Processing posts for {target_date}")

        if dry_run:
            logger.info("🔍 DRY RUN - No posts will be published")

        posts = self.load_schedule(target_date)

        if not posts:
            # Try loading all pending
            if force:
                posts = self.load_all_pending()
                logger.info(f"Found {len(posts)} pending posts (force mode)")
            else:
                logger.info("No posts scheduled for today")
                return

        thread_groups: Dict[str, List[Post]] = {}
        for post in posts:
            if post.thread_id:
                thread_groups.setdefault(post.thread_id, []).append(post)
            else:
                thread_groups[f"single_{post.created_at}"] = [post]

        for thread_id, thread_posts in thread_groups.items():
            # Sort by thread index
            thread_posts.sort(key=lambda p: p.thread_index)

            # Check if all posts in thread should be posted
            all_pending = all(p.status == "pending" for p in thread_posts)

            if not all_pending and not force:
                logger.info(f"Thread {thread_id} already posted, skipping")
                continue

            for post in thread_posts:
                if dry_run:
                    print(f"\n📝 Would post to {post.platform}:")
                    print(f"   {post.content[:100]}...")
                    print(f"   Hashtags: {post.hashtags}")
                    continue

                # Post to platform
                post_id = self.post_to_platform(post, post.platform)

                if post_id:
                    post.post_id = post_id
                    post.posted_at = datetime.now().isoformat()
                    post.status = "posted"
                    self.update_post_status(post, post_id, "posted")
                else:
                    post.status = "failed"
                    self.update_post_status(post, "", "failed")

                # Rate limiting between posts
                time.sleep(2)

    def show_status(self):
        """Show scheduler status."""
        print("\n📊 Post Scheduler Status")
        print("=" * 60)

        today = datetime.now().strftime("%Y-%m-%d")
        posts = self.load_schedule(today)

        pending = sum(1 for p in posts if p.status == "pending")
        posted = sum(1 for p in posts if p.status == "posted")
        failed = sum(1 for p in posts if p.status == "failed")

        print(f"Today's Schedule ({today}):")
        print(f"  📝 Pending: {pending}")
        print(f"  ✅ Posted: {posted}")
        print(f"  ❌ Failed: {failed}")

        all_pending = self.load_all_pending()
        print(f"\nTotal Pending Posts: {len(all_pending)}")

        if posts:
            print("\nScheduled Posts:")
            for post in posts:
                status_emoji = "⏳" if post.status == "pending" else "✅" if post.status == "posted" else "❌"
                thread_info = f" ({post.thread_index}/{post.thread_total})" if post.thread_total > 1 else ""
                print(f"  {status_emoji} {post.platform:<10} {post.content[:50]}...{thread_info}")

        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Social Media Post Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python send_posts.py                    Run today's scheduled posts
  python send_posts.py --dry-run          Preview posts without publishing
  python send_posts.py --date 2024-01-15  Run for specific date
  python send_posts.py --force            Force send pending posts
  python send_posts.py --status           Show queue status
        """,
    )

    parser.add_argument(
        "--date",
        help="Specific date to process (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview posts without publishing",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force send pending posts",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show scheduler status",
    )

    args = parser.parse_args()

    scheduler = PostScheduler()

    if args.status:
        scheduler.show_status()
        return

    if args.dry_run:
        logger.info("Dry run mode - posts will not be published")

    scheduler.process_posts(
        date=args.date,
        dry_run=args.dry_run,
        force=args.force,
    )


if __name__ == "__main__":
    main()
