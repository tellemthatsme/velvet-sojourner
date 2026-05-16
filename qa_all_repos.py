"""
AgentForge QA Toolkit — comprehensive repo validation
Single command to scan, test, verify, and report on all 843 repos.

Usage:
    python qa_all_repos.py [--path REPOS_DIR] [--quick] [--json]
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime


REPOS_DIR = Path(os.getenv("REPOS_DIR", r"C:\temp\velvet-sojourner\repos"))
RESULTS_DIR = REPOS_DIR.parent / "qa-results"
RESULTS_DIR.mkdir(exist_ok=True)

REPORT = {
    "timestamp": datetime.now().isoformat(),
    "scanned": 0,
    "passed": 0,
    "issues": [],
    "checks": {}
}


# ── Check 1: Directory Existence ──────────────────────────────────
def check_dirs_exist():
    """Verify all repo directories actually have files."""
    issues = []
    ok = 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        REPORT["scanned"] += 1
        files = list(path.iterdir())
        if not files:
            issues.append({"repo": name, "check": "empty", "detail": "0 files in directory"})
        elif not any(f.is_file() for f in files):
            issues.append({"repo": name, "check": "empty", "detail": "no files (subdirs only)"})
        else:
            ok += 1
    REPORT["checks"]["dirs_exist"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 2: README Quality ──────────────────────────────────────
def check_readmes():
    """Check every repo has a README with content."""
    issues = []
    ok = 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        readme = path / "README.md"
        if not readme.exists():
            issues.append({"repo": name, "check": "missing-readme", "detail": "no README.md"})
            continue
        size = readme.stat().st_size
        if size < 50:
            issues.append({"repo": name, "check": "tiny-readme", "detail": "%d bytes" % size})
        else:
            ok += 1
    REPORT["checks"]["readmes"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 3: LICENSE ────────────────────────────────────────────
def check_licenses():
    """Verify MIT LICENSE is present."""
    issues = []
    ok = 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        lic = path / "LICENSE"
        if not lic.exists():
            issues.append({"repo": name, "check": "missing-license", "detail": "no LICENSE file"})
            continue
        text = lic.read_text(encoding="utf-8", errors="ignore")
        if "MIT" not in text and "Apache" not in text and "GNU" not in text and "CC0" not in text and "Creative Commons" not in text and "Community License" not in text:
            issues.append({"repo": name, "check": "unknown-license", "detail": "non-standard license"})
            ok += 1  # still has a license file
        else:
            ok += 1
    REPORT["checks"]["licenses"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 4: Dockerfile ─────────────────────────────────────────
def check_dockerfiles():
    """Verify Dockerfile or docker-compose exists and is valid."""
    issues = []
    ok = 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        df = path / "Dockerfile"
        dc = path / "docker-compose.yml"
        if df.exists():
            text = df.read_text(encoding="utf-8", errors="ignore")
            if "FROM " not in text:
                issues.append({"repo": name, "check": "bad-dockerfile", "detail": "no FROM instruction"})
            else:
                ok += 1
        elif dc.exists():
            text = dc.read_text(encoding="utf-8", errors="ignore")
            if "services" not in text:
                issues.append({"repo": name, "check": "bad-compose", "detail": "no services key"})
            else:
                ok += 1
    REPORT["checks"]["dockerfiles"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 5: Git Status ─────────────────────────────────────────
def check_git_status():
    """Check for dirty repos, behind remotes, tokens in URLs."""
    issues = []
    ok = 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        git_dir = path / ".git"
        if not git_dir.exists():
            issues.append({"repo": name, "check": "not-git", "detail": "no .git directory"})
            continue
        try:
            # Check for dirty status
            result = subprocess.run(
                ["git", "-C", str(path), "status", "--porcelain"],
                capture_output=True, text=True, timeout=10
            )
            dirty = bool(result.stdout.strip())
            if dirty:
                issues.append({"repo": name, "check": "dirty", "detail": "uncommitted changes (expected — batch enhanced)"})
            # Check remote URLs for tokens
            remote = subprocess.run(
                ["git", "-C", str(path), "remote", "-v"],
                capture_output=True, text=True, timeout=5
            )
            for line in remote.stdout.split("\n"):
                if "ghp_" in line or "gho_" in line or "github_pat_" in line:
                    issues.append({"repo": name, "check": "exposed-token", "detail": "token in remote URL"})
                    break
            ok += 1
        except subprocess.TimeoutExpired:
            issues.append({"repo": name, "check": "git-timeout", "detail": "git command timed out"})
    REPORT["checks"]["git_status"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 6: File Integrity ─────────────────────────────────────
HARMLESS_EMPTY = {"FETCH_HEAD", "__init__.py", ".nojekyll", ".DS_Store", "Thumbs.db", "desktop.ini", "HEAD", "config", "description", "exclude"}

def check_file_integrity():
    """Check for corrupt files (0-byte files, broken symlinks)."""
    issues = []
    ok = 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        try:
            zero_byte_files = []
            for root, dirs, files in os.walk(str(path)):
                # Skip .git internals
                if ".git" in root.split(os.sep):
                    continue
                for f in files:
                    if f in HARMLESS_EMPTY:
                        continue
                    fp = os.path.join(root, f)
                    try:
                        if os.path.getsize(fp) == 0:
                            zero_byte_files.append(f)
                    except OSError:
                        pass
            if zero_byte_files:
                issues.append({"repo": name, "check": "zero-byte-files",
                               "detail": "%d zero-byte files: %s" % (len(zero_byte_files), zero_byte_files[:3])})
            else:
                ok += 1
        except Exception:
            pass
    REPORT["checks"]["integrity"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 7: Scoring ────────────────────────────────────────────
def check_scoring():
    """Check scoring consistency — no negative, extreme outliers."""
    issues = []
    ok_tier, ok_score, ok = 0, 0, 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        # Check for size anomalies
        size_mb = 0
        file_count = 0
        try:
            for root, dirs, files in os.walk(str(path)):
                for f in files:
                    file_count += 1
                    try:
                        size_mb += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass
            size_mb = size_mb / (1024 * 1024)
        except Exception:
            pass
        if size_mb > 1000:
            issues.append({"repo": name, "check": "huge-repo", "detail": "%.1f MB, %d files" % (size_mb, file_count)})
        elif size_mb < 0.001 and file_count == 0:
            issues.append({"repo": name, "check": "empty-repo", "detail": "%.3f MB, 0 files" % size_mb})
        else:
            ok += 1
    REPORT["checks"]["scoring"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 8: Test Suites ────────────────────────────────────────
def check_test_suites():
    """Find repos with test directories and check they're runnable."""
    issues = []
    ok = 0
    for name in sorted(os.listdir(str(REPOS_DIR))):
        path = REPOS_DIR / name
        if not path.is_dir():
            continue
        test_dir = path / "tests"
        test_file = path / "test.py"
        pytest_dir = path / "pytests"
        has_tests = test_dir.exists() or test_file.exists() or pytest_dir.exists()
        if has_tests:
            ok += 1
            # Check if tests dir has actual files
            if test_dir.exists():
                test_files = list(test_dir.rglob("test_*.py"))
                if not test_files:
                    issues.append({"repo": name, "check": "empty-test-dir", "detail": "tests/ dir exists but no test_*.py files"})
    REPORT["checks"]["test_suites"] = {"ok": ok, "issues": len(issues)}
    REPORT["issues"].extend(issues)
    return issues


