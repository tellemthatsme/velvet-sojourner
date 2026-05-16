# eliza

## Description
No description available

## Tech Stack
JS/TS, Node.js, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # bash ./scripts/dev.sh
```
```bash
npm run start  # pnpm --filter "@ai16z/agent" start --isRoot
```
```bash
npm run build  # turbo run build --filter=!eliza-docs
```
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
eliza/
  agent/
  characters/
  client/
  docs/
  packages/
  scripts/
  tests/
  CHANGELOG.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README.md
  README_CN.md
  README_DE.md
  README_ES.md
  README_FR.md
  README_HE.md
  README_IT.md
  README_JA.md
  README_KOR.md
  README_PTBR.md
  README_RU.md
  README_TH.md
  README_TR.md
  README_VI.md
  SECURITY.md
  codecov.yml
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yaml**: Multi-container orchestration
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/generate-changelog.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies
### npm (production)
- @0glabs/0g-ts-sdk: 0.2.1
- @coinbase/coinbase-sdk: 0.10.0
- @deepgram/sdk: ^3.9.0
- @vitest/eslint-plugin: 1.0.1
- amqplib: 0.10.5
- csv-parse: 5.6.0
- ollama-ai-provider: 0.16.1
- optional: 0.1.4
- pnpm: 9.14.4
- sharp: 0.33.5
- tslog: 4.9.3

### npm (dev)
- @commitlint/cli: 18.6.1
- @commitlint/config-conventional: 18.6.3
- @typescript-eslint/eslint-plugin: 8.16.0
- @typescript-eslint/parser: 8.16.0
- @vitest/eslint-plugin: 1.1.13
- concurrently: 9.1.0
- cross-env: 7.0.3
- eslint: 9.16.0
- eslint-config-prettier: 9.1.0
- husky: 9.1.7
- lerna: 8.1.5
- only-allow: 1.2.1
- prettier: 3.4.1
- turbo: 2.3.3
- typedoc: 0.26.11
- ... and 3 more

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 113/120
- **Size**: 27.9 MB
- **Files**: 1574
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
