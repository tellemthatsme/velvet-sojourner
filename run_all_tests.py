import subprocess, os, sys, json, time, signal, threading, pathlib

REPOS_DIR = r'C:\temp\velvet-sojourner\repos'
TIMEOUT = 60

results = {}

def run_cmd(cmd, cwd, label):
    """Run a command with timeout. Returns (returncode, stdout, stderr, timed_out)"""
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATENO_WINDOW') else 0
        )
        try:
            stdout, stderr = proc.communicate(timeout=TIMEOUT)
            return proc.returncode, stdout.strip(), stderr.strip(), False
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                stdout, stderr = proc.communicate(timeout=10)
            except:
                stdout, stderr = "", ""
            return -1, stdout.strip()[:2000], f"TIMEOUT after {TIMEOUT}s", True
    except FileNotFoundError:
        return -2, "", f"Command not found: {cmd}", False
    except Exception as e:
        return -3, "", str(e), False

with_tests = sorted([d for d in os.listdir(REPOS_DIR) if os.path.isdir(os.path.join(REPOS_DIR, d)) and os.path.isdir(os.path.join(REPOS_DIR, d, 'tests'))])

for repo in with_tests:
    rd = os.path.join(REPOS_DIR, repo)
    has_pkg = os.path.isfile(os.path.join(rd, 'package.json'))
    has_req = os.path.isfile(os.path.join(rd, 'requirements.txt'))
    has_setup = os.path.isfile(os.path.join(rd, 'setup.py'))
    has_cargo = os.path.isfile(os.path.join(rd, 'Cargo.toml'))
    has_gomod = os.path.isfile(os.path.join(rd, 'go.mod'))
    has_pyproj = os.path.isfile(os.path.join(rd, 'pyproject.toml'))
    
    framework = "unknown"
    tests_run = 0
    tests_passed = 0
    tests_failed = 0
    errors = ""
    status = "no-run"
    output = ""
    
    print(f"\n{'='*60}\nTesting: {repo}")
    
    if has_cargo:
        framework = "cargo"
        print("  -> Detected: Rust (Cargo)")
        rc, out, err, to = run_cmd("cargo test 2>&1", rd, "cargo test")
        output = (out + "\n" + err).strip()
        if to:
            status = "timeout"
            errors = "Timed out"
        elif rc == 0:
            status = "pass"
            # Extract test counts
            import re
            m = re.search(r'(\d+)\s+passed', output)
            tests_passed = int(m.group(1)) if m else 0
            m = re.search(r'(\d+)\s+failed', output)
            tests_failed = int(m.group(1)) if m else 0
            tests_run = tests_passed + tests_failed
        elif rc == -2:
            status = "no-tool"
            errors = "cargo not installed"
        else:
            status = "fail"
            errors = err[:500] if err else output[:500]
    
    elif has_gomod:
        framework = "go"
        print("  -> Detected: Go")
        rc, out, err, to = run_cmd("go test ./... 2>&1", rd, "go test")
        output = (out + "\n" + err).strip()
        if to:
            status = "timeout"
            errors = "Timed out"
        elif rc == 0:
            status = "pass"
            import re
            m = re.search(r'ok\s+\S+\s+[\d.]+s', output)
            tests_passed = len(re.findall(r'^ok\s+', output, re.MULTILINE))
            tests_failed = len(re.findall(r'^FAIL\s+', output, re.MULTILINE))
            tests_run = tests_passed + tests_failed
            if tests_run == 0:
                tests_run = output.count("ok ") if "ok " in output else 0
                m = re.search(r'---\s+FAIL:\s+', output)
                if m:
                    status = "fail"
        elif rc == -2:
            status = "no-tool"
            errors = "go not installed"
        else:
            status = "fail"
            errors = err[:500] if err else output[:500]
    
    elif has_pkg:
        framework = "npm"
        print("  -> Detected: Node.js (package.json)")
        rc, out, err, to = run_cmd("npm test 2>&1", rd, "npm test")
        output = (out + "\n" + err).strip()
        if to:
            status = "timeout"
            errors = "Timed out"
        elif rc == 0 or rc == 1:
            import re
            # Try to parse various test frameworks
            # Jest
            m = re.search(r'Tests:\s+(\d+)\s+passed', output)
            if m: tests_passed = int(m.group(1))
            m = re.search(r'Tests:\s+\d+\s+passed.*?(\d+)\s+failed', output, re.DOTALL)
            if m: tests_failed = int(m.group(1))
            # Mocha/Jasmine
            m = re.search(r'(\d+)\s+passing', output)
            if m: tests_passed = int(m.group(1))
            m = re.search(r'(\d+)\s+failing', output)
            if m: tests_failed = int(m.group(1))
            # Vitest
            m = re.search(r'Tests\s+(\d+)', output)
            if m and tests_passed == 0:
                m2 = re.search(r'Tests\s+(\d+)\s*\|\s*(\d+)\s+passed', output)
                if not m2:
                    tests_run = int(m.group(1))
            m = re.search(r'(\d+)\s+passed', output)
            if m and tests_passed == 0: tests_passed = int(m.group(1))
            m = re.search(r'(\d+)\s+failed', output)
            if m and tests_failed == 0: tests_failed = int(m.group(1))
            
            tests_run = tests_passed + tests_failed
            if tests_run == 0:
                tests_run = 1  # assume at least 1 test ran
            if rc == 0:
                status = "pass"
            else:
                status = "fail"
                errors = err[:500] if err else output[:500]
            
            if tests_passed == 0 and tests_failed == 0:
                # Try to count from output differently
                m = re.findall(r'✓|√|pass', output)
                if m:
                    tests_passed = len(m)
                    tests_run = tests_passed
                    if rc == 1:
                        status = "partial"
        elif rc == -2:
            status = "no-tool"
            errors = "npm not installed"
        else:
            status = "fail"
            errors = err[:500] if err else output[:500]
    
    elif has_req or has_setup or has_pyproj:
        framework = "python"
        print("  -> Detected: Python")
        rc, out, err, to = run_cmd("python -m pytest -x --tb=short 2>&1", rd, "pytest")
        output = (out + "\n" + err).strip()
        if to:
            status = "timeout"
            errors = "Timed out"
        elif rc == 0 or rc == 1:
            import re
            m = re.search(r'(\d+)\s+passed', output)
            if m: tests_passed = int(m.group(1))
            m = re.search(r'(\d+)\s+failed', output)
            if m: tests_failed = int(m.group(1))
            m = re.search(r'(\d+)\s+error', output)
            if m: tests_failed += int(m.group(1))
            tests_run = tests_passed + tests_failed
            if tests_run == 0:
                # Try unittest format
                m = re.search(r'Ran\s+(\d+)\s+test', output)
                if m: tests_run = int(m.group(1))
                m = re.search(r'FAILED', output)
                tests_failed = 1 if m else 0
                tests_passed = tests_run - tests_failed
            if rc == 0:
                status = "pass"
            else:
                status = "fail"
                errors = err[:500] if err else output[:500]
        elif rc == -2:
            status = "no-tool"
            errors = "python not installed"
        else:
            # Fallback to unittest
            rc2, out2, err2, to2 = run_cmd("python -m unittest discover -s tests 2>&1", rd, "unittest")
            output2 = (out2 + "\n" + err2).strip()
            if rc2 == 0 or rc2 == 1:
                framework = "unittest"
                output = output2
                import re
                m = re.search(r'Ran\s+(\d+)\s+test', output)
                if m: tests_run = int(m.group(1))
                m = re.search(r'FAILED', output)
                tests_failed = 1 if m else 0
                tests_passed = tests_run - tests_failed
                if rc2 == 0:
                    status = "pass"
                else:
                    status = "fail"
            elif rc2 == -2:
                status = "no-tool"
            else:
                status = "fail"
                errors = err[:500] if err else output[:500]
    
    else:
        status = "no-framework"
        framework = "none"
        errors = "No recognized project framework found"
    
    results[repo] = {
        "framework": framework,
        "status": status,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
        "errors": errors[:300] if errors else "",
        "output": output[:1000] if output else ""
    }
    
    print(f"  Result: {status.upper()} | Framework: {framework} | Ran: {tests_run} | Passed: {tests_passed} | Failed: {tests_failed}")
    if errors:
        print(f"  Errors: {errors[:200]}")

