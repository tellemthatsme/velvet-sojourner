# linkwarden

## Description
No description available

## Tech Stack
JS/TS, Node.js, Docker, GitHub Actions

## Quick Start
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
linkwarden/
  apps/
  assets/
  packages/
  Dockerfile
  LICENSE.md
  README.md
  crowdin.yml
  docker-compose.yml
  package.json
  yarn.lock
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **.github/workflows/check-branch.yml**: CI/CD workflow
- **.github/workflows/locale-action.yml**: CI/CD workflow
- **.github/workflows/playwright-tests.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Documentation included

## Dependencies
### npm (production)
- concurrently: ^9.1.2

### npm (dev)
- dotenv-cli: ^8.0.0

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 113/120
- **Size**: 10.4 MB
- **Files**: 605
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ✅
  - requirements.txt: ❌
  - pyproject.toml: ❌
  - Cargo.toml: ❌
  - go.mod: ❌
