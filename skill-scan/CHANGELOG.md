# Changelog

## [0.1.0] - 2026-05-29

### Added
- 8 security rule categories (shell injection, secrets, code execution, obfuscation,
  prompt injection, network, file access, exfiltration)
- CLI with scan, rules, info, update commands
- 4 output formats (terminal, JSON, SARIF, HTML)
- Pre-commit hook support
- GitHub Actions CI workflow with weekly scheduled scans
- Rule update system with versioned rules and remote manifest
- YAML allowlist for false positive suppression with expiry support
- Custom rule loading via `--rules` and `--no-default-rules`
- Path exclusion with glob patterns
- Severity filtering (CRITICAL through INFO)
- CI mode (exit code 1 on any finding)
- 37 passing tests with benign and malicious fixtures
- Benchmark test for scan speed validation
- PyInstaller spec for standalone binary distribution
