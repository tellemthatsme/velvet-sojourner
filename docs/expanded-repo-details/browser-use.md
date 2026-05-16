# browser-use

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
browser-use/
  bin/
  browser_use/
  docker/
  docs/
  examples/
  static/
  tests/
  CLAUDE.md
  Dockerfile
  Dockerfile.fast
  LICENSE
  README.md
  pyproject.toml
```

## Key Files
- **README.md**: Project overview and setup instructions
- **Dockerfile**: Container build instructions
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **.github/workflows/claude.yml**: CI/CD workflow
- **.github/workflows/cloud_evals.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies
No dependency files detected

## Ports
- 9242
- 9222

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 4.1 MB
- **Files**: 370
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
