"""Quick smoke test to verify everything works end-to-end."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def smoke_test():
    errors = []

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)

        (d / "SKILL.md").write_text("# My Skill\nA benign skill.\n")

        skill2 = d / "bad_skill"
        skill2.mkdir()
        (skill2 / "config.sh").write_text("OPENAI_API_KEY=sk-abc123def456ghi789jkl0\n")

        r = subprocess.run(
            [sys.executable, "-m", "skill_scan", "scan", str(d), "--output", "json"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            errors.append(f"scan clean exited {r.returncode}: {r.stderr}")

        r2 = subprocess.run(
            [sys.executable, "-m", "skill_scan", "scan", str(skill2), "--output", "json"],
            capture_output=True, text=True, timeout=30,
        )

        r3 = subprocess.run(
            [sys.executable, "-m", "skill_scan", "rules"],
            capture_output=True, text=True, timeout=30,
        )
        if "shell-injection" not in r3.stdout:
            errors.append("rules list missing shell-injection")

        r4 = subprocess.run(
            [sys.executable, "-m", "skill_scan", "scan", str(skill2), "--ci"],
            capture_output=True, text=True, timeout=30,
        )
        if r4.returncode != 1:
            errors.append(f"ci mode should exit 1 with findings, got {r4.returncode}")

        empty = d / "empty"
        empty.mkdir()
        r5 = subprocess.run(
            [sys.executable, "-m", "skill_scan", "scan", str(empty), "--ci"],
            capture_output=True, text=True, timeout=30,
        )
        if r5.returncode != 0:
            errors.append(f"empty dir should exit 0, got {r5.returncode}")

    if errors:
        print("SMOKE TEST FAILED:")
        for e in errors:
            print(f"  FAIL: {e}")
        sys.exit(1)
    else:
        print("SMOKE TEST PASSED")


if __name__ == "__main__":
    smoke_test()
