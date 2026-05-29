from __future__ import annotations

import json
import sys

from skill_scan.models import ScanResult


def report(result: ScanResult, file=sys.stdout) -> None:
    json.dump(result.to_dict(), file, indent=2, default=str)
    print(file=file)


def report_sarif(result: ScanResult, file=sys.stdout) -> None:
    """Produce a SARIF 2.1.0 compliant output."""
    seen_rules: dict[str, dict] = {}
    sarif_results = []

    for finding in result.findings:
        if finding.rule_id not in seen_rules:
            seen_rules[finding.rule_id] = {
                "id": finding.rule_id,
                "name": finding.rule_id.split("/")[0],
                "shortDescription": {"text": finding.message},
                "fullDescription": {"text": finding.recommendation or finding.message},
                "defaultConfiguration": {"level": _sarif_level(finding.severity.name)},
                "properties": {"severity": finding.severity.name},
            }

        sarif_results.append({
            "ruleId": finding.rule_id,
            "ruleIndex": list(seen_rules.keys()).index(finding.rule_id),
            "level": _sarif_level(finding.severity.name),
            "message": {"text": finding.message},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": str(finding.file_path),
                        "uriBaseId": "%SRCROOT%",
                    },
                    "region": {
                        "startLine": finding.line_number,
                        "snippet": {
                            "text": finding.snippet[:200],
                        },
                    },
                }
            }],
            "properties": {
                "recommendation": finding.recommendation,
            },
        })

    sarif_doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "skill-scan",
                        "informationUri": "https://github.com/velvet-sojourner/skill-scan",
                        "version": "0.1.0",
                        "rules": list(seen_rules.values()),
                    }
                },
                "results": sarif_results,
                "columnKind": "utf16CodeUnits",
                "properties": {
                    "filesScanned": result.files_scanned,
                    "totalRules": result.total_rules,
                    "scanDuration": result.scan_time,
                },
            }
        ],
    }

    json.dump(sarif_doc, file, indent=2, default=str)
    print(file=file)


def _sarif_level(severity: str) -> str:
    mapping = {
        "CRITICAL": "error",
        "HIGH": "error",
        "MEDIUM": "warning",
        "LOW": "note",
        "INFO": "note",
    }
    return mapping.get(severity, "note")
