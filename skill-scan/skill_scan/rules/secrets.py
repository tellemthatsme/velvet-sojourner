from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


class SecretsRule(Rule):
    name = "secrets"
    description = "Detects hardcoded API keys, tokens, and credentials in skill files"
    severity = Severity.CRITICAL

    _patterns: list[tuple[str, str, str]] = [
        (r'gh[pousr]_[A-Za-z0-9]{36}', "github-token", "GitHub token detected"),
        (r'sk-[A-Za-z0-9]{20,}', "openai-key", "OpenAI API key detected"),
        (r'sk-ant-[A-Za-z0-9]{24,}', "anthropic-key", "Anthropic API key detected"),
        (r'AKIA[0-9A-Z]{16}', "aws-key", "AWS access key ID detected"),
        (r'(?i)(?:api[-_]?(?:key|secret)|secret[-_]?(?:key|access)|password|token)\s*[:=]\s*["\']?(?:[A-Za-z0-9+/]{20,}={0,2})["\']?', "generic-secret", "Potential secret or credential detected"),
        (r'(?i)(?:export|set)\s+[A-Z_]+_(?:API_KEY|SECRET|TOKEN|PASSWORD)\s*=', "env-secret", "Environment variable secret definition detected"),
    ]

    _skip_extensions = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff2", ".woff", ".eot", ".ttf", ".pyc", ".exe", ".dll", ".zip"}

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
                start = max(0, match.start() - 10)
                end = min(len(content), match.end() + 20)
                snippet = content[start:end].strip()
                findings.append(Finding(
                    rule_id=f"secrets/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=snippet,
                    recommendation=(
                        "Remove hardcoded secrets. Use environment variables "
                        "or a secrets manager instead."
                    ),
                ))
        return findings
