from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class Severity(enum.IntEnum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_string(cls, s: str) -> Severity | None:
        norm = s.strip().upper()
        for member in cls:
            if member.name == norm:
                return member
        return None


@dataclass
class Finding:
    rule_id: str
    severity: Severity
    message: str
    file_path: Path
    line_number: int
    snippet: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.name,
            "message": self.message,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "snippet": self.snippet,
            "recommendation": self.recommendation,
        }


@dataclass
class ScanResult:
    skill_path: Path
    findings: list[Finding] = field(default_factory=list)
    scan_time: float = 0.0
    total_rules: int = 0
    files_scanned: int = 0

    def __post_init__(self) -> None:
        if not self.findings:
            self.findings = []

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def passed(self) -> bool:
        return len(self.findings) == 0

    def to_dict(self) -> dict:
        return {
            "skill_path": str(self.skill_path),
            "scan_time": self.scan_time,
            "total_rules": self.total_rules,
            "total_findings": self.total_findings,
            "files_scanned": self.files_scanned,
            "passed": self.passed,
            "findings": [f.to_dict() for f in self.findings],
        }
