# local-operator

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
local-operator/
  docs/
  examples/
  local_operator/
  scripts/
  static/
  tests/
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  Makefile
  README.md
  SECURITY.md
  docker-compose.yml
  flake.lock
  flake.nix
  pyproject.toml
  requirements.txt
  setup.py
```

## Key Files
- **README.md**: Project overview and setup instructions
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **Makefile**: Build automation targets
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/publish.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Build automation
- Python ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies

### Python (pip)
- langchain-openai==0.3.11
- pydantic==2.10.6
- python-dotenv==1.0.1
- langchain-ollama==0.3.0
- langchain==0.3.21
- langchain-community==0.3.14
- langchain-anthropic==0.3.3
- langchain-google-genai==2.1.2
- tiktoken==0.8.0
- uvicorn==0.22.0
- fastapi==0.115.8
- playwright==1.49.1
- requests==2.32.3
- psutil==7.0.0
- dill==0.3.9
- pyreadline3==3.5.4
- jsonlines==4.0.0
- python-multipart==0.0.20
- websockets==15.0.1
- browser-use==0.1.45
- ... and 16 more

## Ports
- 1111
- 8000

## Score Breakdown
- **Overall Score**: 111/120
- **Size**: 80.3 MB
- **Files**: 135
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ✅
  - package.json: ❌
  - requirements.txt: ✅
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
