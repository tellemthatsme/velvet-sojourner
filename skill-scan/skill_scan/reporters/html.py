from __future__ import annotations

import html as html_mod
import sys
from pathlib import Path

from skill_scan.models import ScanResult, Severity


_SEVERITY_COLORS_HEX = {
    Severity.CRITICAL: "#dc2626",
    Severity.HIGH: "#ea580c",
    Severity.MEDIUM: "#ca8a04",
    Severity.LOW: "#2563eb",
    Severity.INFO: "#6b7280",
}


def report(result: ScanResult, title: str = "skill-scan Report", file=sys.stdout) -> None:
    rows_html = ""
    for finding in result.findings:
        color = _SEVERITY_COLORS_HEX.get(finding.severity, "#6b7280")
        fpath = str(finding.file_path)
        snippet_esc = html_mod.escape(finding.snippet[:300])
        rows_html += f"""
        <tr>
            <td><span class="badge" style="background:{color}">{finding.severity.name}</span></td>
            <td>{html_mod.escape(finding.rule_id)}</td>
            <td class="msg">{html_mod.escape(finding.message)}</td>
            <td>{html_mod.escape(fpath)}:{finding.line_number}</td>
        </tr>
        <tr class="snippet-row">
            <td colspan="4"><pre>{snippet_esc}</pre></td>
        </tr>
        """

    summary_class = "fail" if result.findings else "pass"
    summary_text = f"{len(result.findings)} finding(s)" if result.findings else "All clean"

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_mod.escape(title)}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; color: #f1f5f9; }}
  .summary {{ display: flex; gap: 2rem; margin: 1rem 0 1.5rem; flex-wrap: wrap; }}
  .summary-item {{ background: #1e293b; padding: 0.75rem 1.25rem; border-radius: 0.5rem; }}
  .summary-item .label {{ font-size: 0.75rem; color: #94a3b8; }}
  .summary-item .value {{ font-size: 1.25rem; font-weight: 700; }}
  .summary-item .value.pass {{ color: #22c55e; }}
  .summary-item .value.fail {{ color: #ef4444; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 2px solid #334155; font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
  td {{ padding: 0.5rem; border-bottom: 1px solid #1e293b; font-size: 0.875rem; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 9999px; color: #fff; font-size: 0.75rem; font-weight: 600; }}
  .msg {{ color: #cbd5e1; }}
  .snippet-row td {{ padding: 0 0.5rem 0.75rem; }}
  .snippet-row pre {{ background: #1e293b; padding: 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; color: #a5b4fc; overflow-x: auto; margin: 0; }}
  .snippet-row:last-child td {{ border-bottom: none; }}
</style>
</head>
<body>
<h1>{html_mod.escape(title)}</h1>
<div class="summary">
  <div class="summary-item">
    <div class="label">Result</div>
    <div class="value {summary_class}">{summary_text}</div>
  </div>
  <div class="summary-item">
    <div class="label">Files Scanned</div>
    <div class="value">{result.files_scanned}</div>
  </div>
  <div class="summary-item">
    <div class="label">Rules Applied</div>
    <div class="value">{result.total_rules}</div>
  </div>
  <div class="summary-item">
    <div class="label">Duration</div>
    <div class="value">{result.scan_time:.2f}s</div>
  </div>
</div>
<table>
<thead>
  <tr>
    <th>Severity</th>
    <th>Rule</th>
    <th>Message</th>
    <th>Location</th>
  </tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>"""

    print(doc, file=file)
