"""Quick smoke test -- run after build to verify everything works."""
import subprocess, sys, json, os
from pathlib import Path


def smoke():
    errors = []

    r = subprocess.run([sys.executable, "main.py", "--cli", "--help"], capture_output=True, text=True)
    if "--analytics" not in r.stdout:
        errors.append("--help missing --analytics")

    for mod in ["src.analyzers.cost_tracker", "src.api.routes", "src.web.app"]:
        r = subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"import {mod}: {r.stderr}")

    r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short",
                        "-k", "not serve_starts and not dashboard_routes"],
                       capture_output=True, text=True)
    if "passed" not in r.stdout or "failed" in r.stdout:
        errors.append("some tests failed")

    if errors:
        print("SMOKE TEST FAILED:")
        for e in errors:
            print(f"  X {e}")
        sys.exit(1)
    else:
        print("SMOKE TEST PASSED V")


if __name__ == "__main__":
    smoke()
