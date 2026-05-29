from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


class ObfuscationRule(Rule):
    name = "obfuscation"
    description = "Detects obfuscated code, encoded strings, and suspicious encoding patterns"
    severity = Severity.MEDIUM

    _patterns: list[tuple[str, str, str]] = [
        (r'base64\.b64decode\s*\(', "b64decode", "base64.b64decode() — potential payload obfuscation"),
        (r'base64\.b64encode\s*\(', "b64encode", "base64.b64encode() — payload encoding detected"),
        (r'base64\.urlsafe_b64decode', "b64url-decode", "Base64 URL-safe decode — potential payload obfuscation"),
        (r'(?i)\bbytes\.fromhex\b', "bytes-fromhex", "bytes.fromhex() — hex decoding detected"),
        (r"\b[xX]['\"][0-9a-fA-F]{20,}['\"]", "hex-string", "Hex-encoded string detected (>20 chars)"),
        (r'\'[A-Za-z0-9+/]{40,}={0,2}\'', "b64-string", "Base64-encoded string detected (>40 chars)"),
        (r'"[A-Za-z0-9+/]{40,}={0,2}"', "b64-string-double", "Base64-encoded string detected (>40 chars)"),
        (r'(?i)(?:rot13|rot_13|crypt|codecs\.encode)\s*\(', "encoding-func", "Suspicious encoding function detected"),
        (r'(?i)(?:decompress|uncompress|zlib|gzip)\.(?:decompress|open)\s*\(', "compression-func", "Compression/decompression used — potential payload extraction"),
        (r'\'\\\\x[0-9a-f]{2}\'', "escaped-hex", "Escaped hex characters detected — potential obfuscation"),
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
                    rule_id=f"obfuscation/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=snippet,
                    recommendation=(
                        "Obfuscated code is a strong indicator of malicious intent. "
                        "Replace with clear, readable code using standard libraries."
                    ),
                ))
        return findings
