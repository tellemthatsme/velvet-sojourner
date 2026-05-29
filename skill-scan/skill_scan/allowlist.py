from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from skill_scan.models import Finding


@dataclass
class AllowlistEntry:
    rule_id: str
    file_pattern: str
    reason: str = ""
    expires: Optional[str] = None

    def is_expired(self) -> bool:
        if not self.expires:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires)
            return datetime.now() > expiry
        except (ValueError, TypeError):
            return False


class Allowlist:
    def __init__(self, path: Path) -> None:
        self.path = path.resolve()

    def load(self) -> list[AllowlistEntry]:
        if not self.path.is_file():
            return []
        if yaml is None:
            return []
        try:
            raw = self.path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
            if not data or "allowlist" not in data:
                return []
            entries: list[AllowlistEntry] = []
            for item in data["allowlist"]:
                entries.append(AllowlistEntry(
                    rule_id=item.get("rule_id", ""),
                    file_pattern=item.get("file_pattern", ""),
                    reason=item.get("reason", ""),
                    expires=item.get("expires"),
                ))
            return entries
        except (yaml.YAMLError, OSError):
            return []

    def save(self, entries: list[AllowlistEntry]) -> None:
        if yaml is None:
            raise RuntimeError("PyYAML is required to save allowlist files")
        data = {"allowlist": []}
        for entry in entries:
            item: dict = {
                "rule_id": entry.rule_id,
                "file_pattern": entry.file_pattern,
            }
            if entry.reason:
                item["reason"] = entry.reason
            if entry.expires:
                item["expires"] = entry.expires
            data["allowlist"].append(item)
        self.path.write_text(
            yaml.safe_dump(data, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

    @staticmethod
    def _norm(p: str) -> str:
        return p.replace("\\", "/")

    def is_allowed(self, finding: Finding) -> bool:
        entries = self.load()
        fpath_str = self._norm(str(finding.file_path))
        fname_str = self._norm(finding.file_path.name)
        try:
            rel_str = self._norm(str(finding.file_path.relative_to(self.path.parent)))
        except (ValueError, AttributeError):
            rel_str = fpath_str
        candidates = [fpath_str, rel_str, fname_str]

        for entry in entries:
            if entry.is_expired():
                continue
            pattern = self._norm(entry.file_pattern)
            if not any(
                fnmatch.fnmatch(c, pattern)
                for c in candidates
                if c is not None
            ):
                continue
            if fnmatch.fnmatch(finding.rule_id, entry.rule_id):
                return True
        return False

    def add_entry(self, entry: AllowlistEntry) -> None:
        entries = self.load()
        entries.append(entry)
        self.save(entries)

    def remove_entry(self, rule_id: str, file_pattern: str) -> bool:
        entries = self.load()
        before = len(entries)
        entries = [
            e for e in entries
            if not (e.rule_id == rule_id and e.file_pattern == file_pattern)
        ]
        if len(entries) == before:
            return False
        self.save(entries)
        return True
