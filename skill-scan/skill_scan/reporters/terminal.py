from __future__ import annotations

import sys

from skill_scan.models import ScanResult, Severity


_SEVERITY_ICONS = {
    Severity.CRITICAL: "[CRIT]",
    Severity.HIGH: "[HIGH]",
    Severity.MEDIUM: "[MED]",
    Severity.LOW: "[LOW]",
    Severity.INFO: "[INFO]",
}

_SEVERITY_COLORS = {
    Severity.CRITICAL: "\033[1;31m",
    Severity.HIGH: "\033[0;31m",
    Severity.MEDIUM: "\033[0;33m",
    Severity.LOW: "\033[0;34m",
    Severity.INFO: "\033[0;37m",
}

_RESET = "\033[0m"
_BOLD = "\033[1m"


def _color(text: str, severity: Severity) -> str:
    color = _SEVERITY_COLORS.get(severity, _RESET)
    return f"{color}{text}{_RESET}"


def report(result: ScanResult, *, verbose: bool = False, file=sys.stdout) -> None:
    summary_color = "\033[1;31m" if result.findings else "\033[1;32m"

    print(f"\n{_BOLD}skill-scan report{_RESET}", file=file)
    print(f"  Path:        {result.skill_path}", file=file)
    print(f"  Files:       {result.files_scanned}", file=file)
    print(f"  Rules:       {result.total_rules}", file=file)
    print(f"  Findings:    {summary_color}{len(result.findings)}{_RESET}", file=file)
    print(f"  Duration:    {result.scan_time:.2f}s", file=file)

    if not result.findings:
        print(f"\n  {_BOLD}All clean!{_RESET}", file=file)
        return

    print(f"\n  {'Severity':<10} {'Rule ID':<28} {'File':<45} {'Line':<6} Message", file=file)
    print(f"  {'-'*8:<10} {'-'*26:<28} {'-'*43:<45} {'-'*4:<6} -------", file=file)

    for finding in result.findings:
        icon = _SEVERITY_ICONS.get(finding.severity, "?")
        sev_str = f"{icon} {finding.severity.name}"
        colored_sev = _color(sev_str, finding.severity)
        fpath = str(finding.file_path.relative_to(result.skill_path) if finding.file_path.is_relative_to(result.skill_path) else finding.file_path)
        print(
            f"  {colored_sev:<20} {finding.rule_id:<28} {fpath:<45} {finding.line_number:<6} {finding.message}",
            file=file,
        )

        if verbose and finding.snippet:
            for snippet_line in finding.snippet.split("\n"):
                print(f"  {'':>20} {'':>28} {snippet_line}", file=file)
            print(file=file)

    print(file=file)
