from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


class SkillMDParser:
    """Parse a SKILL.md file into its logical sections."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._content: Optional[str] = None
        self._sections: dict[str, str] = {}
        self._code_blocks: list[dict] = []
        self._urls: list[str] = []

    def parse(self) -> SkillMDParser:
        if not self.path.is_file():
            raise FileNotFoundError(f"SKILL.md not found: {self.path}")

        try:
            self._content = self.path.read_text(encoding="utf-8")
        except (PermissionError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Cannot read {self.path}: {e}")

        self._extract_sections()
        self._extract_code_blocks()
        self._extract_urls()
        return self

    def _extract_sections(self) -> None:
        if not self._content:
            return
        lines = self._content.split("\n")
        current_section = "__header__"
        self._sections[current_section] = ""

        for line in lines:
            if re.match(r"^##\s+", line):
                heading = re.sub(r"^##\s+", "", line).strip().lower().replace(" ", "_")
                current_section = heading
                if current_section not in self._sections:
                    self._sections[current_section] = ""
            else:
                self._sections[current_section] += line + "\n"

    def _extract_code_blocks(self) -> None:
        if not self._content:
            return
        pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
        for match in pattern.finditer(self._content):
            self._code_blocks.append({
                "language": match.group(1) or "text",
                "code": match.group(2),
            })

    def _extract_urls(self) -> None:
        if not self._content:
            return
        self._urls = re.findall(
            r"https?://[^\s()<>\"']+", self._content
        )

    @property
    def content(self) -> Optional[str]:
        return self._content

    @property
    def sections(self) -> dict[str, str]:
        return dict(self._sections)

    @property
    def code_blocks(self) -> list[dict]:
        return list(self._code_blocks)

    @property
    def urls(self) -> list[str]:
        return list(self._urls)

    def get_section(self, name: str) -> Optional[str]:
        return self._sections.get(name)

    @property
    def name(self) -> str:
        return self.get_section("description").split("\n")[0].strip() if self._sections else ""

    def get_section(self, key: str) -> str:
        return self._sections.get(key, "")
