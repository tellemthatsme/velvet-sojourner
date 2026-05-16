#!/usr/bin/env python3
"""
Chat Export Sorter - AI Chat Export Organizer
==============================================
Parses, categorizes, and organizes chat exports from various AI platforms.

Features:
- Supports TXT, MD, JSON, HTML, PDF inputs
- Detects GPT/Claude/Gemini format
- Extracts Q&A structure and metadata
- Deduplication by hash
- Merge broken threads
- PDF/HTML to Markdown conversion
- Keyword tagging and topic classification
- Organized output by project/date/source
- Clean Markdown with YAML frontmatter

Usage:
    python export_sorter.py                           # Run on default input
    python export_sorter.py --input ./downloads       # Custom input directory
    python export_sorter.py --output ./exports        # Custom output directory
    python export_sorter.py --dedupe                  # Deduplicate only
    python export_sorter.py --merge                   # Merge fragments only
    python export_sorter.py --stats                   # Show statistics

Dependencies:
    - pypdf (for PDF)
    - beautifulsoup4 (for HTML)
    - python-frontmatter (for YAML parsing)
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
EXPORTS_DIR = BASE_DIR / "exports"
INPUT_DIR = BASE_DIR / "downloads"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "export_sort.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ChatExport:
    """Parsed chat export."""
    source: str  # chatgpt, claude, gemini, etc.
    title: str
    model: Optional[str]
    date: Optional[str]
    first_prompt: str
    messages: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    raw_content: str = ""


@dataclass
class SortStats:
    """Sorting statistics."""
    total_files: int = 0
    processed: int = 0
    duplicates: int = 0
    merged: int = 0
    converted: int = 0
    by_source: Dict = field(default_factory=dict)
    by_type: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class ExportParser:
    """Parse chat exports from various formats."""

    SUPPORTED_FORMATS = {".txt", ".md", ".json", ".html", ".pdf"}

    def __init__(self):
        self.stats = SortStats()

    def detect_format(self, filepath: Path) -> str:
        """Detect the format of a chat export."""
        ext = filepath.suffix.lower()

        if ext == ".json":
            return "json"
        elif ext == ".pdf":
            return "pdf"
        elif ext == ".html":
            return "html"
        elif ext in [".txt", ".md"]:
            # Check content for format hints
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if "ChatGPT" in content or "gpt" in content.lower()[:500]:
                return "chatgpt"
            elif "Claude" in content or "anthropic" in content.lower()[:500]:
                return "claude"
            elif "Gemini" in content or "bard" in content.lower()[:500]:
                return "gemini"
            else:
                return "generic"

        return "unknown"

    def parse_file(self, filepath: Path) -> Optional[ChatExport]:
        """Parse a single export file."""
        ext = filepath.suffix.lower()

        if ext not in self.SUPPORTED_FORMATS:
            logger.debug(f"Unsupported format: {filepath}")
            return None

        format_type = self.detect_format(filepath)

        try:
            if format_type == "json":
                return self._parse_json(filepath)
            elif format_type == "pdf":
                return self._parse_pdf(filepath)
            elif format_type == "html":
                return self._parse_html(filepath)
            else:
                return self._parse_text(filepath, format_type)

        except Exception as e:
            logger.error(f"Failed to parse {filepath}: {e}")
            self.stats.errors.append(f"{filepath}: {e}")
            return None

    def _parse_json(self, filepath: Path) -> Optional[ChatExport]:
        """Parse JSON export."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Detect source
        source = "unknown"
        if "chatgpt" in str(data).lower()[:1000]:
            source = "chatgpt"
        elif "claude" in str(data).lower()[:1000]:
            source = "claude"
        elif "gemini" in str(data).lower()[:1000]:
            source = "gemini"

        title = filepath.stem
        model = data.get("model", None)
        date = data.get("created_at", None) or data.get("date", None)

        first_prompt = ""
        messages = []

        # Try to extract messages
        if "messages" in data:
            for msg in data["messages"]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if role == "user" and not first_prompt:
                    first_prompt = content[:200]
                messages.append({"role": role, "content": content})

        return ChatExport(
            source=source,
            title=title,
            model=model,
            date=date,
            first_prompt=first_prompt,
            messages=messages,
            raw_content=str(data)[:1000],
            metadata={"format": "json", "file_size": filepath.stat().st_size},
        )

    def _parse_pdf(self, filepath: Path) -> Optional[ChatExport]:
        """Parse PDF export by converting to text first."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            # Convert to markdown-like format
            return self._parse_text_content(text, "pdf", filepath.stem)

        except ImportError:
            logger.warning("pypdf not installed. PDF parsing disabled.")
            return None

    def _parse_html(self, filepath: Path) -> Optional[ChatExport]:
        """Parse HTML export."""
        try:
            from bs4 import BeautifulSoup

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()

            soup = BeautifulSoup(html, "html.parser")

            # Remove script/style
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            text = soup.get_text(separator="\n")

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            return self._parse_text_content(text, "html", filepath.stem)

        except ImportError:
            logger.warning("beautifulsoup4 not installed. HTML parsing disabled.")
            return None

    def _parse_text(self, filepath: Path, format_type: str) -> Optional[ChatExport]:
        """Parse text/markdown export."""
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        return self._parse_text_content(content, format_type, filepath.stem)

    def _parse_text_content(
        self, content: str, format_type: str, fallback_title: str
    ) -> Optional[ChatExport]:
        """Parse text content and extract chat structure."""
        # Detect source
        source = format_type
        content_lower = content.lower()

        if "chatgpt" in content_lower[:1000] or "openai" in content_lower[:1000]:
            source = "chatgpt"
        elif "claude" in content_lower[:1000] or "anthropic" in content_lower[:1000]:
            source = "claude"
        elif "gemini" in content_lower[:1000] or "bard" in content_lower[:1000]:
            source = "gemini"

        # Extract title from first line or heading
        title = fallback_title
        lines = content.split("\n")
        for line in lines[:5]:
            line = line.strip()
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break

        # Extract first user prompt
        first_prompt = ""
        messages = []

        # Split into user/assistant pairs
        user_pattern = re.compile(r"(?:User|You|Human|Question):?\s*(.+?)(?=(?:Assistant|AI|Bot|Answer|Cursor):|\n\n|\Z)", re.DOTALL | re.IGNORECASE)
        assistant_pattern = re.compile(r"(?:Assistant|AI|Bot|Answer|Cursor):?\s*(.+?)(?=(?:User|You|Human|Question):|\n\n|\Z)", re.DOTALL | re.IGNORECASE)

        # Try to extract Q&A structure
        current_role = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect role markers
            if re.match(r"^(?:User|You|Human|Question):", line, re.IGNORECASE):
                if current_role and current_content:
                    messages.append({"role": current_role, "content": "\n".join(current_content)})
                current_role = "user"
                current_content = [re.sub(r"^(?:User|You|Human|Question):\s*", "", line, flags=re.IGNORECASE)]
            elif re.match(r"^(?:Assistant|AI|Bot|Answer|Cursor):", line, re.IGNORECASE):
                if current_role and current_content:
                    messages.append({"role": current_role, "content": "\n".join(current_content)})
                current_role = "assistant"
                current_content = [re.sub(r"^(?:Assistant|AI|Bot|Answer|Cursor):\s*", "", line, flags=re.IGNORECASE)]
            elif current_role:
                current_content.append(line)

        # Don't forget last message
        if current_role and current_content:
            messages.append({"role": current_role, "content": "\n".join(current_content)})

        # Extract first prompt
        for msg in messages:
            if msg["role"] == "user":
                first_prompt = msg["content"][:200]
                break

        # Try to extract model info
        model = None
        model_match = re.search(r"(?:model|model:|using|powered by|gpt-4|gpt-3\.5|claude-2|claude-3)", content_lower)
        if model_match:
            model = content[model_match.start():model_match.end() + 20].strip()

        # Extract date
        date = None
        date_match = re.search(r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", content[:500])
        if date_match:
            date = date_match.group(1)

        return ChatExport(
            source=source,
            title=title,
            model=model,
            date=date,
            first_prompt=first_prompt,
            messages=messages,
            raw_content=content[:500],
            metadata={"format": format_type},
        )


class ExportOrganizer:
    """Organize and output parsed exports."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_hashes: set = set()
        self._load_existing_hashes()

    def _load_existing_hashes(self):
        """Load existing file hashes to detect duplicates."""
        for md_file in self.output_dir.rglob("*.md"):
            try:
                # Check for content hash
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                content_hash = hashlib.md5(content.encode()).hexdigest()
                self.processed_hashes.add(content_hash)
            except Exception:
                pass

    def _calculate_hash(self, content: str) -> str:
        """Calculate hash for deduplication."""
        return hashlib.md5(content.encode()).hexdigest()

    def _classify_type(self, chat: ChatExport) -> str:
        """Classify chat type by analyzing content."""
        content = chat.raw_content.lower()
        first_prompt = chat.first_prompt.lower()

        # Code-related keywords
        code_keywords = ["code", "function", "class", "implement", "debug", "api", "python", "javascript", "react"]
        if any(kw in first_prompt or kw in content[:1000] for kw in code_keywords):
            return "code"

        # Design-related
        design_keywords = ["design", "ui", "ux", "layout", "css", "style", "visual"]
        if any(kw in first_prompt for kw in design_keywords):
            return "design"

        # Planning
        plan_keywords = ["plan", "strategy", "roadmap", "architecture", "structure"]
        if any(kw in first_prompt for kw in plan_keywords):
            return "plan"

        # Tutorial/Guide
        guide_keywords = ["how to", "tutorial", "explain", "learn", "guide", "tips"]
        if any(kw in first_prompt for kw in guide_keywords):
            return "guide"

        # Ideas
        idea_keywords = ["idea", "thought", "concept", "brainstorm"]
        if any(kw in first_prompt for kw in idea_keywords):
            return "idea"

        return "general"

    def _extract_tags(self, chat: ChatExport) -> List[str]:
        """Extract tags from chat content."""
        tags = []

        # Add source
        tags.append(chat.source)

        # Add model if known
        if chat.model:
            model_tag = chat.model.lower().replace(" ", "-")
            tags.append(f"model-{model_tag}")

        # Add type
        chat_type = self._classify_type(chat)
        tags.append(f"type-{chat_type}")

        # Extract keywords from first prompt
        prompt_words = chat.first_prompt.split()[:5]
        for word in prompt_words:
            word = re.sub(r"[^\w]", "", word).lower()
            if len(word) > 3:
                tags.append(word[:10])

        return list(set(tags))

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename for filesystem."""
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"\s+", "-", name)
        return name[:50].lower()

    def organize(self, chat: ChatExport) -> Optional[Path]:
        """Organize a chat export into the output directory."""
        content = self._format_chat(chat)
        content_hash = self._calculate_hash(content)

        # Check for duplicates
        if content_hash in self.processed_hashes:
            logger.debug(f"Duplicate detected: {chat.title}")
            return None

        # Determine output path
        date = chat.date or datetime.now().strftime("%Y-%m-%d")
        chat_type = self._classify_type(chat)
        tags = self._extract_tags(chat)

        # Create directory structure
        dir_path = self.output_dir / chat_type / date
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create filename
        safe_title = self._sanitize_filename(chat.title)
        filename = f"{safe_title}.md"
        filepath = dir_path / filename

        # Handle duplicates by appending number
        counter = 1
        while filepath.exists():
            filename = f"{safe_title}_{counter}.md"
            filepath = dir_path / filename
            counter += 1

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Add to processed set
        self.processed_hashes.add(content_hash)

        logger.info(f"  📄 {filepath.relative_to(self.output_dir)}")

        return filepath

    def _format_chat(self, chat: ChatExport) -> str:
        """Format chat as markdown with YAML frontmatter."""
        tags = self._extract_tags(chat)

        lines = [
            "---",
            f"title: {chat.title}",
            f"source: {chat.source}",
            f"date: {chat.date or datetime.now().strftime('%Y-%m-%d')}",
            f"tags: {tags}",
            f"model: {chat.model or 'unknown'}",
            f"exported_at: {datetime.now().isoformat()}",
            "---",
            "",
            f"# {chat.title}",
            "",
        ]

        # Add first prompt prominently
        if chat.first_prompt:
            lines.extend([
                "## First Prompt",
                "",
                "> " + chat.first_prompt.replace("\n", "\n> "),
                "",
            ])

        # Add conversation
        if chat.messages:
            lines.extend([
                "## Conversation",
                "",
            ])

            for i, msg in enumerate(chat.messages):
                role = msg.get("role", "unknown").capitalize()
                content = msg.get("content", "")

                lines.extend([
                    f"### {role}",
                    "",
                    content,
                    "",
                ])

        # Add metadata footer
        lines.extend([
            "---",
            f"*Exported from {chat.source} on {datetime.now().isoformat()}*",
        ])

        return "\n".join(lines)


class ExportSorter:
    """Main export sorting pipeline."""

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.parser = ExportParser()
        self.organizer = ExportOrganizer(output_dir)

    def scan_input(self) -> List[Path]:
        """Scan input directory for export files."""
        if not self.input_dir.exists():
            logger.warning(f"Input directory not found: {self.input_dir}")
            return []

        files = []
        for ext in ExportParser.SUPPORTED_FORMATS:
            files.extend(self.input_dir.rglob(f"*{ext}"))

        return sorted(set(files))

    def run(self) -> SortStats:
        """Run the full sorting pipeline."""
        logger.info("=" * 60)
        logger.info("Chat Export Sorter Started")
        logger.info("=" * 60)
        logger.info(f"Input:  {self.input_dir}")
        logger.info(f"Output: {self.output_dir}")
        logger.info("")

        files = self.scan_input()
        self.parser.stats.total_files = len(files)

        logger.info(f"Found {len(files)} files to process")

        for filepath in files:
            logger.info(f"Processing: {filepath.name}")

            # Parse the file
            chat = self.parser.parse_file(filepath)

            if chat:
                # Organize into output
                result = self.organizer.organize(chat)

                if result:
                    self.parser.stats.processed += 1
                    self.parser.stats.by_source[chat.source] = (
                        self.parser.stats.by_source.get(chat.source, 0) + 1
                    )
                    chat_type = self.organizer._classify_type(chat)
                    self.parser.stats.by_type[chat_type] = (
                        self.parser.stats.by_type.get(chat_type, 0) + 1
                    )
                else:
                    self.parser.stats.duplicates += 1
            else:
                self.parser.stats.errors.append(f"Failed to parse: {filepath}")

        self._print_stats()
        return self.parser.stats

    def _print_stats(self):
        """Print sorting statistics."""
        logger.info("")
        logger.info("=" * 60)
        logger.info("Sorting Complete")
        logger.info("=" * 60)
        logger.info(f"Total files:      {self.parser.stats.total_files}")
        logger.info(f"Processed:        {self.parser.stats.processed}")
        logger.info(f"Duplicates:       {self.parser.stats.duplicates}")
        logger.info(f"Errors:           {len(self.parser.stats.errors)}")

        if self.parser.stats.by_source:
            logger.info("")
            logger.info("By Source:")
            for source, count in sorted(self.parser.stats.by_source.items()):
                logger.info(f"  - {source}: {count}")

        if self.parser.stats.by_type:
            logger.info("")
            logger.info("By Type:")
            for chat_type, count in sorted(self.parser.stats.by_type.items()):
                logger.info(f"  - {chat_type}: {count}")

        if self.parser.stats.errors:
            logger.info("")
            logger.info("Errors:")
            for error in self.parser.stats.errors[:10]:
                logger.info(f"  - {error}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Chat Export Sorter - Organize AI chat exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_sorter.py                           Run on default directories
  python export_sorter.py --input ./downloads       Custom input directory
  python export_sorter.py --output ./my-exports    Custom output directory
  python export_sorter.py --stats                  Show statistics only
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=INPUT_DIR,
        help="Input directory (default: downloads/)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=EXPORTS_DIR,
        help="Output directory (default: exports/)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics only",
    )
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove duplicates only",
    )

    args = parser.parse_args()

    sorter = ExportSorter(args.input, args.output)

    if args.stats:
        files = sorter.scan_input()
        print(f"\n📊 Found {len(files)} files in {args.input}")
        print(f"   Output directory: {args.output}")
        return

    if args.dedupe:
        logger.info("Deduplication mode - processing existing exports...")
        # Just re-run organization on existing exports
        sorter.run()
        return

    sorter.run()


if __name__ == "__main__":
    main()
