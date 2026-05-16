#!/usr/bin/env python3
"""
Social Media Post Generator - AI-Powered Content Creation
==========================================================
Generates tweets/posts using OpenAI based on topics and style prompts.

Features:
- Multiple post style templates (professional, casual, thought leader)
- Topic-based generation
- Thread support (multi-tweet posts)
- Hashtag optimization
- Thread export for scheduler
- Content variety with temperature control

Usage:
    python post_gen.py                              # Generate from config
    python post_gen.py --topic "AI automation"      # Custom topic
    python post_gen.py --style "casual"             # Set style
    python post_gen.py --count 5                    # Generate 5 posts
    python post_gen.py --thread                     # Generate thread
    python post_gen.py --preview                    # Preview only
    python post_gen.py --save                       # Save to posts folder

Dependencies:
    - openai
    - python-dotenv
"""

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
POSTS_DIR = BASE_DIR / "posts"
SCHEDULE_DIR = BASE_DIR / "schedule"
CONFIG_FILE = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "post_gen.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class PostStyle:
    """Style configuration for posts."""
    name: str
    description: str
    system_prompt: str
    max_length: int = 280
    hashtags: int = 3
    emoji_level: str = "minimal"  # none, minimal, moderate


@dataclass
class GeneratedPost:
    """Generated post content."""
    content: str
    topic: str
    style: str
    hashtags: List[str]
    thread_index: int = 0
    thread_total: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# Predefined styles
STYLES = {
    "professional": PostStyle(
        name="Professional",
        description="Formal, authoritative, industry-focused",
        system_prompt="""You are a professional thought leader in technology and AI.
Write posts that are:
- Clear and authoritative
- Data-driven when possible
- Focused on business value
- Professional but approachable
- Include actionable insights

Avoid:
- Excessive jargon
- Clickbait
- Controversial topics
- Overly casual language""",
        max_length=280,
        hashtags=3,
        emoji_level="minimal",
    ),
    "casual": PostStyle(
        name="Casual",
        description="Friendly, conversational, relatable",
        system_prompt="""You are a friendly tech enthusiast sharing knowledge.
Write posts that are:
- Conversational and warm
- Use first-person perspective
- Include relatable examples
- Light and engaging
- Sometimes use humor

Avoid:
- Being too formal
- Corporate language
- Preaching tone""",
        max_length=280,
        hashtags=2,
        emoji_level="moderate",
    ),
    "thought_leader": PostStyle(
        name="Thought Leader",
        description="Provocative, forward-thinking, insights",
        system_prompt="""You are a visionary tech leader who challenges conventions.
Write posts that are:
- Thought-provoking questions
- Bold predictions
- Counter-narrative insights
- Strategic thinking
- Inspire action

Include:
- Questions that make people think
- Fresh perspectives
- Original frameworks

Avoid:
- Generic advice
- Summarizing known information
- Playing it safe""",
        max_length=280,
        hashtags=4,
        emoji_level="none",
    ),
    "educational": PostStyle(
        name="Educational",
        description="Informative, tutorial-style, helpful",
        system_prompt="""You are an expert educator breaking down complex topics.
Write posts that are:
- Clear explanations
- Step-by-step thinking
- Use analogies
- Progressive complexity
- End with actionable takeaways

Format:
- Start with the key insight
- Build understanding
- End with practical application""",
        max_length=280,
        hashtags=3,
        emoji_level="minimal",
    ),
    "announcement": PostStyle(
        name="Announcement",
        description="Exciting, feature-focused, promotional",
        system_prompt="""You are announcing an exciting new feature or release.
Write posts that are:
- Enthusiastic but genuine
- Highlight key benefits
- Include specifics
- Call to action
- Create urgency

Keep it compelling without being spammy.""",
        max_length=280,
        hashtags=4,
        emoji_level="moderate",
    ),
}


