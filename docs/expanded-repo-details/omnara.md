# omnara

## Description
No description available

## Tech Stack
Python, Docker, GitHub Actions

## Quick Start
```bash
make  # or make run/dev
```
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
omnara/
  backend/
  cli/
  docker/
  docs/
  integrations/
  omnara/
  scripts/
  servers/
  shared/
  tests/
  CLAUDE.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  Makefile
  README.md
  dev-start.sh
  dev-stop.sh
  docker-compose.yml
  pyproject.toml
  pyrightconfig.json
  requirements-dev.txt
```

## Key Files
- **README.md**: Project overview and setup instructions
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **Makefile**: Build automation targets
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/release.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Multi-service orchestration
- CI/CD pipeline
- Build automation
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies
No dependency files detected

## Ports
- 5432
- 8080
- 8000

## Score Breakdown
- **Overall Score**: 101/120
- **Size**: 46.6 MB
- **Files**: 181
  - README: ✅
  - License: ✅
  - Dockerfile: ❌
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ✅
  - package.json: ❌
  - requirements.txt: ❌
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
