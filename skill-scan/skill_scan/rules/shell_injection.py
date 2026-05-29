from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


class ShellInjectionRule(Rule):
    name = "shell-injection"
    description = "Detects shell command injection patterns in skill files"
    severity = Severity.HIGH

    _patterns: list[tuple[str, str, str]] = [
        (r'\$\(', "command-substitution", "Command substitution $(...) detected"),
        (r'`[^`\n]{10,}`', "backtick", "Backtick command execution detected"),
        (r'\beval\s*\(', "eval", "eval() call detected"),
        (r'\bos\.system\s*\(', "os-system", "os.system() call detected"),
        (r'\bsubprocess\s*\.', "subprocess", "subprocess module usage detected"),
        (r"'?\bsh\s*-c\s*'?", "sh-c", "sh -c shell execution detected"),
        (r"'?\bbash\s*-c\s*'?", "bash-c", "bash -c shell execution detected"),
        (r'\bos\.popen\s*\(', "os-popen", "os.popen() call detected"),
        (r'\bPopen\s*\(', "popen", "subprocess.Popen() call detected"),
        (r'\brun\s*\(', "run", "subprocess.run() call detected"),
        (r'\bcheck_output\s*\(', "check-output", "subprocess.check_output() call detected"),
        (r'\bcheck_call\s*\(', "check-call", "subprocess.check_call() call detected"),
    ]

    _skip_extensions = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".eot", ".ttf", ".pyc", ".exe", ".dll", ".so", ".zip", ".tar", ".gz"}

    def match(self, file_path: Path, content: str) -> list[Finding]:
        ext = file_path.suffix.lower()
        if ext in self._skip_extensions:
            return []

        if not content or len(content) < 4:
            return []

        findings: list[Finding] = []
        for pattern, rule_id, message in self._patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 30)
                snippet = content[start:end].strip()
                findings.append(Finding(
                    rule_id=f"shell-injection/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=snippet,
                    recommendation=(
                        "Avoid shell command execution in skill files. "
                        "Use native Python APIs or safe abstractions instead."
                    ),
                ))
        return findings
