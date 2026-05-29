from __future__ import annotations

import fnmatch
import time
from pathlib import Path
from typing import Optional

from skill_scan.allowlist import Allowlist
from skill_scan.models import Finding, ScanResult, Severity
from skill_scan.rules import builtin_rules
from skill_scan.rules.base import Rule


_SAFE_EXTENSIONS = {
    ".md", ".py", ".sh", ".bat", ".ps1",
    ".js", ".ts", ".cfg", ".yaml", ".yml",
    ".json", ".toml", ".ini", ".conf", ".txt",
    ".env", ".cfg", ".xml", ".html", ".css",
}

_SKIP_DIRS = {
    ".git", "__pycache__", "node_modules",
    ".venv", "venv", "env", ".tox",
    ".egg-info", ".mypy_cache", ".pytest_cache",
}


class ScanEngine:
    """Core scanning engine that walks directories and runs rules."""

    def __init__(self, rules: Optional[list[Rule]] = None,
                 exclude_patterns: Optional[list[str]] = None,
                 allowlist: Optional[Allowlist] = None) -> None:
        self.rules = rules or list(builtin_rules)
        self.exclude_patterns = exclude_patterns or []
        self.allowlist = allowlist

    def scan(
        self,
        path: Path,
        severity_filter: Optional[Severity] = None,
    ) -> ScanResult:
        start = time.monotonic()
        path = path.resolve()

        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        findings: list[Finding] = []
        files_scanned = 0

        if path.is_file():
            files_scanned += 1
            findings.extend(self._scan_file(path))
        else:
            for fpath in self._walk(path):
                files_scanned += 1
                findings.extend(self._scan_file(fpath))

        if severity_filter is not None:
            findings = [f for f in findings if f.severity >= severity_filter]

        if self.allowlist is not None:
            findings = [f for f in findings if not self.allowlist.is_allowed(f)]

        findings.sort(key=lambda f: (f.severity, f.file_path, f.line_number), reverse=True)

        elapsed = time.monotonic() - start
        return ScanResult(
            skill_path=path,
            findings=findings,
            scan_time=round(elapsed, 4),
            total_rules=len(self.rules),
            files_scanned=files_scanned,
        )

    def _walk(self, directory: Path) -> list[Path]:
        files: list[Path] = []
        try:
            for entry in directory.iterdir():
                if entry.name in _SKIP_DIRS or entry.name.startswith("."):
                    continue
                if entry.is_dir():
                    files.extend(self._walk(entry))
                elif entry.suffix.lower() in _SAFE_EXTENSIONS:
                    if any(fnmatch.fnmatch(str(entry), pat) for pat in self.exclude_patterns):
                        continue
                    files.append(entry)
        except PermissionError:
            pass
        return files

    def _scan_file(self, file_path: Path) -> list[Finding]:
        content = self._read_file(file_path)
        if content is None:
            return []

        file_findings: list[Finding] = []
        for rule in self.rules:
            try:
                file_findings.extend(rule.match(file_path, content))
            except Exception:
                continue
        return file_findings

    def _read_file(self, file_path: Path) -> Optional[str]:
        try:
            data = file_path.read_bytes()
            text = data.decode("utf-8")
            return text
        except (PermissionError, UnicodeDecodeError, OSError):
            return None
