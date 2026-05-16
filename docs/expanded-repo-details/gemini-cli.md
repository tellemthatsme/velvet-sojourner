# gemini-cli

## Description
[![Gemini CLI CI](

## Tech Stack
JS/TS, Docker, GitHub Actions

## Quick Start
```bash
npm run start  # node scripts/start.js
```
```bash
npm run build  # node scripts/build.js
```
```bash
make  # or make run/dev
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
gemini-cli/
  docs/
  eslint-rules/
  integration-tests/
  packages/
  scripts/
  CONTRIBUTING.md
  Dockerfile
  GEMINI.md
  LICENSE
  Makefile
  README.md
  esbuild.config.js
  eslint.config.js
  package-lock.json
  package.json
  tsconfig.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **Makefile**: Build automation targets
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/community-report.yml**: CI/CD workflow
- **.github/workflows/e2e.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Build automation
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included
- Cli focused

## Dependencies

### npm (dev)
- @types/micromatch: ^4.0.9
- @types/mime-types: ^3.0.1
- @types/minimatch: ^5.1.2
- @types/shell-quote: ^1.7.5
- @vitest/coverage-v8: ^3.1.1
- concurrently: ^9.2.0
- cross-env: ^7.0.3
- esbuild: ^0.25.0
- eslint: ^9.24.0
- eslint-config-prettier: ^10.1.2
- eslint-plugin-import: ^2.31.0
- eslint-plugin-license-header: ^0.8.0
- eslint-plugin-react: ^7.37.5
- eslint-plugin-react-hooks: ^5.2.0
- glob: ^10.4.5
- ... and 9 more

## Ports
- Not detected

## Score Breakdown
- **Overall Score**: 111/120
- **Size**: 5.2 MB
- **Files**: 448
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ❌
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ✅
  - package.json: ✅
  - requirements.txt: ❌
  - pyproject.toml: ❌
  - Cargo.toml: ❌
  - go.mod: ❌
