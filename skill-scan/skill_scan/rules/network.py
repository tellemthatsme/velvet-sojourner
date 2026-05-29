from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


_SUSPICIOUS_TLDS = frozenset({
    ".gq", ".ml", ".cf", ".tk", ".ga", ".xyz", ".top", ".work",
    ".date", ".bid", ".loan", ".men", ".click", ".download",
    ".review", ".stream", ".trade",
})

_IP_PATTERN = re.compile(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


class NetworkRule(Rule):
    name = "network"
    description = "Detects unexpected network calls and suspicious outbound connections"
    severity = Severity.MEDIUM

    _patterns: list[tuple[str, str, str]] = [
        (r'\bcurl\s+', "curl", "curl command detected — potential outbound network call"),
        (r'\bwget\s+', "wget", "wget command detected — potential outbound network call"),
        (r'\bInvoke-WebRequest\b', "invoke-webrequest", "Invoke-WebRequest detected — PowerShell network call"),
        (r'\biwr\b', "iwr", "iwr (Invoke-WebRequest alias) detected"),
        (r'\brequests\.(?:get|post|put|delete|patch|head)\s*\(', "requests-http", "requests HTTP call detected"),
        (r'\burllib\.request\b', "urllib-request", "urllib.request module detected"),
        (r'\bhttpx\.(?:get|post|put|delete|patch)\s*\(', "httpx", "httpx HTTP call detected"),
        (r'\bsocket\.connect\s*\(', "socket-connect", "socket.connect() — raw network connection detected"),
        (r'\bsocket\.send\b', "socket-send", "socket.send() — outbound data transmission detected"),
        (r'\baiohttp\.ClientSession\b', "aiohttp-session", "aiohttp.ClientSession detected — async HTTP"),
        (r'\bwebsockets\.connect\b', "websockets-connect", "websockets.connect() — WebSocket connection detected"),
        (r'\bftp\.(?:connect|login|retrbinary|storbinary)\s*\(', "ftp-call", "FTP operation detected"),
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
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 30)
                snippet = content[start:end].strip()

                rec = (
                    "Unexpected network calls in skill files may exfiltrate data "
                    "or connect to command-and-control servers. "
                    "Verify the destination and purpose of each connection."
                )

                findings.append(Finding(
                    rule_id=f"network/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=snippet,
                    recommendation=rec,
                ))

        for match in _IP_PATTERN.finditer(content):
            line_num = content[:match.start()].count("\n") + 1
            start = max(0, match.start() - 20)
            end = min(len(content), match.end() + 30)
            snippet = content[start:end].strip()
            findings.append(Finding(
                rule_id="network/ip-url",
                severity=Severity.HIGH,
                message=f"URL with raw IP address detected: {match.group(0)}",
                file_path=file_path,
                line_number=line_num,
                snippet=snippet,
                recommendation="Raw IP addresses in URLs may bypass domain-based security controls. Verify the destination is legitimate.",
            ))

        url_pattern = re.compile(r"https?://[^\s()<>\"']+")
        for url_match in url_pattern.finditer(content):
            url = url_match.group(0)
            for tld in _SUSPICIOUS_TLDS:
                if tld in url:
                    line_num = content[:url_match.start()].count("\n") + 1
                    start = max(0, url_match.start() - 20)
                    end = min(len(content), url_match.end() + 30)
                    snippet = content[start:end].strip()
                    findings.append(Finding(
                        rule_id="network/suspicious-tld",
                        severity=Severity.HIGH,
                        message=f"URL with suspicious TLD '{tld}': {url}",
                        file_path=file_path,
                        line_number=line_num,
                        snippet=snippet,
                        recommendation=(
                            f"URLs ending in '{tld}' are associated with low-cost or untrusted domains. "
                            "Verify the destination before allowing network access from a skill."
                        ),
                    ))
                    break

        return findings
