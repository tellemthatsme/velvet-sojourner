# Qwen

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
Qwen/
  ascend-support/
  assets/
  dcu-support/
  docker/
  eval/
  examples/
  finetune/
  recipes/
  Dockerfile
  FAQ.md
  FAQ_ja.md
  FAQ_zh.md
  LICENSE
  NOTICE
  QWEN_TECHNICAL_REPORT.pdf
  README.md
  README_CN.md
  README_ES.md
  README_FR.md
  README_JA.md
  Tongyi Qianwen LICENSE AGREEMENT
  Tongyi Qianwen RESEARCH LICENSE AGREEMENT
  cli_demo.py
  finetune.py
  openai_api.py
  requirements.txt
  requirements_web_demo.txt
  run_gptq.py
```

## Key Files
- **README.md**: Project overview and setup instructions
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **.github/workflows/stale.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Python ecosystem
- Environment configuration
- Documentation included
- Open source licensed

## Dependencies

### Python (pip)
- transformers>=4.32.0,<4.38.0
- accelerate
- tiktoken
- einops
- transformers_stream_generator==0.0.4
- scipy

## Ports
- 8000

## Score Breakdown
- **Overall Score**: 103/120
- **Size**: 18.5 MB
- **Files**: 146
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ❌
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ❌
  - requirements.txt: ✅
  - pyproject.toml: ❌
  - Cargo.toml: ❌
  - go.mod: ❌
