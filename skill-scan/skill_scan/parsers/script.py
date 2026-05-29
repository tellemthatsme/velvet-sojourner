from __future__ import annotations

from pathlib import Path
from typing import Optional


class ScriptParser:
    """Analyze script files to detect language and extract patterns."""

    LANG_MAP = {
        ".py": "python",
        ".sh": "shell",
        ".bat": "batch",
        ".ps1": "powershell",
        ".js": "javascript",
        ".ts": "typescript",
        ".rb": "ruby",
        ".pl": "perl",
        ".php": "php",
    }

    def __init__(self, path: Path) -> None:
        self.path = path
        self._content: Optional[str] = None
        self._lines: list[str] = []

    def parse(self) -> ScriptParser:
        if not self.path.is_file():
            raise FileNotFoundError(f"File not found: {self.path}")

        try:
            self._content = self.path.read_text(encoding="utf-8")
        except (PermissionError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Cannot read {self.path}: {e}")

        self._lines = self._content.split("\n")
        return self

    @property
    def content(self) -> Optional[str]:
        return self._content

    @property
    def lines(self) -> list[str]:
        return list(self._lines)

    @property
    def line_count(self) -> int:
        return len(self._lines)

    @property
    def language(self) -> str:
        return self.LANG_MAP.get(self.path.suffix.lower(), "text")

    @property
    def is_binary(self) -> bool:
        if not self._content:
            return False
        try:
            self._content.encode("utf-8")
            return False
        except (UnicodeEncodeError, UnicodeDecodeError):
            return True

    def find_pattern(self, pattern: str) -> list[tuple[int, str]]:
        """Find all lines matching a regex pattern."""
        import re
        matches: list[tuple[int, str]] = []
        for i, line in enumerate(self._lines, 1):
            if re.search(pattern, line):
                matches.append((i, line.strip()))
        return matches

    def extract_shebang(self) -> Optional[str]:
        if self._lines and self._lines[0].startswith("#!"):
            return self._lines[0]
        return None
