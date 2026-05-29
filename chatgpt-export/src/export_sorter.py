#!/usr/bin/env python3
"""
Chat Export Sorter - AI Chat Export Organizer
==============================================
Enhanced version with merge, HTML/PDF output, and API integration.
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


@dataclass
class ChatExport:
    source: str
    title: str
    model: Optional[str]
    date: Optional[str]
    first_prompt: str
    messages: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    raw_content: str = ""


@dataclass
class SortStats:
    total_files: int = 0
    processed: int = 0
    duplicates: int = 0
    merged: int = 0
    converted: int = 0
    by_source: Dict = field(default_factory=dict)
    by_type: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class ExportParser:
    SUPPORTED_FORMATS = {".txt", ".md", ".json", ".html", ".pdf"}

    def __init__(self):
        self.stats = SortStats()

    def detect_format(self, filepath: Path) -> str:
        ext = filepath.suffix.lower()
        if ext == ".json":
            return "json"
        elif ext == ".pdf":
            return "pdf"
        elif ext == ".html":
            return "html"
        elif ext in [".txt", ".md"]:
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
        ext = filepath.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
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
            self.stats.errors.append(f"{filepath}: {e}")
            return None

    def _parse_json(self, filepath: Path) -> Optional[ChatExport]:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        source = "unknown"
        if "chatgpt" in str(data).lower()[:1000]:
            source = "chatgpt"
        elif "claude" in str(data).lower()[:1000]:
            source = "claude"
        elif "gemini" in str(data).lower()[:1000]:
            source = "gemini"
        title = filepath.stem
        model = data.get("model", None)
        if not model:
            try:
                from src.analyzers.model_detector import ModelDetector
                detected = ModelDetector().detect(json.dumps(data)[:2000])
                if detected[1] > 0.3:
                    model = detected[0]
            except ImportError:
                pass
        date = data.get("created_at", None) or data.get("date", None)
        first_prompt = ""
        messages = []
        if "messages" in data:
            for msg in data["messages"]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if role == "user" and not first_prompt:
                    first_prompt = content[:200]
                messages.append({"role": role, "content": content})
        return ChatExport(
            source=source, title=title, model=model, date=date,
            first_prompt=first_prompt, messages=messages,
            raw_content=str(data)[:1000],
            metadata={"format": "json", "file_size": filepath.stat().st_size},
        )

    def _parse_pdf(self, filepath: Path) -> Optional[ChatExport]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return self._parse_text_content(text, "pdf", filepath.stem)
        except ImportError:
            return None

    def _parse_html(self, filepath: Path) -> Optional[ChatExport]:
        try:
            from bs4 import BeautifulSoup
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)
            return self._parse_text_content(text, "html", filepath.stem)
        except ImportError:
            return None

    def _parse_text(self, filepath: Path, format_type: str) -> Optional[ChatExport]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return self._parse_text_content(content, format_type, filepath.stem)

    def _parse_text_content(self, content: str, format_type: str, fallback_title: str) -> Optional[ChatExport]:
        source = format_type
        content_lower = content.lower()
        if "chatgpt" in content_lower[:1000] or "openai" in content_lower[:1000]:
            source = "chatgpt"
        elif "claude" in content_lower[:1000] or "anthropic" in content_lower[:1000]:
            source = "claude"
        elif "gemini" in content_lower[:1000] or "bard" in content_lower[:1000]:
            source = "gemini"
        title = fallback_title
        lines = content.split("\n")
        for line in lines[:5]:
            line = line.strip()
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
        first_prompt = ""
        messages = []
        current_role = None
        current_content = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
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
        if current_role and current_content:
            messages.append({"role": current_role, "content": "\n".join(current_content)})
        for msg in messages:
            if msg["role"] == "user":
                first_prompt = msg["content"][:200]
                break
        model = None
        try:
            from src.analyzers.model_detector import ModelDetector
            detected = ModelDetector().detect(content)
            if detected[1] > 0.5:
                model = detected[0]
            else:
                model_match = re.search(r"(?:model|model:|using|powered by|gpt-4|gpt-3\.5|claude-2|claude-3)", content_lower)
                if model_match:
                    model = content[model_match.start():model_match.end() + 20].strip()
        except ImportError:
            model_match = re.search(r"(?:model|model:|using|powered by|gpt-4|gpt-3\.5|claude-2|claude-3)", content_lower)
            if model_match:
                model = content[model_match.start():model_match.end() + 20].strip()
        date = None
        date_match = re.search(r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", content[:500])
        if date_match:
            date = date_match.group(1)
        return ChatExport(
            source=source, title=title, model=model, date=date,
            first_prompt=first_prompt, messages=messages,
            raw_content=content[:500], metadata={"format": format_type},
        )


class ExportOrganizer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_hashes: set = set()
        self._load_existing_hashes()

    def _load_existing_hashes(self):
        for md_file in self.output_dir.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                content_hash = hashlib.md5(content.encode()).hexdigest()
                self.processed_hashes.add(content_hash)
            except Exception:
                pass

    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def _classify_type(self, chat: ChatExport) -> str:
        content = chat.raw_content.lower()
        first_prompt = chat.first_prompt.lower()
        code_keywords = ["code", "function", "class", "implement", "debug", "api", "python", "javascript", "react"]
        if any(kw in first_prompt or kw in content[:1000] for kw in code_keywords):
            return "code"
        design_keywords = ["design", "ui", "ux", "layout", "css", "style", "visual"]
        if any(kw in first_prompt for kw in design_keywords):
            return "design"
        plan_keywords = ["plan", "strategy", "roadmap", "architecture", "structure"]
        if any(kw in first_prompt for kw in plan_keywords):
            return "plan"
        guide_keywords = ["how to", "tutorial", "explain", "learn", "guide", "tips"]
        if any(kw in first_prompt for kw in guide_keywords):
            return "guide"
        idea_keywords = ["idea", "thought", "concept", "brainstorm"]
        if any(kw in first_prompt for kw in idea_keywords):
            return "idea"
        return "general"

    def _extract_tags(self, chat: ChatExport) -> List[str]:
        tags = [chat.source]
        if chat.model:
            model_tag = chat.model.lower().replace(" ", "-")
            tags.append(f"model-{model_tag}")
        chat_type = self._classify_type(chat)
        tags.append(f"type-{chat_type}")
        prompt_words = chat.first_prompt.split()[:5]
        for word in prompt_words:
            word = re.sub(r"[^\w]", "", word).lower()
            if len(word) > 3:
                tags.append(word[:10])
        return list(set(tags))

    def _sanitize_filename(self, name: str) -> str:
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"\s+", "-", name)
        return name[:50].lower()

    def organize(self, chat: ChatExport) -> Optional[Path]:
        content = self._format_chat(chat)
        hash_input = f"{chat.source}|{chat.title}|{chat.date}|{chat.model}|{chat.first_prompt}|{json.dumps(chat.messages, sort_keys=True)}"
        content_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        if content_hash in self.processed_hashes:
            return None
        date = chat.date or datetime.now().strftime("%Y-%m-%d")
        chat_type = self._classify_type(chat)
        dir_path = self.output_dir / chat_type / date
        dir_path.mkdir(parents=True, exist_ok=True)
        safe_title = self._sanitize_filename(chat.title)
        filename = f"{safe_title}.md"
        filepath = dir_path / filename
        counter = 1
        while filepath.exists():
            filename = f"{safe_title}_{counter}.md"
            filepath = dir_path / filename
            counter += 1
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        self.processed_hashes.add(content_hash)
        return filepath

    def _format_chat(self, chat: ChatExport) -> str:
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
        if chat.first_prompt:
            lines.extend(["## First Prompt", "", "> " + chat.first_prompt.replace("\n", "\n> "), ""])
        if chat.messages:
            lines.extend(["## Conversation", ""])
            for msg in chat.messages:
                role = msg.get("role", "unknown").capitalize()
                content = msg.get("content", "")
                lines.extend([f"### {role}", "", content, ""])
        lines.extend(["---", f"*Exported from {chat.source} on {datetime.now().isoformat()}*"])
        return "\n".join(lines)

    def export_html(self, chats: List[ChatExport], output_file: Path):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Conversations Export</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #fafafa; color: #333; }
h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }
.conversation { margin-bottom: 30px; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }
.conv-header { background: #f5f5f5; padding: 15px; border-bottom: 1px solid #e0e0e0; }
.conv-header h2 { margin: 0 0 5px 0; font-size: 1.2em; }
.conv-meta { color: #888; font-size: 0.9em; }
.message { padding: 15px; border-bottom: 1px solid #f0f0f0; }
.message:last-child { border-bottom: none; }
.message.user { background: #fff; }
.message.assistant { background: #f8f9ff; }
.role-label { font-weight: 600; font-size: 0.85em; text-transform: uppercase; color: #666; margin-bottom: 5px; }
.message.user .role-label { color: #2c5282; }
.message.assistant .role-label { color: #276749; }
.timestamp { color: #aaa; font-size: 0.8em; float: right; }
</style>
</head>
<body>
<h1>AI Conversations Export</h1>
<p>Exported on """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """ &mdash; """ + str(len(chats)) + """ conversations</p>
"""
        for chat in chats:
            html += f"""
<div class="conversation">
<div class="conv-header">
<h2>{chat.title}</h2>
<div class="conv-meta">Source: {chat.source} | Model: {chat.model or 'unknown'} | Date: {chat.date or 'unknown'}</div>
</div>
"""
            for msg in chat.messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                html += f"""
<div class="message {role}">
<span class="role-label">{role}</span>
<p>{content}</p>
</div>"""
            html += "</div>\n"
        html += "</body>\n</html>"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

    def export_pdf(self, chats: List[ChatExport], output_file: Path):
        html_file = output_file.with_suffix(".html")
        self.export_html(chats, html_file)
        try:
            from weasyprint import HTML
            HTML(html_file).write_pdf(output_file)
        except ImportError:
            raise ImportError("weasyprint required for PDF export: pip install weasyprint")


