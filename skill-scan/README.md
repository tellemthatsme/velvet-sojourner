# skill-scan

> Security scanner for AI agent skills (SKILL.md) — detect dangerous patterns before they cause harm.

![Python](https://img.shields.io/badge/python-%3E%3D3.9-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-37%20passing-brightgreen)
![Status](https://img.shields.io/badge/status-beta-yellow)
![Self-scan](https://img.shields.io/badge/self--scan-0%20findings-brightgreen)

## Quick Reference

```bash
skill-scan scan ./skills/         # Scan a skill directory
skill-scan scan . --ci            # CI mode — exit 1 on any finding
skill-scan scan . --output sarif  # SARIF for GitHub Advanced Security
skill-scan rules                  # List all available rules
skill-scan info SKILL.md          # Show skill metadata
skill-scan update                 # Download latest rules
skill-scan update --check         # Check for updates (no download)
skill-scan scan . --allowlist allowlist.yaml  # Suppress false positives
```

## Installation

```bash
pip install .
```

Or with dev extras:

```bash
pip install -e ".[dev]"
```

## Rule Reference

| Rule ID | Severity | Description | Example |
|---|---|---|---|
| `shell-injection` | HIGH | Shell command injection patterns | `$(...)`, `` `...` ``, `os.system`, `subprocess.*`, `sh -c`, `bash -c` |
| `secrets` | CRITICAL | Hardcoded API keys and tokens | GitHub tokens (`ghp_*`), OpenAI keys (`sk-...`), AWS keys (`AKIA...`) |
| `code-exec` | CRITICAL | Arbitrary code execution | `eval(`, `exec(`, `compile(`, `__import__`, `importlib.import_module` |
| `obfuscation` | MEDIUM | Encoded/obfuscated code | `base64.b64decode`, `bytes.fromhex`, hex strings >20 chars, compression |
| `prompt-injection` | HIGH | System prompt override patterns | "Ignore previous instructions", `<system>` tags, role-play override |
| `network` | MEDIUM | Unexpected outbound connections | `curl`, `requests.get`, `socket.connect`, suspicious TLDs (`.gq`, `.ml`, `.xyz`) |
| `file-access` | MEDIUM | File ops outside skill scope | `/etc/`, `C:\Windows`, `.ssh/` writes, `shutil.rmtree`, temp files |
| `exfiltration` | CRITICAL | Data theft pipelines | Read+HTTP, encode+send, SMTP, DNS exfil, socket+read in same function |

### Severity Levels

- **CRITICAL** — Immediate security threat (secrets, code exec, exfiltration)
- **HIGH** — Significant risk (shell injection, prompt injection)
- **MEDIUM** — Moderate concern (obfuscation, network, file access)
- **LOW** — Minor issue (temp files without cleanup)
- **INFO** — Informational only

## Allowlist Configuration

Suppress false positives by creating a `.skill-scan-allowlist.yaml` file:

```yaml
allowlist:
  - rule_id: secrets-detection
    file_pattern: tests/fixtures/*
    reason: "Test credentials, not real secrets"
    expires: "2027-01-01"
  - rule_id: shell-injection
    file_pattern: scripts/deploy.sh
    reason: "Intended shell execution"
  - rule_id: "*"
    file_pattern: vendor/*
    reason: "Third-party code — not authored by us"
```

| Field | Description |
|---|---|
| `rule_id` | Rule identifier to suppress (use `"*"` for all rules) |
| `file_pattern` | Glob pattern matching files to allowlist |
| `reason` | Human-readable justification for the suppression |
| `expires` | Optional ISO date — entry auto-expires after this date |

Use a custom allowlist path:

```bash
skill-scan scan . --allowlist /path/to/allowlist.yaml
```

## Rule Update System

Keep your rules current with the built-in updater:

```bash
skill-scan update           # Download and install new rules
skill-scan update --check   # Check what's available without downloading
```

The updater fetches a remote manifest, compares version numbers, and downloads only newer rules.

## Self-Scan

skill-scan scans itself in CI. Current status:

```
Self-scan: 0 critical, 0 high findings
```

Test fixture secrets are allowlisted via `.skill-scan-allowlist.yaml`.

## Commands

### `scan`

```bash
skill-scan scan [OPTIONS] PATH

Options:
  -o, --output TEXT       Output format: terminal, json, sarif, html  [default: terminal]
  -s, --severity TEXT     Minimum severity: critical, high, medium, low, info
  -v, --verbose           Show snippet details in terminal output
  --ci                    Exit with code 1 if any finding is discovered
  --exclude TEXT          Glob pattern of paths to exclude (can be used multiple times)
  --no-default-rules      Disable built-in rules
  --rules PATH            Load custom rules from a directory
  --allowlist PATH        Path to allowlist YAML file
  --help                  Show this message and exit
```

### `rules`

```bash
skill-scan rules
```

Lists all available rules with their severity and description.

### `info`

```bash
skill-scan info PATH
```

Show metadata from a skill's SKILL.md file.

### `update`

```bash
skill-scan update [--check]
```

Check for or install rule updates from the remote source.

## CI Integration

### GitHub Actions

Full workflow example including rule update check:

```yaml
name: Skill Security Scan

on:
  push:
    branches: [main, master]
    paths:
      - "*.md"
      - "**/*.md"
  pull_request:
    branches: [main, master]
    paths:
      - "*.md"
      - "**/*.md"

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install skill-scan
        run: pip install .

      - name: Check for rule updates
        run: skill-scan update --check || true

      - name: Run skill-scan
        run: |
          mkdir -p scan-results
          skill-scan scan . --output sarif --ci > scan-results/results.sarif 2>&1 || true

      - name: Upload SARIF artifact
        uses: actions/upload-artifact@v4
        with:
          name: skill-scan-results
          path: scan-results/results.sarif
```

The included `.github/workflows/scan.yml` provides this out of the box.

### Pre-commit Hook

skill-scan ships with a `.pre-commit-hooks.yaml` at the project root. To use it:

1. Add to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/velvet-sojourner/skill-scan
  rev: v0.1.0
  hooks:
    - id: skill-scan
```

Or use it as a local hook:

```yaml
- repo: local
  hooks:
    - id: skill-scan
      name: skill-scan
      description: Scan AI agent skills for security issues
      entry: skill-scan scan --ci
      language: python
      files: \.md$
```

## Custom Rules

Write your own rule by subclassing `Rule`:

```python
from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule
import re

class MyCustomRule(Rule):
    name = "my-custom-rule"
    description = "Detects dangerous patterns specific to my project"
    severity = Severity.HIGH

    def match(self, file_path, content):
        findings = []
        for match in re.finditer(r"dangerous_pattern", content):
            findings.append(Finding(...))
        return findings
```

Load custom rules at scan time:

```bash
skill-scan scan ./skills/ --rules ./my-custom-rules/
```

Combine with `--no-default-rules` to run only your rules:

```bash
skill-scan scan ./skills/ --no-default-rules --rules ./my-custom-rules/
```

## Output Formats

- **terminal**: Colored terminal output with severity icons
- **json**: Structured JSON with all findings and metadata
- **sarif**: SARIF 2.1.0 format for integration with GitHub Advanced Security
- **html**: Self-contained HTML report with severity badges and code snippets

### Sample Output

```
skill-scan report
  Path:        ./test-skill
  Files:       12
  Rules:       8
  Findings:    3
  Duration:    0.24s

  Severity            Rule ID                      File                                            Line   Message
  --------            ---------------------------  ----------------------------------------------  -----  -------
  [CRIT] CRITICAL     secrets/openai-key           test-skill/script.py                             7     OpenAI API key detected
  [HIGH] HIGH         shell-injection/sh-c         test-skill/script.py                             15    sh -c shell execution detected
  [MED]  MEDIUM       obfuscation/b64-string       test-skill/utils.py                              22    Base64-encoded string detected

Found 3 issue(s) across 12 file(s).
```

## Usage Examples

### Exclude paths

```bash
skill-scan scan ./skills/ --exclude "**/test*" --exclude "**/vendor/*"
```

### Run only custom rules

```bash
skill-scan scan ./skills/ --no-default-rules --rules ./my-rules/
```

### Scan with minimal severity threshold

```bash
skill-scan scan ./skills/ --severity high
```

### SARIF output for GitHub Advanced Security

```bash
skill-scan scan ./skills/ --output sarif > results.sarif
```

### Verbose mode

```bash
skill-scan scan ./skills/ --verbose
```

## FAQ

### How is this different from Snyk?

Snyk scans your application dependencies for known vulnerabilities (CVEs). skill-scan scans AI agent skill files (SKILL.md and associated scripts) for dangerous patterns like shell injection, hardcoded secrets, prompt injection, and data exfiltration. They solve different problems — Snyk is about supply chain security, skill-scan is about AI agent behavior security.

### Can I add custom rules?

Yes. Write a Python class that subclasses `Rule`, implementing the `match()` method. Load custom rules with `--rules ./my-rules/`. See the Custom Rules section for a full example.

### Does it work with CI?

Yes. Use `--ci` flag to exit with code 1 on any finding. skill-scan ships with a GitHub Actions workflow, a pre-commit hook, and supports SARIF output for GitHub Advanced Security integration.

### What happens if my skill has no issues?

The scanner prints a clean summary: `No issues found across N file(s).` and exits with code 0 (unless you used `--ci`, in which case it also exits 0).

### Can I exclude test files from scanning?

Use `--exclude "**/test*"` to skip test files. Combine with `--allowlist` to suppress specific findings instead of excluding entire files.

### Does skill-scan send data to any external service?

No. skill-scan runs entirely locally. The `update` command fetches rule definitions from a remote URL, which is optional and disabled by default.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run tool directly
python -m skill_scan scan ./tests/fixtures/malicious/

# Scan yourself (eat your own dog food)
skill-scan scan . --output html > report.html
```

## License

MIT
