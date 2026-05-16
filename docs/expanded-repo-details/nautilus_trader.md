# nautilus_trader

## Description
[![codecov](

## Tech Stack
Python, Rust, Docker, GitHub Actions

## Quick Start
```bash
make  # or make run/dev
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
nautilus_trader/
  assets/
  crates/
  docs/
  examples/
  nautilus_trader/
  python/
  schema/
  scripts/
  tests/
  CLA.md
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  Cargo.lock
  Cargo.toml
  Dockerfile
  LICENSE
  Makefile
  README.md
  RELEASES.md
  ROADMAP.md
  SECURITY.md
  build.py
  clippy.toml
  pyproject.toml
  rust-toolchain.toml
  rustfmt.toml
  uv-version
  uv.lock
  version.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **Dockerfile**: Container build instructions
- **Makefile**: Build automation targets
- **pyproject.toml**: Python project configuration
- **Cargo.toml**: Rust project configuration
- **.env.example**: Environment variable template
- **.github/workflows/build-docs.yml**: CI/CD workflow
- **.github/workflows/build-v2.yml**: CI/CD workflow
- **.github/workflows/build.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Build automation
- Rust native performance
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies
No dependency files detected

## Ports
- 8000

## Score Breakdown
- **Overall Score**: 116/120
- **Size**: 103.1 MB
- **Files**: 3056
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ❌
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ✅
  - package.json: ❌
  - requirements.txt: ❌
  - pyproject.toml: ✅
  - Cargo.toml: ✅
  - go.mod: ❌
