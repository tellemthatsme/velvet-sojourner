# crawlee

## Description
No description available

## Tech Stack
JS/TS, Docker, GitHub Actions

## Quick Start
```bash
npm run build  # turbo run build && node ./scripts/typescript_fixes.mjs
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
crawlee/
  docs/
  packages/
  scripts/
  test/
  website/
  CHANGELOG.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE.md
  MIGRATIONS.md
  README.md
  RELEASE.md
  biome.json
  eslint.config.mjs
  lerna.json
  package.json
  renovate.json
  tsconfig.build.json
  tsconfig.eslint.json
  tsconfig.json
  turbo.json
  vitest.config.ts
  yarn.lock
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/check-pr-title.yml**: CI/CD workflow
- **.github/workflows/docs.yml**: CI/CD workflow
- **.github/workflows/release.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Environment configuration
- Documentation included
- Test suite included

## Dependencies

### npm (dev)
- @apify/eslint-config: ^1.0.0
- @apify/log: ^2.4.0
- @apify/tsconfig: ^0.1.0
- @biomejs/biome: ^1.7.3
- @commitlint/config-conventional: ^19.0.0
- @playwright/browser-chromium: 1.53.2
- @playwright/browser-firefox: 1.53.2
- @playwright/browser-webkit: 1.53.2
- @stylistic/eslint-plugin-ts: ^4.2.0
- @types/content-type: ^1.1.5
- @types/deep-equal: ^1.0.1
- @types/domhandler: ^2.4.2
- @types/express: ^4.17.13
- @types/fs-extra: ^11.0.0
- @types/inquirer: ^8.2.1
- ... and 45 more

## Ports
- 8000
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 100.0 MB
- **Files**: 2126
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
