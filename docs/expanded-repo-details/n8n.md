# n8n

## Description
n8n is a workflow automation platform that gives technical teams the flexibility of code with the speed of no-code. With 400+ integrations, native AI capabilities, and a fair-code license, n8n lets yo

## Tech Stack
JS/TS, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # turbo run dev --parallel --env-mode=loose --filter=!@n8n/design-system --filter=!@n8n/chat --filter=!@n8n/task-runner
```
```bash
npm run start  # run-script-os
```
```bash
npm run build  # turbo run build
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
n8n/
  assets/
  cypress/
  docker/
  packages/
  patches/
  scripts/
  test-workflows/
  CHANGELOG.md
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  CONTRIBUTOR_LICENSE_AGREEMENT.md
  Dockerfile
  LICENSE.md
  LICENSE_EE.md
  README.md
  SECURITY.md
  biome.jsonc
  codecov.yml
  jest.config.js
  lefthook.yml
  package.json
  pnpm-lock.yaml
  pnpm-workspace.yaml
  tsconfig.json
  turbo.json
  vitest.workspace.ts
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/benchmark-destroy-nightly.yml**: CI/CD workflow
- **.github/workflows/benchmark-nightly.yml**: CI/CD workflow
- **.github/workflows/check-documentation-urls.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Environment configuration
- Documentation included
- Test suite included
- Automation focused
- Platform focused

## Dependencies

### npm (dev)
- @biomejs/biome: ^1.9.0
- @n8n/eslint-config: workspace:*
- @types/jest: ^29.5.3
- @types/node: *
- @types/supertest: ^6.0.3
- cross-env: ^7.0.3
- jest: ^29.6.2
- jest-environment-jsdom: ^29.6.2
- jest-expect-message: ^1.1.3
- jest-junit: ^16.0.0
- jest-mock: ^29.6.2
- jest-mock-extended: ^3.0.4
- lefthook: ^1.7.15
- nock: ^14.0.1
- nodemon: ^3.0.1
- ... and 11 more

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 62.1 MB
- **Files**: 10756
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