class OpenAIPoster:
    """AI-powered post generator using OpenAI."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL

        if not self.api_key:
            logger.error("OpenAI API key required. Set OPENAI_API_KEY in .env")
            sys.exit(1)

        self.client = OpenAI(api_key=self.api_key)

    def generate_post(
        self,
        topic: str,
        style: str = "professional",
        count: int = 1,
        include_hashtags: bool = True,
        temperature: float = 0.8,
    ) -> List[GeneratedPost]:
        """Generate posts on a topic with specified style."""
        if style not in STYLES:
            logger.warning(f"Unknown style '{style}', using 'professional'")
            style = "professional"

        style_config = STYLES[style]
        posts = []

        logger.info(f"Generating {count} posts on '{topic}' with style '{style}'")

        for i in range(count):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": style_config.system_prompt},
                        {"role": "user", "content": f"""Write a single social media post about: {topic}

Requirements:
- Maximum {style_config.max_length} characters
- Engaging hook at the start
- Clear, impactful message
- {'Include ' + str(style_config.hashtags) + ' relevant hashtags' if include_hashtags else 'No hashtags'}
- {'Minimal emoji usage' if style_config.emoji_level == 'none' else 'Moderate emoji usage' if style_config.emoji_level == 'moderate' else 'No emoji'}

Write ONLY the post content, nothing else."""},
                    ],
                    temperature=temperature,
                    max_tokens=500,
                )

                content = response.choices[0].message.content.strip()

                # Extract hashtags if present
                hashtags = []
                if include_hashtags:
                    import re
                    hashtags = re.findall(r"#\w+", content)
                    # Remove hashtags from content if they're at the end
                    for tag in hashtags:
                        content = content.replace(tag, "").strip()
                    hashtags = [h.strip() for h in hashtags if h.strip()]

                post = GeneratedPost(
                    content=content,
                    topic=topic,
                    style=style,
                    hashtags=hashtags,
                    thread_index=i + 1,
                    thread_total=count,
                )
                posts.append(post)
                logger.info(f"Generated post {i + 1}/{count}")

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Failed to generate post {i + 1}: {e}")
                continue

        return posts

    def generate_thread(
        self,
        topic: str,
        style: str = "professional",
        tweet_count: int = 5,
        thread_title: Optional[str] = None,
    ) -> List[GeneratedPost]:
        """Generate a Twitter thread on a topic."""
        if style not in STYLES:
            style = "professional"

        style_config = STYLES[style]
        thread = []

        logger.info(f"Generating {tweet_count}-tweet thread on '{topic}'")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": style_config.system_prompt},
                    {"role": "user", "content": f"""Create a Twitter thread about: {topic}

Requirements:
- {tweet_count} tweets total
- Each tweet max {style_config.max_length} characters
- Number each tweet (1/{tweet_count}, 2/{tweet_count}, etc.)
- First tweet is a hook, last includes CTA
- Coherent narrative across all tweets

