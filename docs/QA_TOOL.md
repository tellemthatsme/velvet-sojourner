# AgentForge QA Tool

Single command to validate all 843 repos across 9 dimensions.

## Quick Start

```bash
python qa_all_repos.py --quick
```

## Commands

```bash
# Full scan (includes git status + file integrity — ~3 min)
python qa_all_repos.py

# Quick scan — skip slow checks
python qa_all_repos.py --quick

# JSON output for programmatic use
python qa_all_repos.py --json

# Scan a different repo directory
python qa_all_repos.py --path /path/to/repos
```

## What It Checks

| Check | What It Validates | Why |
|-------|------------------|-----|
| **Directory existence** | Every repo has files | Empty dirs = failed download |
| **README quality** | README.md exists with content | Usability — no stub READMEs |
| **License presence** | MIT/Apache/GPL/CC0 header | Legal safety |
| **Dockerfile validity** | Has `FROM` or `services` | Deployability |
| **Git status** | Dirty repos, behind remotes, tokens in URLs | Source integrity |
| **File integrity** | Zero-byte files (excludes git internals, `__init__.py`, `.nojekyll`) | Corrupt downloads |
| **Size anomalies** | >1 GB or 0-file repos | Failed clones |
| **Test suites** | `tests/` dirs with actual test files | Development readiness |
| **Category coverage** | All repos tagged in `docs/repo-categories.json` | Taxonomy completeness |

## Exit Codes

- `0` — all critical checks pass (may have minor issues)
- `1` — issues found

## Output

Results saved to `qa-results/qa-report.json` with full per-repo details.