class ExportSorter:
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.parser = ExportParser()
        self.organizer = ExportOrganizer(output_dir)

    def scan_input(self) -> List[Path]:
        if not self.input_dir.exists():
            return []
        files = []
        for ext in ExportParser.SUPPORTED_FORMATS:
            files.extend(self.input_dir.rglob(f"*{ext}"))
        return sorted(set(files))

    def merge_conversations(self, input_files: List[str], output_file: Optional[Path] = None) -> ChatExport:
        all_messages = []
        title = "Merged Conversation"
        source = "merged"
        model = None
        date = None

        for file_path in input_files:
            chat = self.parser.parse_file(Path(file_path))
            if chat:
                all_messages.extend(chat.messages)
                if not model and chat.model:
                    model = chat.model
                if not date and chat.date:
                    date = chat.date

        all_messages.sort(key=lambda x: x.get('timestamp', ''))
        merged = []
        for msg in all_messages:
            if merged and merged[-1]['role'] == msg['role']:
                merged[-1]['content'] += "\n\n" + msg['content']
            else:
                merged.append(msg)

        merged_chat = ChatExport(
            source=source, title=title, model=model, date=date,
            first_prompt=merged[0]['content'][:200] if merged else "",
            messages=merged,
        )

        if output_file:
            content = self.organizer._format_chat(merged_chat)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

        return merged_chat

    def run(self, output_format: str = "md") -> SortStats:
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("Chat Export Sorter Started")
        logger.info("=" * 60)
        logger.info(f"Input:  {self.input_dir}")
        logger.info(f"Output: {self.output_dir}")
        logger.info(f"Format: {output_format}")

        files = self.scan_input()
        self.parser.stats.total_files = len(files)
        logger.info(f"Found {len(files)} files to process")

        processed_chats = []
        for filepath in files:
            logger.info(f"Processing: {filepath.name}")
            chat = self.parser.parse_file(filepath)
            if chat:
                result = self.organizer.organize(chat)
                if result:
                    processed_chats.append(chat)
                    self.parser.stats.processed += 1
                    self.parser.stats.by_source[chat.source] = self.parser.stats.by_source.get(chat.source, 0) + 1
                    chat_type = self.organizer._classify_type(chat)
                    self.parser.stats.by_type[chat_type] = self.parser.stats.by_type.get(chat_type, 0) + 1
                else:
                    self.parser.stats.duplicates += 1
            else:
                self.parser.stats.errors.append(f"Failed to parse: {filepath}")

        if output_format in ("html", "pdf") and processed_chats:
            output_file = self.output_dir / f"export.{output_format}"
            if output_format == "html":
                self.organizer.export_html(processed_chats, output_file)
            elif output_format == "pdf":
                self.organizer.export_pdf(processed_chats, output_file)
            logger.info(f"Generated {output_format.upper()}: {output_file}")

        self._print_stats()
        return self.parser.stats

    def _print_stats(self):
        logger = logging.getLogger(__name__)
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
            logger.info(f"Errors ({len(self.parser.stats.errors)}):")
            for error in self.parser.stats.errors[:10]:
                logger.info(f"  - {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Chat Export Sorter - Organize AI chat exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python export_sorter.py                           Run on default directories
  python export_sorter.py --input ./downloads       Custom input directory
  python export_sorter.py --output ./my-exports     Custom output directory
  python export_sorter.py --dedupe                  Deduplicate only
  python export_sorter.py --merge file1.txt file2.txt --output merged.md    Merge conversations
  python export_sorter.py --format html             Export as HTML
  python export_sorter.py --format pdf              Export as PDF
  python export_sorter.py --stats                   Show statistics only
        """,
    )
    parser.add_argument("--input", "-i", type=Path, default=Path("downloads"), help="Input directory")
    parser.add_argument("--output", "-o", type=Path, default=Path("exports"), help="Output directory")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--dedupe", action="store_true", help="Remove duplicates only")
    parser.add_argument("--merge", nargs="+", help="Merge conversation files into one")
    parser.add_argument("--format", choices=["md", "html", "pdf"], default="md", help="Output format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout)])

    sorter = ExportSorter(args.input, args.output)

    if args.stats:
        files = sorter.scan_input()
        print(f"\n📊 Found {len(files)} files in {args.input}")
        print(f"   Output directory: {args.output}")
        return

    if args.merge:
        if not args.output:
            print("Error: --output required with --merge")
            sys.exit(1)
        result = sorter.merge_conversations(args.merge, Path(args.output))
        print(f"\n✅ Merged {len(args.merge)} files into {args.output}")
        print(f"   Messages: {len(result.messages)}")
        return

    if args.dedupe:
        logging.getLogger().info("Deduplication mode - processing existing exports...")
        sorter.run(args.format)
        return

    sorter.run(args.format)


if __name__ == "__main__":
    main()