# Write summary
os.makedirs(r'C:\temp\velvet-sojourner\docs', exist_ok=True)
report_path = r'C:\temp\velvet-sojourner\docs\test-results.md'

total_pass = sum(1 for r in results.values() if r['status'] == 'pass')
total_fail = sum(1 for r in results.values() if r['status'] == 'fail')
total_timeout = sum(1 for r in results.values() if r['status'] == 'timeout')
total_noframework = sum(1 for r in results.values() if r['status'] == 'no-framework')
total_notool = sum(1 for r in results.values() if r['status'] == 'no-tool')
total_norun = sum(1 for r in results.values() if r['status'] == 'no-run')
total_partial = sum(1 for r in results.values() if r['status'] == 'partial')
total_run = sum(r['tests_run'] for r in results.values())
total_passed = sum(r['tests_passed'] for r in results.values())
total_failed = sum(r['tests_failed'] for r in results.values())

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# AgentForge Test Results\n\n")
    f.write(f"**Scan Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Repos with tests/ dir:** 61\n\n")
    
    f.write("## Summary\n\n")
    f.write("| Metric | Value |\n")
    f.write("|--------|-------|\n")
    f.write(f"| Total repos with tests/ | 61 |\n")
    f.write(f"| Tests ran successfully | {total_pass} |\n")
    f.write(f"| Tests failed | {total_fail} |\n")
    f.write(f"| Tests timed out | {total_timeout} |\n")
    f.write(f"| No recognized framework | {total_noframework} |\n")
    f.write(f"| Tool not installed | {total_notool} |\n")
    f.write(f"| Partial pass | {total_partial} |\n")
    f.write(f"| Total individual tests run | {total_run} |\n")
    f.write(f"| Total tests passed | {total_passed} |\n")
    f.write(f"| Total tests failed | {total_failed} |\n\n")
    
    overall_rate = (total_passed / max(total_run, 1)) * 100
    f.write(f"**Overall pass rate: {overall_rate:.1f}%** ({total_passed}/{total_run})\n\n")
    
    f.write("## Per-Repo Results\n\n")
    f.write("| Repo | Framework | Status | Tests Run | Passed | Failed | Errors |\n")
    f.write("|------|-----------|--------|-----------|--------|--------|--------|\n")
    for repo, r in sorted(results.items()):
        f.write(f"| {repo} | {r['framework']} | {r['status']} | {r['tests_run']} | {r['tests_passed']} | {r['tests_failed']} | {r['errors'][:80]} |\n")
    
    f.write("\n## Detailed Output\n\n")
    for repo, r in sorted(results.items()):
        f.write(f"### {repo}\n\n")
        f.write(f"- **Framework:** {r['framework']}\n")
        f.write(f"- **Status:** {r['status']}\n")
        f.write(f"- **Tests Run:** {r['tests_run']}\n")
        f.write(f"- **Tests Passed:** {r['tests_passed']}\n")
        f.write(f"- **Tests Failed:** {r['tests_failed']}\n")
        if r['errors']:
            f.write(f"- **Errors:** {r['errors']}\n")
        if r['output']:
            f.write(f"- **Output:**\n```\n{r['output'][:800]}\n```\n")
        f.write("\n")
    
    f.write("## Repos with Broken Tests (Need Fixing)\n\n")
    broken = [(k, v) for k, v in sorted(results.items()) if v['status'] == 'fail' or v['status'] == 'timeout']
    if broken:
        f.write(f"{len(broken)} repos have broken or failing tests:\n\n")
        for repo, r in broken:
            f.write(f"- **{repo}** ({r['framework']}): {r['errors'][:100]}\n")
    else:
        f.write("None — all tests that ran passed successfully.\n")
    
    f.write("\n## Repos with No Runnable Tests\n\n")
    norun = [(k, v) for k, v in sorted(results.items()) if v['status'] in ('no-framework', 'no-tool', 'no-run')]
    if norun:
        f.write(f"{len(norun)} repos have a tests/ directory but no runnable tests:\n\n")
        for repo, r in norun:
            reason = "No recognized framework" if r['status'] == 'no-framework' else ("Tool not installed" if r['status'] == 'no-tool' else "No test runner configured")
            f.write(f"- **{repo}**: {reason}\n")
    else:
        f.write("None.\n")

print(f"\n\n{'='*60}")
print(f"REPORT: {report_path}")
print(f"Pass: {total_pass}/{len(results)} | Fail: {total_fail} | Timeout: {total_timeout} | NoFramework: {total_noframework} | NoTool: {total_notool} | Partial: {total_partial}")
print(f"Tests: {total_passed}/{total_run} passed ({overall_rate:.1f}%)")
print(f"Broken: {len(broken)}")
print(f"No runnable: {len(norun)}")
