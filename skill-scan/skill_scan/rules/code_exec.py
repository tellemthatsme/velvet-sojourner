from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


class CodeExecRule(Rule):
    name = "code-exec"
    description = "Detects arbitrary code execution patterns in skill files"
    severity = Severity.CRITICAL

    _patterns: list[tuple[str, str, str]] = [
        (r'\beval\s*\(', "eval", "eval() — arbitrary code execution detected"),
        (r'\bexec\s*\(', "exec", "exec() — arbitrary code execution detected"),
        (r'\bcompile\s*\(', "compile", "compile() — dynamic code compilation detected"),
        (r'\b__import__\s*\(', "import", "__import__() — dynamic import detected"),
        (r'\bimportlib\.import_module\s*\(', "importlib", "importlib.import_module() — dynamic import detected"),
        (r'\bos\.popen\s*\(', "os-popen", "os.popen() — shell execution detected"),
        (r'\bexecfile\s*\(', "execfile", "execfile() — file-based code execution detected (Python 2)"),
        (r'\brunpy\b', "runpy", "runpy module — code execution via module path detected"),
        (r'\bcode\.interact\b', "code-interact", "code.interact() — interactive interpreter detected"),
        (r'\bpty\.spawn\b', "pty-spawn", "pty.spawn() — pseudo-terminal spawn detected"),
    ]

    def match(self, file_path: Path, content: str) -> list[Finding]:
        if not content:
            return []

        findings: list[Finding] = []
        for pattern, rule_id, message in self._patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 30)
                snippet = content[start:end].strip()
                findings.append(Finding(
                    rule_id=f"code-exec/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=snippet,
                    recommendation=(
                        "Avoid dynamic code execution. Use safer alternatives "
                        "like restricted Python runners or static imports."
                    ),
                ))
        return findings
