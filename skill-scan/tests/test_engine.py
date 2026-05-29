from __future__ import annotations

from pathlib import Path

import pytest

from skill_scan.engine import ScanEngine
from skill_scan.models import Severity, ScanResult
from skill_scan.rules.base import Rule, RuleRegistry

FIXTURES = Path(__file__).parent / "fixtures"
BENIGN = FIXTURES / "benign"
MALICIOUS = FIXTURES / "malicious"


class TestScanEngine:

    def setup_method(self) -> None:
        self.engine = ScanEngine()

    def test_scan_nonexistent_path(self) -> None:
        with pytest.raises(FileNotFoundError):
            self.engine.scan(Path("/nonexistent/path"))

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        result = self.engine.scan(tmp_path)
        assert isinstance(result, ScanResult)
        assert result.passed
        assert result.total_findings == 0

    def test_scan_benign_skill(self) -> None:
        result = self.engine.scan(BENIGN)
        assert result.total_findings == 0
        assert result.passed
        assert result.files_scanned >= 2

    def test_scan_malicious_shell(self) -> None:
        result = self.engine.scan(MALICIOUS / "shell_inject.sh")
        assert result.total_findings > 0
        assert not result.passed

        rule_ids = {f.rule_id for f in result.findings}
        assert "shell-injection/command-substitution" in rule_ids or \
               "shell-injection/backtick" in rule_ids or \
               "shell-injection/sh-c" in rule_ids

    def test_scan_malicious_secrets(self) -> None:
        result = self.engine.scan(MALICIOUS / "secrets.sh")
        assert result.total_findings > 0
        assert not result.passed

        rule_ids = {f.rule_id for f in result.findings}
        matches = {"secrets/openai-key", "secrets/github-token",
                    "secrets/anthropic-key", "secrets/aws-key",
                    "secrets/generic-secret"}
        assert rule_ids & matches, f"No secret rules matched. Got: {rule_ids}"

    def test_scan_malicious_code_exec(self) -> None:
        result = self.engine.scan(MALICIOUS / "code_exec.py")
        assert result.total_findings > 0
        assert not result.passed

        rule_ids = {f.rule_id for f in result.findings}
        assert "code-exec/eval" in rule_ids
        assert "code-exec/importlib" in rule_ids or "code-exec/import" in rule_ids

    def test_scan_malicious_obfuscation(self) -> None:
        result = self.engine.scan(MALICIOUS / "obfuscation.py")
        assert result.total_findings > 0
        assert not result.passed

        rule_ids = {f.rule_id for f in result.findings}
        assert "obfuscation/b64decode" in rule_ids or \
               "obfuscation/bytes-fromhex" in rule_ids

    def test_severity_filter_critical_only(self) -> None:
        result = self.engine.scan(
            MALICIOUS,
            severity_filter=Severity.CRITICAL,
        )
        for finding in result.findings:
            assert finding.severity >= Severity.CRITICAL

    def test_severity_filter_high_plus(self) -> None:
        result = self.engine.scan(
            MALICIOUS,
            severity_filter=Severity.HIGH,
        )
        for finding in result.findings:
            assert finding.severity >= Severity.HIGH

    def test_severity_filter_medium_plus(self) -> None:
        result = self.engine.scan(
            MALICIOUS,
            severity_filter=Severity.MEDIUM,
        )
        for finding in result.findings:
            assert finding.severity >= Severity.MEDIUM

    def test_scan_result_counts(self) -> None:
        result = self.engine.scan(MALICIOUS / "shell_inject.sh")
        assert result.total_rules > 0
        assert result.files_scanned == 1
        assert result.scan_time > 0

    def test_scan_result_to_dict(self) -> None:
        result = self.engine.scan(MALICIOUS / "code_exec.py")
        d = result.to_dict()
        assert "findings" in d
        assert isinstance(d["findings"], list)
        assert d["passed"] is False
        assert d["scan_time"] > 0


class TestRuleRegistry:

    def test_singleton(self) -> None:
        r1 = RuleRegistry()
        r2 = RuleRegistry()
        assert r1 is r2

    def test_register_and_list(self) -> None:
        registry = RuleRegistry()
        registry._rules.clear()
        class FakeRule(Rule):
            name = "fake"
            description = "fake rule"
            severity = Severity.INFO
            def match(self, file_path, content):
                return []
        registry.register(FakeRule())
        assert len(registry.rules) == 1
        assert registry.rules[0].name == "fake"

    def test_register_invalid(self) -> None:
        registry = RuleRegistry()
        with pytest.raises(TypeError):
            registry.register("not-a-rule")  # type: ignore


class TestFinding:
    def test_to_dict(self) -> None:
        from skill_scan.models import Finding, Severity
        f = Finding(
            rule_id="test/rule",
            severity=Severity.HIGH,
            message="Test finding",
            file_path=Path("/tmp/test.py"),
            line_number=42,
            snippet="dangerous_code()",
            recommendation="Fix it",
        )
        d = f.to_dict()
        assert d["rule_id"] == "test/rule"
        assert d["severity"] == "HIGH"
        assert d["line_number"] == 42
