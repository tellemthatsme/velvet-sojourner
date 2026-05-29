import pytest
import sys
import os
import json
import tempfile
import time
import threading
from pathlib import Path


class TestIntegration:
    """End-to-end integration tests."""

    def _make_sample(self, tmpdir, content, filename="chatgpt_sample.txt"):
        fpath = Path(tmpdir) / filename
        fpath.write_text(content, encoding="utf-8")
        return fpath

    def _sample_conversation(self):
        return """User: Write a Python function to sort a list
Assistant: Here's a bubble sort implementation...
User: Can you optimize it?
Assistant: Use sorted() instead --- O(n log n).
"""

    def _sample_json(self):
        return json.dumps({
            "model": "gpt-4",
            "created_at": "2026-05-22",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
        })

    def _sample_html(self):
        return """<html><body><p>User: What is Python?</p><p>Assistant: Python is a language.</p></body></html>"""

    def test_full_pipeline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            inp = td / "input"
            out = td / "output"
            inp.mkdir()
            self._make_sample(inp, self._sample_conversation(), "chatgpt_test.txt")
            self._make_sample(inp, self._sample_json(), "api_export.json")
            from src.export_sorter import ExportSorter
            sorter = ExportSorter(inp, out)
            files = sorter.scan_input()
            assert len(files) == 2
            stats = sorter.run("md")
            assert stats.processed >= 1
            assert out.exists()
            md_files = list(out.rglob("*.md"))
            assert len(md_files) > 0

    def test_cli_analytics(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "main.py", "--cli", "--analytics", "--input", "tests", "--output", "tests"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0

    def test_cli_cost(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "main.py", "--cli", "--cost", "--input", "tests", "--output", "tests"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0

    def test_cli_help(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "main.py", "--cli", "--help"],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0
        assert "--analytics" in result.stdout
        assert "--cost" in result.stdout
        assert "--serve" in result.stdout

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.export_sorter import ExportSorter
            sorter = ExportSorter(Path(tmpdir), Path(tmpdir))
            files = sorter.scan_input()
            assert len(files) == 0
            stats = sorter.run("md")
            assert stats.processed == 0

    def test_mixed_formats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            inp = td / "input"
            out = td / "output"
            inp.mkdir()
            self._make_sample(inp, self._sample_conversation(), "conv1.txt")
            self._make_sample(inp, self._sample_json(), "conv2.json")
            self._make_sample(inp, self._sample_html(), "conv3.html")
            self._make_sample(inp, "Just a plain file here", "notes.md")
            from src.export_sorter import ExportSorter
            sorter = ExportSorter(inp, out)
            files = sorter.scan_input()
            assert len(files) == 4
            stats = sorter.run("md")
            assert stats.total_files == 4
            assert stats.processed >= 1

    def test_cli_serve_starts(self):
        import subprocess, socket
        port = 18766
        proc = subprocess.Popen(
            [sys.executable, "main.py", "--cli", "--serve", "--port", str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            import urllib.request
            for _ in range(20):
                try:
                    resp = urllib.request.urlopen(f"http://localhost:{port}", timeout=2)
                    assert resp.status == 200
                    break
                except Exception:
                    time.sleep(0.5)
            else:
                proc.kill()
                pytest.fail("Server did not start in time")
        finally:
            proc.kill()
            proc.wait()

    def test_dashboard_routes(self):
        import subprocess, urllib.request
        port = 18767
        proc = subprocess.Popen(
            [sys.executable, "main.py", "--cli", "--serve", "--port", str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            for _ in range(20):
                try:
                    urllib.request.urlopen(f"http://localhost:{port}", timeout=2)
                    break
                except Exception:
                    time.sleep(0.5)
            else:
                proc.kill()
                pytest.fail("Server did not start")

            routes = ["/", "/api/stats", "/api/trends", "/api/topics", "/api/costs", "/api/conversations"]

            for route in routes:
                resp = urllib.request.urlopen(f"http://localhost:{port}{route}", timeout=5)
                assert resp.status == 200, f"Route {route} returned {resp.status}"
        finally:
            proc.kill()
            proc.wait()

    def test_knowledge_base(self):
        from src.knowledge_base import KnowledgeBase
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            kb = KnowledgeBase(db_path)
            kb.add_conversation({
                "title": "Python coding session",
                "content": "How to write Python code",
                "source": "chatgpt",
                "topic": "code",
                "tags": "python code",
            })
            kb.add_conversation({
                "title": "React component design",
                "content": "Building React components",
                "source": "claude",
                "topic": "design",
                "tags": "react ui",
            })
            results = kb.search("python")
            assert len(results) > 0
            assert any("python" in r.get("title", "").lower() for r in results)
            kb2 = KnowledgeBase(db_path)
            results2 = kb2.search("react")
            assert len(results2) > 0
        finally:
            os.unlink(db_path)

    def test_cost_tracker(self):
        from src.analyzers.cost_tracker import CostAnalyzer, estimate_cost, estimate_tokens
        conv = {
            "id": "test1",
            "source": "chatgpt",
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Write a long essay about AI." * 100},
                {"role": "assistant", "content": "Here is the essay." * 100},
            ]
        }
        ca = CostAnalyzer()
        result = ca.analyze_conversation(conv)
        assert result["tokens"] > 0
        assert result["message_count"] == 2
        batch = ca.analyze_batch([conv])
        assert batch["total"] == 1
        assert batch["total_tokens"] > 0
        assert batch["total_cost"] > 0
        assert estimate_tokens("hello") == 1
        assert estimate_cost("hello", "gpt-4") >= 0
        assert estimate_cost("hello", "nonexistent-model") == 0.0

    def test_trend_analyzer(self):
        from src.analyzers.trend_analyzer import TrendAnalyzer
        convs = [
            {"date": "2026-01-01", "source": "chatgpt", "topic": "code", "model": "gpt-4", "messages": []},
            {"date": "2026-01-02", "source": "claude", "topic": "design", "model": "claude-3-sonnet", "messages": []},
            {"date": "2026-01-03", "source": "chatgpt", "topic": "code", "model": "gpt-4", "messages": []},
        ]
        ta = TrendAnalyzer()
        result = ta.analyze(convs)
        assert result["total_conversations"] == 3
        assert len(result["daily"]) == 3
        assert result["date_range"]["start"] == "2026-01-01"
        assert result["date_range"]["end"] == "2026-01-03"

    def test_model_detector(self):
        from src.analyzers.model_detector import ModelDetector
        md = ModelDetector()
        assert md.detect("using gpt-4-turbo now")[0] == "gpt-4-turbo"
        assert md.detect("claude-3-opus is great")[0] == "claude-3-opus"
        assert md.detect("random text")[0] == "unknown"
        assert md.detect_source_model("chatgpt") == "gpt-4"
        assert md.detect_source_model("claude") == "claude-3-sonnet"
        assert md.detect_source_model("unknown") == "unknown"

    def test_session_stats(self):
        from src.analyzers.session_stats import compute
        convs = [
            {"id": "1", "source": "chatgpt", "topic": "code", "date": "2026-01-01",
             "messages": [{"role": "user", "content": "hello world"}]},
            {"id": "2", "source": "claude", "topic": "design", "date": "2026-01-02",
             "messages": [{"role": "user", "content": "test"}, {"role": "assistant", "content": "response"}]},
        ]
        stats = compute(convs)
        assert stats.total_conversations == 2
        assert stats.total_messages == 3
        assert stats.avg_messages_per_conv == 1.5
        assert stats.most_active_source == "chatgpt"

    def test_analytics_report(self):
        from src.exporters.analytics_report import AnalyticsReport
        stats = {"total_conversations": 10, "total_messages": 50, "avg_messages_per_conv": 5.0,
                 "avg_length_chars": 200.0, "most_active_source": "chatgpt",
                 "most_common_topics": [("code", 5), ("design", 3), ("general", 2)],
                 "top_keywords": [("python", 10), ("react", 5)]}
        trends = {"daily": [{"date": "2026-01-01", "count": 5}], "date_range": {"start": "2026-01-01", "end": "2026-01-01"}}
        costs = {"total_cost": 0.50, "by_model": {"gpt-4": {"total_cost": 0.50}}}
        report = AnalyticsReport()
        html = report.generate_html(stats, trends, costs)
        assert "10" in html
        assert "Total Messages" in html
        csv = report.generate_csv(stats)
        assert "total_conversations,10" in csv

    def test_csv_export(self):
        from src.exporters.csv_export import export_conversations_csv
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = Path(tmpdir) / "export.csv"
            convs = [{"id": "1", "title": "Test", "date": "2026-01-01", "source": "chatgpt",
                      "model": "gpt-4", "topic": "code", "messages": [{"role": "user", "content": "hello"}]}]
            export_conversations_csv(convs, str(fpath))
            content = fpath.read_text(encoding="utf-8")
            assert "id,title,date" in content
            assert "Test" in content
