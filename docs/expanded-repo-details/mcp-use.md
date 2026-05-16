# mcp-use

## Description
No description available

## Tech Stack
Python, Docker, GitHub Actions

## Quick Start
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
mcp-use/
  docs/
  examples/
  mcp_use/
  static/
  tests/
  CHANGELOG.md
  CLAUDE.md
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README.md
  pyproject.toml
  pytest.ini
  ruff.toml
```

## Key Files
- **README.md**: Project overview and setup instructions
- **Dockerfile**: Container build instructions
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **.github/workflows/changelog.yml**: CI/CD workflow
- **.github/workflows/publish.yml**: CI/CD workflow
- **.github/workflows/release-drafter.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included
- Mcp focused

## Dependencies
No dependency files detected

## Ports
- 8000

## Score Breakdown
- **Overall Score**: 103/120
- **Size**: 6.4 MB
- **Files**: 160
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ❌
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ❌
  - requirements.txt: ❌
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
