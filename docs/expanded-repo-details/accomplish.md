# accomplish

## Description
No description available

## Tech Stack
JS/TS, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # node scripts/dev.cjs
```
```bash
npm run build  # pnpm -r --workspace-concurrency=1 build
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
accomplish/
  apps/
  docs/
  packages/
  scripts/
  AGENTS.md
  CLAUDE.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README.ar.md
  README.es.md
  README.id.md
  README.ja.md
  README.ko.md
  README.md
  README.ru.md
  README.tr.md
  README.zh-CN.md
  SECURITY.md
  TRADEMARKS.md
  eslint.config.js
  package.json
  pnpm-lock.yaml
  pnpm-workspace.yaml
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/commitlint.yml**: CI/CD workflow
- **.github/workflows/refresh-agent-core-split.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Environment configuration
- Documentation included
- Open source licensed

## Dependencies

### npm (dev)
- @eslint/js: ^9.39.2
- eslint: ^9.39.2
- eslint-config-prettier: ^10.1.8
- eslint-plugin-react: ^7.37.5
- eslint-plugin-react-hooks: ^7.0.1
- globals: ^17.3.0
- husky: ^9.1.7
- lint-staged: ^16.2.7
- prettier: ^3.8.1
- typescript-eslint: ^8.55.0
- wait-on: ^9.0.4

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 14.3 MB
- **Files**: 648
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ❌
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ✅
  - requirements.txt: ❌
  - pyproject.toml: ❌
  - Cargo.toml: ❌
  - go.mod: ❌
