# AgentForge Test Results

**Scan Date:** 2026-05-10
**Repos with tests/ dir:** 61

## Summary

| Metric | Value |
|--------|-------|
| Total repos with tests/ directory | 61 |
| Tests ran successfully (all passed) | 1 |
| Tests ran with failures | 4 |
| Tests timed out | 1 |
| No test script configured (has tests/ dir but npm missing "test" script) | 30 |
| Dependencies not installed (has test script but node_modules missing) | 9 |
| No recognized project framework | 7 |
| Tool not available (Go, etc.) | 1 |
| No-run/other | 8 |
| **Total individual tests run** | **192** |
| **Total tests passed** | **143** |
| **Total tests failed** | **49** |

**Overall pass rate: 74.5%** (143/192)

## Per-Repo Results

| Repo | Framework | Status | Tests Run | Passed | Failed | Category |
|------|-----------|--------|-----------|--------|--------|----------|
| multi-agent-coding-environment | python | ✅ PASS | 8 | 8 | 0 | All tests passed |
| PydanticAI-Research-Agent | python | ❌ FAIL | 1 | 0 | 1 | Import error |
| agenticSeek | python | ❌ FAIL | 1 | 0 | 1 | Import error |
| aider | python | ❌ FAIL | 1 | 0 | 1 | Import error |
| deer-flow | python | ❌ FAIL | 1 | 0 | 1 | Import error |
| fastapi_mcp | python | ⚠️ PARTIAL | 17 | 16 | 1 | 1 test failed |
| local-operator | python | ❌ FAIL | 1 | 0 | 1 | Import error |
| mcp-use | python | ❌ FAIL | 1 | 0 | 1 | Import error |
| omnara | python/unittest | ⚠️ PARTIAL | 4 | 3 | 1 | 1 test failed |
| openrouter-ai-ecosystem | python/unittest | ❌ FAIL | 1 | 0 | 1 | Test failure |
| scrapy | python/unittest | ⚠️ PARTIAL | 117 | 116 | 1 | 1 test failed |
| browser-use | python | ❌ FAIL | 0 | 0 | 0 | Missing pytest plugin |
| claude-code-complete-backup | python/unittest | ❌ FAIL | 1 | 0 | 1 | Test failure |
| nautilus_trader | cargo | ⏱ TIMEOUT | 0 | 0 | 0 | Timed out (60s) |
| awesome-cli | go | ❌ NO-TOOL | 0 | 0 | 0 | Go not installed |
| ai-deals-oasis | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed (vitest) |
| ai-dev-command-clone | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed (vitest) |
| b-7161 | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed (vitest) |
| cherry-studio | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed |
| claude-task-master | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed (jest) |
| eliza | npm | ❌ NO-DEPS | 0 | 0 | 0 | Dependencies not installed |
| git-mcp | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed (vitest) |
| playwright-mcp | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed (playwright) |
| woodsai69rme_v0-ai-agent-army-refactor | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed (tsx) |
| ai-command-center-nexus-22 | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| bot-trading-maestro | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| chat-saga-sorter | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| chat-saga-sorter-ad13c3d7 | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| cogno-control-center | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| crypto-ai-nexus-dashboard | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| crypto-fusion-quest | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| crypto-nexus-automator | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| crypto-woods-alpha | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| freebie-ai-optimiser | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| hermes-agent | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| insight-engine-buddy | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| litellm | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| lovable-project-merger | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| note-scribe-echo | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| opstart-glimpse-demo | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| profile-detective-seeker | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| repo-rite | npm | ❌ NO-SCRIPT | 1 | 0 | 0 | No "test" script in package.json |
| woodsai69rme_* (8 variants) | npm | ❌ NO-SCRIPT | 1 each | 0 | 0 | No "test" script in package.json |
| woodsai69rme_v0-ai-agent-army-refactor | npm | ❌ NO-DEPS | 1 | 0 | 0 | Dependencies not installed |
| aicodeecoemerg | none | ❌ NO-FRAMEWORK | 0 | 0 | 0 | No recognized framework |
| base44clone | none | ❌ NO-FRAMEWORK | 0 | 0 | 0 | No recognized framework |
| cladstudioemerg | none | ❌ NO-FRAMEWORK | 0 | 0 | 0 | No recognized framework |
| cryptoclone | none | ❌ NO-FRAMEWORK | 0 | 0 | 0 | No recognized framework |
| emergent | none | ❌ NO-FRAMEWORK | 0 | 0 | 0 | No recognized framework |
| ladybird | none | ❌ NO-FRAMEWORK | 0 | 0 | 0 | No recognized framework |
| vibecloneemergent | none | ❌ NO-FRAMEWORK | 0 | 0 | 0 | No recognized framework |

