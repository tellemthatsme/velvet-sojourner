from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


_SENSITIVE_WINDOWS_PATHS = (
    "C:\\\\Windows",
    "C:\\\\System32",
    "C:\\\\ProgramData",
)
_SENSITIVE_UNIX_PATHS = (
    "/etc/",
    "/root/",
    "/var/log/",
    "/dev/",
    "/proc/",
    "/sys/",
)
_SENSITIVE_DOT_DIRS = (".ssh", ".config", ".aws", ".kube", ".gnupg", ".docker")


class FileAccessRule(Rule):
    name = "file-access"
    description = "Detects file operations outside expected skill scope"
    severity = Severity.MEDIUM

    _patterns: list[tuple[str, str, str]] = [
        (r'\bopen\s*\(\s*["\']/etc/', "open-etc", "File open on /etc/ detected — system configuration access"),
        (r'\bopen\s*\(\s*["\']/root/', "open-root", "File open on /root/ detected — restricted directory access"),
        (r'\bopen\s*\(\s*["\']C:\\Windows', "open-windows", "File open on C:\\Windows detected — system directory access"),
        (r'\bshutil\.rmtree\s*\(', "shutil-rmtree", "shutil.rmtree() — recursive directory deletion detected"),
        (r'\bos\.remove\s*\(', "os-remove", "os.remove() — file deletion detected"),
        (r'\bos\.unlink\s*\(', "os-unlink", "os.unlink() — file deletion detected"),
        (r'\bPath\s*\([^)]*\)\s*\.(?:unlink|rmdir)\s*\(', "pathlib-delete", "Path.unlink()/rmdir() — file deletion via pathlib detected"),
    ]

    _skip_extensions = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff2", ".woff", ".eot", ".ttf", ".pyc", ".exe", ".dll", ".zip"}

    def _snip(self, content: str, match: re.Match) -> str:
        start = max(0, match.start() - 20)
        end = min(len(content), match.end() + 30)
        return content[start:end].strip()

    def match(self, file_path: Path, content: str) -> list[Finding]:
        ext = file_path.suffix.lower()
        if ext in self._skip_extensions:
            return []

        if not content:
            return []

        findings: list[Finding] = []

        for pattern, rule_id, message in self._patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                findings.append(Finding(
                    rule_id=f"file-access/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=self._snip(content, match),
                    recommendation=(
                        "Skill files should not access system directories. "
                        "Restrict file operations to the skill's own workspace."
                    ),
                ))

        self._check_system_path_access(file_path, content, findings)
        self._check_dot_dir_write(file_path, content, findings)
        self._check_sensitive_reads(file_path, content, findings)
        self._check_tempfile(file_path, content, findings)

        return findings

    def _check_system_path_access(self, file_path: Path, content: str, findings: list[Finding]) -> None:
        for p in _SENSITIVE_UNIX_PATHS:
            pattern = re.compile(r'open\s*\(\s*["\']' + re.escape(p), re.IGNORECASE)
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                findings.append(Finding(
                    rule_id="file-access/system-path",
                    severity=self.severity,
                    message=f"Sensitive system path access: open('{p}...')",
                    file_path=file_path,
                    line_number=line_num,
                    snippet=self._snip(content, match),
                    recommendation="Skills should not access sensitive system paths.",
                ))

    def _check_dot_dir_write(self, file_path: Path, content: str, findings: list[Finding]) -> None:
        for d in _SENSITIVE_DOT_DIRS:
            pattern = re.compile(
                r'(?:open|write|shutil\.copy)\s*\([^)]*' + re.escape(d),
                re.IGNORECASE,
            )
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                findings.append(Finding(
                    rule_id="file-access/dot-dir-write",
                    severity=Severity.HIGH,
                    message=f"Write operation to sensitive directory '{d}' detected",
                    file_path=file_path,
                    line_number=line_num,
                    snippet=self._snip(content, match),
                    recommendation=(
                        f"Writing to '{d}' may overwrite SSH keys, cloud credentials, "
                        "or Kubernetes configuration. Restrict file writes to safe locations."
                    ),
                ))

    def _check_sensitive_reads(self, file_path: Path, content: str, findings: list[Finding]) -> None:
        sensitive = ["/etc/shadow", "/etc/passwd", "/etc/environment", "/.env"]
        for path in sensitive:
            pattern = re.compile(r'open\s*\(\s*["\']' + re.escape(path), re.IGNORECASE)
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                findings.append(Finding(
                    rule_id="file-access/sensitive-read",
                    severity=Severity.CRITICAL,
                    message=f"Read of sensitive file '{path}' detected",
                    file_path=file_path,
                    line_number=line_num,
                    snippet=self._snip(content, match),
                    recommendation="Reading sensitive system files is dangerous and should never be done in a skill.",
                ))

    def _check_tempfile(self, file_path: Path, content: str, findings: list[Finding]) -> None:
        pattern = re.compile(r'tempfile\.(?:mkstemp|mkdtemp|NamedTemporaryFile|TemporaryDirectory)\s*\(')
        for match in pattern.finditer(content):
            line_num = content[:match.start()].count("\n") + 1
            findings.append(Finding(
                rule_id="file-access/tempfile",
                severity=Severity.LOW,
                message="Temporary file creation detected — verify files are cleaned up",
                file_path=file_path,
                line_number=line_num,
                snippet=self._snip(content, match),
                recommendation="Ensure temporary files are deleted after use to avoid filling disk space or leaking data.",
            ))
