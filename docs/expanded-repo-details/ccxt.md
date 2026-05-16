# ccxt

## Description
[![NPM Downloads]( [![npm]( [![PyPI]( [![NuGet version](

## Tech Stack
Python, Node.js, Docker, GitHub Actions

## Quick Start
```bash
npm run build  # npm run pre-transpile && npm run transpile && npm run post-transpile && npm run update-badges && npm run build-docs
```
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
ccxt/
  build/
  cs/
  dist/
  doc/
  examples/
  go/
  js/
  php/
  python/
  ts/
  utils/
  wiki/
  CHANGELOG.md
  CODEOWNERS
  CONTRIBUTING.md
  Dockerfile
  ISSUE_TEMPLATE.md
  LICENSE.txt
  README.md
  build-go.sh
  build.sh
  ccxt.php
  ci-requirements.txt
  cleanup.sh
  coin-ws.js
  composer-install.sh
  composer.json
  composer.lock
  docker-compose.yml
  examples2md.js
  exchanges.cfg
  gource.sh
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **index.html**: Application entry point
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/cs.yml**: CI/CD workflow
- **.github/workflows/go-app.yml**: CI/CD workflow
- **.github/workflows/js.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included

## Dependencies
### npm (production)
- ws: ^8.8.1

### npm (dev)
- @rollup/plugin-commonjs: ^21.0.3
- @rollup/plugin-json: ^4.1.0
- @rollup/plugin-node-resolve: ^15.2.3
- @types/node: ^18.15.11
- @typescript-eslint/eslint-plugin: ^5.30.5
- @typescript-eslint/parser: ^5.30.5
- ansicolor: ^2.0.0
- as-table: ^1.0.55
- asciichart: ^1.5.25
- assert: ^2.0.0
- ast-transpiler: ^0.0.66
- docsify: ^4.11.4
- eslint: 8.22.0
- eslint-config-airbnb-base: 15.0.0
- eslint-plugin-import: 2.25.4
- ... and 15 more

## Ports
- Not detected

## Score Breakdown
- **Overall Score**: 113/120
- **Size**: 229.2 MB
- **Files**: 7127
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ✅
  - requirements.txt: ❌
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
