from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from skill_scan.engine import ScanEngine
from skill_scan.models import Severity
from skill_scan.rules import builtin_rules
from skill_scan.allowlist import Allowlist, AllowlistEntry

FIXTURES = Path(__file__).parent / "fixtures"
MIXED = FIXTURES / "mixed"
BENIGN = FIXTURES / "benign"
MALICIOUS = FIXTURES / "malicious"


class TestIntegration:

    def setup_method(self) -> None:
        self.engine = ScanEngine()

    def test_end_to_end_mixed_directory(self) -> None:
        result = self.engine.scan(MIXED)
        assert result.files_scanned >= 4
        assert result.total_findings > 0
        rule_ids = {f.rule_id for f in result.findings}
        assert "secrets/openai-key" in rule_ids
        assert "shell-injection/command-substitution" in rule_ids
        assert "exfiltration/read-then-http" in rule_ids

    def test_json_output_format(self) -> None:
        result = self.engine.scan(MALICIOUS)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "findings" in d
        assert "skill_path" in d
        assert "scan_time" in d
        assert "files_scanned" in d
        for f in d["findings"]:
            assert "rule_id" in f
            assert "severity" in f
            assert "file_path" in f
            assert "line_number" in f
        import json
        serialized = json.dumps(d)
        assert len(serialized) > 0

    def test_sarif_output_valid(self) -> None:
        from skill_scan.reporters.json_reporter import report_sarif
        import io
        result = self.engine.scan(MALICIOUS)
        buf = io.StringIO()
        report_sarif(result, buf)
        output = buf.getvalue()
        sarif = json.loads(output)
        assert sarif["version"] == "2.1.0"
        assert "$schema" in sarif
        assert len(sarif["runs"]) == 1
        run = sarif["runs"][0]
        assert run["tool"]["driver"]["name"] == "skill-scan"
        assert len(run["results"]) > 0

    def test_ci_mode_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "secret.sh").write_text("KEY=sk-abcdefghijklmnopqrstuvwxyz\n")
            result = self.engine.scan(d)
            assert result.total_findings > 0

        bad_dir = FIXTURES / "malicious"
        result = self.engine.scan(bad_dir)
        assert result.total_findings > 0

    def test_allowlist_suppresses_finding(self) -> None:
        from skill_scan.allowlist import Allowlist
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            allow_path = d / "allowlist.yaml"
            allow_path.write_text("""allowlist:
  - rule_id: secrets/*
    file_pattern: "**/secret.sh"
    reason: "Testing suppression"
""")
            skill_file = d / "secret.sh"
            skill_file.write_text("KEY=sk-abcdefghijklmnopqrstuvwxyz\n")

            result_no_allow = self.engine.scan(d)
            assert result_no_allow.total_findings > 0

            engine_with_allow = ScanEngine(allowlist=Allowlist(allow_path))
            result_allow = engine_with_allow.scan(d)
            assert result_allow.total_findings == 0

    def test_exclude_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "keep.py").write_text("x = 1")
            (d / "skip.py").write_text("x = 1")
            engine = ScanEngine(exclude_patterns=["**/skip.py"])
            result = engine.scan(d)
            assert result.files_scanned == 1

    def test_severity_filter(self) -> None:
        result = self.engine.scan(MALICIOUS, severity_filter=Severity.CRITICAL)
        for f in result.findings:
            assert f.severity >= Severity.CRITICAL

        result_high = self.engine.scan(MALICIOUS, severity_filter=Severity.HIGH)
        for f in result_high.findings:
            assert f.severity >= Severity.HIGH

    def test_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.engine.scan(Path(tmp))
            assert result.passed
            assert result.total_findings == 0

    def test_large_file(self) -> None:
        result = self.engine.scan(MIXED / "large_file.py")
        assert result.files_scanned >= 1
        assert isinstance(result.scan_time, float)

    def test_binary_file_skipped_gracefully(self) -> None:
        result = self.engine.scan(MIXED / "binary_file.bin")
        assert result.passed or result.total_findings == 0

    def test_rules_command_lists_all_8_rules(self) -> None:
        assert len(builtin_rules) == 8
        names = {r.name for r in builtin_rules}
        expected = {
            "shell-injection", "secrets", "code-exec",
            "obfuscation", "prompt-injection", "network",
            "file-access", "exfiltration",
        }
        assert names == expected

    def test_info_on_real_skill_md(self) -> None:
        from skill_scan.parsers.skill_md import SkillMDParser
        skill_file = BENIGN / "sample_skill.md"
        parser = SkillMDParser(skill_file).parse()
        assert parser.name is not None
        assert len(parser.sections) > 0
        assert "description" in parser.sections or "__header__" in parser.sections

    def test_cli_scan_json_output(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "skill_scan", "scan", str(BENIGN), "--output", "json"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "findings" in data

    def test_cli_rules_command(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "skill_scan", "rules"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "shell-injection" in result.stdout

    def test_nested_directory_scan(self) -> None:
        result = self.engine.scan(MIXED)
        nested_files = [f for f in result.findings if "nested" in str(f.file_path)]
        has_nested = any("nested" in str(f.file_path) for f in result.findings)
        assert result.files_scanned >= 4
