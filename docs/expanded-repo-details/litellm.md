# litellm

## Description
No description available

## Tech Stack
Python, Node.js, React, Docker, GitHub Actions

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
litellm/
  ci_cd/
  cookbook/
  db_scripts/
  deploy/
  dist/
  docker/
  docs/
  enterprise/
  litellm-js/
  litellm-proxy-extras/
  litellm/
  tests/
  ui/
  AGENTS.md
  CLAUDE.md
  CONTRIBUTING.md
  Dockerfile
  GEMINI.md
  LICENSE
  Makefile
  README.md
  codecov.yaml
  docker-compose.yml
  index.yaml
  mcp_servers.json
  model_prices_and_context_window.json
  package-lock.json
  package.json
  poetry.lock
  prometheus.yml
  proxy_server_config.yaml
  pyproject.toml
  pyrightconfig.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **Makefile**: Build automation targets
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **.github/workflows/auto_update_price_and_context_window.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Build automation
- Node.js/TypeScript ecosystem
- Python ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included
- Llm focused

## Dependencies
### npm (production)
- prism-react-renderer: ^2.4.1
- prisma: ^5.17.0
- react-copy-to-clipboard: ^5.1.0

### npm (dev)
- @types/react-copy-to-clipboard: ^5.0.7

### Python (pip)
- anyio==4.8.0 # openai + http req.
- httpx==0.28.1
- openai==1.99.5  # openai req.
- fastapi==0.115.5 # server dep
- backoff==2.2.1 # server dep
- pyyaml==6.0.2 # server dep
- uvicorn==0.29.0 # server dep
- gunicorn==23.0.0 # server dep
- uvloop==0.21.0 # uvicorn dep, gives us much better performance under load
- boto3==1.34.34 # aws bedrock/sagemaker calls
- redis==5.2.1 # redis caching
- prisma==0.11.0 # for db
- mangum==0.17.0 # for aws lambda functions
- pynacl==1.5.0 # for encrypting keys
- google-cloud-aiplatform==1.47.0 # for vertex ai calls
- google-cloud-iam==2.19.1 # for GCP IAM Redis authentication
- google-genai==1.22.0
- anthropic[vertex]==0.54.0
- mcp==1.10.1    # for MCP server
- google-generativeai==0.5.0 # for vertex ai calls
- ... and 37 more

## Ports
- 5432
- 4000
- 9090

## Score Breakdown
- **Overall Score**: 116/120
- **Size**: 242.3 MB
- **Files**: 3740
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ✅
  - package.json: ✅
  - requirements.txt: ✅
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