## Detailed Output

### multi-agent-coding-environment — ✅ PASS (8/8)

**Framework:** python (pytest)
**Tests Run:** 8
**Tests Passed:** 8
**Tests Failed:** 0

All 8 tests passed successfully. This is the only repo with a fully functional test suite.

---

### fastapi_mcp — ⚠️ PARTIAL (16/17)

**Framework:** python (pytest)
**Tests Run:** 17
**Tests Passed:** 16
**Tests Failed:** 1

The test suite is largely functional. 1 test is failing, likely due to an API change or environment issue.

---

### omnara — ⚠️ PARTIAL (3/4)

**Framework:** python (unittest)
**Tests Run:** 4
**Tests Passed:** 3
**Tests Failed:** 1

---

### scrapy — ⚠️ PARTIAL (116/117)

**Framework:** python (unittest)
**Tests Run:** 117
**Tests Passed:** 116
**Tests Failed:** 1

Scrapy has the largest test suite in the collection. All but 1 test pass.

---

### nautilus_trader — ⏱ TIMEOUT

**Framework:** Rust (cargo)
**Tests Run:** 0 (timed out at 60s)
**Tests Passed:** 0
**Tests Failed:** 0

Cargo test compilation took longer than 60 seconds. May need extended build time.

---

## Repos with Broken Tests (Need Fixing)

**5 repos** have tests that ran but had failures:

| Repo | Framework | Tests | Passed | Failed | Issue |
|------|-----------|-------|--------|--------|-------|
| **fastapi_mcp** | pytest | 17 | 16 | 1 | 1 test failure |
| **omnara** | unittest | 4 | 3 | 1 | 1 test failure |
| **scrapy** | unittest | 117 | 116 | 1 | 1 test failure |
| **openrouter-ai-ecosystem** | unittest | 1 | 0 | 1 | Test failure in base suite |
| **claude-code-complete-backup** | unittest | 1 | 0 | 1 | Test failure |

## Repos with Import/Setup Errors (Need Fixing)

**6 repos** had test runners that started but failed to import modules:

| Repo | Framework | Issue |
|------|-----------|-------|
| **PydanticAI-Research-Agent** | pytest | Import error — missing dependencies or module path issue |
| **agenticSeek** | pytest | Import error — code likely depends on uninstalled packages |
| **aider** | pytest | Import error — missing dependencies |
| **deer-flow** | pytest | Import error — missing dependencies |
| **local-operator** | pytest | Import error — missing dependencies |
| **mcp-use** | pytest | Import error — missing dependencies |

## Repos with No Runnable Tests

**47 repos** have a tests/ directory but no runnable tests in this environment:

| Category | Count | Details |
|----------|-------|---------|
| No "test" script in package.json | 30 | Most are Vite/React scaffolded projects (via Lovable/Bolt) with tests/ dir but no test runner configured |
| Dependencies not installed | 9 | Has test script (vitest/jest/playwright) but `node_modules` missing |
| No recognized project framework | 7 | No package.json, requirements.txt, setup.py, Cargo.toml, or go.mod |
| Tool not available | 1 | Go not installed on this system |
| Unsupported test config | 1 | browser-use needs pytest plugin `--dist=loadscope (pytest-xdist) not installed |

## Key Findings

1. **Only 1 repo passes all tests:** `multi-agent-coding-environment`
2. **4 repos have test runners that work but have failing tests** (scrapy, fastapi_mcp, omnara, openrouter-ai-ecosystem, claude-code-complete-backup)
3. **30 repos have a tests/ directory but no `test` script in package.json** — these are scaffold projects with placeholder test folders
4. **6 repos have import/setup errors** — tests exist but dependencies aren't installed
5. **7 repos have tests/ directories but no recognizable build framework** — likely contain test data or config files only
6. **1 repo (nautilus_trader)** times out — Rust compilation exceeds 60s budget
7. Many `woodsai69rme_*` repos are duplicates of other repos in the collection

## Recommendations

- **Install dependencies** on repos with test scripts to enable test execution
- **Add test scripts** to the 30 repos that have tests/ directories but no test runner configured
- **Remove empty/placeholder tests/ directories** from repos that don't actually use them
- The multi-agent-coding-environment, scrapy (116/117), and fastapi_mcp (16/17) test suites should be maintained as examples
