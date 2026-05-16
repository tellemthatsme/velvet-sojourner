# hermes-agent

## Description
No description available

## Tech Stack
Python, Node.js, Docker, GitHub Actions

## Quick Start
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
hermes-agent/
  acp_adapter/
  acp_registry/
  agent/
  assets/
  cron/
  datagen-config-examples/
  docker/
  docs/
  environments/
  gateway/
  hermes_cli/
  honcho_integration/
  landingpage/
  nix/
  optional-skills/
  packaging/
  plans/
  scripts/
  skills/
  tests/
  AGENTS.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  MANIFEST.in
  README.md
  RELEASE_v0.2.0.md
  RELEASE_v0.3.0.md
  RELEASE_v0.4.0.md
  RELEASE_v0.5.0.md
  RELEASE_v0.6.0.md
  batch_runner.py
  cli-config.yaml.example
  cli.py
  flake.lock
  flake.nix
  hermes
  hermes_constants.py
  hermes_state.py
  hermes_time.py
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container build instructions
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **.github/workflows/deploy-site.yml**: CI/CD workflow
- **.github/workflows/docker-publish.yml**: CI/CD workflow
- **.github/workflows/docs-site-checks.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Python ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included
- Agent focused

## Dependencies
### npm (production)
- @askjo/camoufox-browser: ^1.0.0
- agent-browser: ^0.13.0

### Python (pip)
- openai
- python-dotenv
- fire
- httpx
- rich
- tenacity
- prompt_toolkit
- pyyaml
- requests
- jinja2
- pydantic>=2.0
- PyJWT[crypto]
- firecrawl-py
- parallel-web>=0.4.2
- fal-client
- edge-tts
- croniter
- python-telegram-bot>=20.0
- discord.py>=2.0
- aiohttp>=3.9.0

## Ports
- 993
- 587
- 8443
- 22

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 23.8 MB
- **Files**: 1254
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ❌
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ✅
  - requirements.txt: ✅
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
