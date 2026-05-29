from __future__ import annotations

import time
from pathlib import Path

from skill_scan.engine import ScanEngine
from skill_scan.models import Severity


def test_scan_speed():
    """Scan 100 files should complete in < 3 seconds."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(100):
            (Path(tmp) / f"file_{i}.py").write_text("x = 1\n")
        engine = ScanEngine()
        start = time.time()
        result = engine.scan(Path(tmp))
        elapsed = time.time() - start
        assert result.files_scanned >= 100
        assert elapsed < 3.0, f"Scanned 100 files in {elapsed:.2f}s (expected < 3s)"