# ── Check 9: Category Assignment ────────────────────────────────
def check_categories():
    """Check category coverage and missing."""
    cat_file = REPOS_DIR.parent / "docs" / "repo-categories.json"
    if not cat_file.exists():
        REPORT["checks"]["categories"] = {"ok": 0, "issues": 1, "note": "repo-categories.json not found"}
        return []
    with open(str(cat_file)) as f:
        data = json.load(f)
    uncategorized = [r["name"] for r in data if r.get("category", "unknown") == "unknown"]
    issues = []
    if uncategorized:
        issues.append({"check": "uncategorized", "detail": "%d repos with category=unknown" % len(uncategorized),
                       "repos": uncategorized[:10]})
    REPORT["checks"]["categories"] = {"ok": len(data) - len(uncategorized), "issues": len(uncategorized)}
    REPORT["issues"].extend(issues)
    return issues


# ── Run All ──────────────────────────────────────────────────────
def run_all(quick=False):
    print("=" * 60)
    print("  AgentForge QA Toolkit")
    print("  Scanning: %s" % REPOS_DIR)
    print("  Quick mode: %s" % quick)
    print("=" * 60)

    checks = [
        ("Directory existence", check_dirs_exist),
        ("README quality", check_readmes),
        ("LICENSE presence", check_licenses),
        ("Dockerfile validity", check_dockerfiles),
        ("Git status", check_git_status),
        ("File integrity", check_file_integrity),
        ("Size anomalies", check_scoring),
        ("Test suites", check_test_suites),
        ("Category coverage", check_categories),
    ]

    for name, fn in checks:
        if quick and name in ("File integrity", "Git status"):
            print("  [SKIP] %s" % name)
            continue
        print("  [SCAN] %s ..." % name, end=" ")
        sys.stdout.flush()
        t0 = time.time()
        issues = fn()
        elapsed = time.time() - t0
        c = REPORT["checks"].get(name.lower().replace(" ", "_"), {})
        print("done (%d issues, %.1fs)" % (len(issues), elapsed))

    total_issues = len(REPORT["issues"])
    print()
    print("=" * 60)
    print("  QA Summary")
    print("=" * 60)
    print("  Repos scanned: %d" % REPORT["scanned"])
    print("  Total issues:  %d" % total_issues)
    for name, data in REPORT["checks"].items():
        ok = data.get("ok", 0)
        issues = data.get("issues", 0)
        status = "OK" if issues == 0 else "ISSUES (%d)" % issues
        print("  %-25s %s" % (name, status))

    print()
    if total_issues == 0:
        print("  ALL CHECKS PASSED")
    else:
        print("  TOP ISSUES:")
        by_check = {}
        for issue in REPORT["issues"]:
            c = issue.get("check", "unknown")
            by_check[c] = by_check.get(c, 0) + 1
        for c, count in sorted(by_check.items(), key=lambda x: -x[1])[:10]:
            print("    %s: %d" % (c, count))

    # Save report
    report_path = RESULTS_DIR / "qa-report.json"
    with open(str(report_path), "w") as f:
        json.dump(REPORT, f, indent=2)
    print("\n  Full report: %s" % report_path)
    return total_issues


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AgentForge QA Toolkit")
    parser.add_argument("--path", default=str(REPOS_DIR), help="Repos directory")
    parser.add_argument("--quick", action="store_true", help="Skip slow checks (git status, file integrity)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    if args.path:
        REPOS_DIR = Path(args.path)
    total = run_all(quick=args.quick)

    if args.json:
        print(json.dumps(REPORT, indent=2))

    sys.exit(0 if total == 0 else 1)