Return ONLY the numbered tweets, one per line, with no additional text."""},
                ],
                temperature=0.8,
                max_tokens=1500,
            )

            content = response.choices[0].message.content.strip()
            lines = content.split("\n")

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                # Remove numbering like "1/" or "1."
                import re
                line = re.sub(r"^\d+/\d+\s*", "", line)
                line = re.sub(r"^\d+\.\s*", "", line)

                # Extract hashtags
                hashtags = re.findall(r"#\w+", line)
                for tag in hashtags:
                    line = line.replace(tag, "").strip()
                hashtags = [h.strip() for h in hashtags if h.strip()]

                post = GeneratedPost(
                    content=line,
                    topic=topic,
                    style=style,
                    hashtags=hashtags,
                    thread_index=i + 1,
                    thread_total=tweet_count,
                )
                thread.append(post)

            logger.info(f"Generated {len(thread)} tweets for thread")

        except Exception as e:
            logger.error(f"Failed to generate thread: {e}")

        return thread


class PostManager:
    """Manage generated posts."""

    def __init__(self, posts_dir: Path, schedule_dir: Path):
        self.posts_dir = posts_dir
        self.schedule_dir = schedule_dir
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.schedule_dir.mkdir(parents=True, exist_ok=True)

    def save_post(
        self,
        post: GeneratedPost,
        platform: str = "twitter",
        scheduled_date: Optional[str] = None,
    ) -> Path:
        """Save a post to file."""
        filename = f"{post.created_at[:19].replace(':', '-').replace('T', '_')}_{platform}.json"

        if scheduled_date:
            date_dir = self.schedule_dir / scheduled_date
            date_dir.mkdir(parents=True, exist_ok=True)
            filepath = date_dir / filename
        else:
            filepath = self.posts_dir / filename

        post_data = {
            "content": post.content,
            "topic": post.topic,
            "style": post.style,
            "hashtags": post.hashtags,
            "thread_index": post.thread_index,
            "thread_total": post.thread_total,
            "platform": platform,
            "created_at": post.created_at,
            "scheduled_date": scheduled_date,
        }

        with open(filepath, "w") as f:
            json.dump(post_data, f, indent=2)

        logger.info(f"Saved post to {filepath}")
        return filepath

    def save_thread(
        self,
        thread: List[GeneratedPost],
        topic: str,
        platform: str = "twitter",
    ) -> List[Path]:
        """Save a thread to files."""
        thread_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        paths = []

        for post in thread:
            filename = f"thread_{thread_id}_{post.thread_index:02d}.json"
            filepath = self.posts_dir / filename

            post_data = {
                "content": post.content,
                "topic": topic,
                "style": post.style,
                "hashtags": post.hashtags,
                "thread_index": post.thread_index,
                "thread_total": post.thread_total,
                "thread_id": thread_id,
                "platform": platform,
                "created_at": post.created_at,
            }

            with open(filepath, "w") as f:
                json.dump(post_data, f, indent=2)

            paths.append(filepath)

        # Also save thread metadata
        meta_file = self.posts_dir / f"thread_{thread_id}_meta.json"
        with open(meta_file, "w") as f:
            json.dump({
                "thread_id": thread_id,
                "topic": topic,
                "tweet_count": len(thread),
                "created_at": datetime.now().isoformat(),
                "files": [str(p.name) for p in paths],
            }, f, indent=2)

        logger.info(f"Saved thread with {len(thread)} tweets")
        return paths


def format_for_display(post: GeneratedPost) -> str:
    """Format post for terminal display."""
    lines = [
        "=" * 60,
        f"📝 Post #{post.thread_index}/{post.thread_total} ({post.style})",
        "-" * 60,
        post.content,
    ]

    if post.hashtags:
        lines.append("")
        lines.append("Tags: " + " ".join(post.hashtags))

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered Social Media Post Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python post_gen.py                                      Generate from config
  python post_gen.py --topic "AI automation"              Generate on topic
  python post_gen.py --style "casual"                      Set style
  python post_gen.py --count 5                             Generate 5 posts
  python post_gen.py --thread --count 7                    Generate 7-tweet thread
  python post_gen.py --preview                             Preview only
  python post_gen.py --save --schedule tomorrow            Save and schedule
        """,
    )

    parser.add_argument("--topic", help="Topic for post generation")
    parser.add_argument(
        "--style",
        choices=list(STYLES.keys()),
        default="professional",
        help="Post style (default: professional)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of posts to generate (default: 1)",
    )
    parser.add_argument(
        "--thread",
        action="store_true",
        help="Generate as Twitter thread",
    )
    parser.add_argument(
        "--max-tweets",
        type=int,
        default=5,
        help="Maximum tweets in thread (default: 5)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview posts without saving",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save generated posts",
    )
    parser.add_argument(
        "--schedule",
        metavar="DATE",
        help="Schedule posts for date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--platform",
        default="twitter",
        choices=["twitter", "bluesky", "linkedin", "threads"],
        help="Target platform (default: twitter)",
    )

    args = parser.parse_args()

    # Load config for default topic
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

    topic = args.topic or config.get("default_post_topic", "AI automation and productivity")
    temperature = float(config.get("post_temperature", 0.8))

    # Initialize poster
    poster = OpenAIPoster()

    # Generate posts
    if args.thread:
        thread = poster.generate_thread(
            topic=topic,
            style=args.style,
            tweet_count=min(args.max_tweets, 10),
        )

        for post in thread:
            print(format_for_display(post))
            print()

        if args.save:
            manager = PostManager(POSTS_DIR, SCHEDULE_DIR)
            manager.save_thread(thread, topic, args.platform)
    else:
        posts = poster.generate_post(
            topic=topic,
            style=args.style,
            count=args.count,
            temperature=temperature,
        )

        for post in posts:
            print(format_for_display(post))
            print()

        if args.save:
            manager = PostManager(POSTS_DIR, SCHEDULE_DIR)
            for post in posts:
                manager.save_post(post, args.platform, args.schedule)


if __name__ == "__main__":
    main()
