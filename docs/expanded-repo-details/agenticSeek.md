# agenticSeek

## Description
No description available

## Tech Stack
Python, Docker, GitHub Actions

## Quick Start
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
agenticSeek/
  crx/
  docs/
  frontend/
  llm_router/
  llm_server/
  media/
  prompts/
  scripts/
  searxng/
  sources/
  tests/
  Dockerfile
  Dockerfile.backend
  LICENSE
  README.md
  README_CHS.md
  README_CHT.md
  README_FR.md
  README_JP.md
  api.py
  cli.py
  config.ini
  docker-compose.yml
  install.bat
  install.sh
  requirements.txt
  setup.py
  start_services.cmd
  start_services.sh
```

## Key Files
- **README.md**: Project overview and setup instructions
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **.env.example**: Environment variable template

## Features
- Unit/integration tests
- Multi-service orchestration
- CI/CD pipeline
- Python ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included
- Agent focused

## Dependencies

### Python (pip)
- kokoro==0.9.4
- certifi==2025.4.26
- fastapi>=0.115.12
- flask>=3.1.0
- celery>=5.5.1
- aiofiles>=24.1.0
- uvicorn>=0.34.0
- pydantic>=2.10.6
- pydantic_core>=2.27.2
- setuptools>=75.6.0
- sacremoses>=0.0.53
- requests>=2.31.0
- numpy>=1.24.4
- colorama>=0.4.6
- python-dotenv>=1.0.0
- playsound>=1.3.0
- soundfile>=0.13.1
- transformers>=4.46.3
- torch>=2.4.1
- python-dotenv>=1.0.0
- ... and 28 more

## Ports
- 8080
- 8000
- 3000

## Score Breakdown
- **Overall Score**: 98/120
- **Size**: 9.2 MB
- **Files**: 127
  - README: ✅
  - License: ✅
  - Dockerfile: ❌
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ❌
  - requirements.txt: ✅
  - pyproject.toml: ❌
  - Cargo.toml: ❌
  - go.mod: ❌
