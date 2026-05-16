# deer-flow

## Description
[![Python 3.12+](

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
deer-flow/
  assets/
  docs/
  examples/
  src/
  tests/
  web/
  CONTRIBUTING
  Dockerfile
  LICENSE
  Makefile
  README.md
  README_de.md
  README_es.md
  README_ja.md
  README_pt.md
  README_ru.md
  README_zh.md
  bootstrap.bat
  bootstrap.sh
  conf.yaml.example
  docker-compose.yml
  langgraph.json
  main.py
  pre-commit
  pyproject.toml
  server.py
```

## Key Files
- **README.md**: Project overview and setup instructions
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **Makefile**: Build automation targets
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **main.py**: Main Python entry point
- **server.py**: Server entry point

## Features
- Unit/integration tests
- Containerized deployment
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
- 8000
- 3000

## Score Breakdown
- **Overall Score**: 116/120
- **Size**: 5.3 MB
- **Files**: 275
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ✅
  - package.json: ❌
  - requirements.txt: ❌
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
