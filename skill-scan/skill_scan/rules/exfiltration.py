from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


class ExfiltrationRule(Rule):
    name = "exfiltration"
    description = "Detects data exfiltration patterns — reading files and sending data externally"
    severity = Severity.CRITICAL

    _patterns: list[tuple[str, str, str]] = [
        (r'(?:open|read)[\s\S]{0,100}(?:requests\.post|requests\.get|httpx\.|urllib\.)', "read-then-http",
         "File read followed by HTTP request — potential data exfiltration"),
        (r'(?:base64\.b64encode)[\s\S]{0,100}(?:requests\.post|requests\.get|httpx\.)', "encode-then-send",
         "Base64 encode followed by network send — potential encoded data exfiltration"),
        (r'(?:smtplib\.SMTP|smtp\.SMTP|sendmail|smtp\.sendmail)\s*\(', "smtp-send",
         "SMTP client detected — potential email-based exfiltration"),
        (r'\bsocket\.(?:sendto|send|connect)\s*\(.*?\b(?:\d{1,3}\.){3}\d{1,3}\b', "socket-exfil",
         "Socket connection to IP address — potential direct data exfiltration"),
        (r'(?:subprocess|os\.system|os\.popen)[\s\S]{0,100}(?:nslookup|dig|host)\s+.*?(?:\$\(|`|\{file)', "dns-exfil",
         "DNS query with embedded data — potential DNS exfiltration"),
        (r'\bMIME\w*\b.*\bsmtp\b', "mime-smtp",
         "MIME + SMTP pattern detected — potential email exfiltration with attachments"),
        (r'(?:open|read)[\s\S]{0,100}(?:socket\.|websocket\.)', "read-then-socket",
         "File read followed by socket operation — potential data exfiltration over socket"),
        (r'(?:urllib\.request|requests|httpx)[\s\S]{0,200}(?:open|read)', "http-then-read",
         "Network request near file read — potential exfiltration pipeline"),
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
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 40)
                snippet = content[start:end].strip()
                findings.append(Finding(
                    rule_id=f"exfiltration/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=snippet,
                    recommendation=(
                        "Data exfiltration patterns indicate a skill reading sensitive data "
                        "and sending it to external servers. This is a critical security concern. "
                        "Remove any code that reads files and transmits their contents externally."
                    ),
                ))

        self._check_same_function_exfil(file_path, content, findings)

        return findings

    def _check_same_function_exfil(self, file_path: Path, content: str, findings: list[Finding]) -> None:
        func_pattern = re.compile(
            r'def\s+\w+\s*\([^)]*\)\s*:.*?(?:open|read|base64\.b64encode).*?(?:requests|urllib|socket|httpx|smtp)',
            re.DOTALL,
        )
        for match in func_pattern.finditer(content):
            line_num = content[:match.start()].count("\n") + 1
            start = max(0, match.start() - 10)
            end = min(len(content), match.end() + 10)
            snippet = content[start:end].strip()
            findings.append(Finding(
                rule_id="exfiltration/same-function",
                severity=self.severity,
                message="File read and network call detected in same function — potential exfiltration pipeline",
                file_path=file_path,
                line_number=line_num,
                snippet=snippet[:300],
                recommendation=(
                    "A function that both reads files and makes network calls is a strong "
                    "exfiltration indicator. Separate I/O operations or justify each independently."
                ),
            ))
