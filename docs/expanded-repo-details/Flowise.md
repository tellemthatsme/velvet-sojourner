# Flowise

## Description
No description available

## Tech Stack
JS/TS, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # turbo run dev --parallel --no-cache
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
Flowise/
  assets/
  docker/
  i18n/
  images/
  metrics/
  packages/
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE.md
  README.md
  SECURITY.md
  artillery-load-test.yml
  package.json
  pnpm-lock.yaml
  pnpm-workspace.yaml
  turbo.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **.github/workflows/docker-image.yml**: CI/CD workflow
- **.github/workflows/main.yml**: CI/CD workflow
- **.github/workflows/test_docker_build.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Environment configuration
- Documentation included
- Test suite included

## Dependencies

### npm (dev)
- @babel/preset-env: ^7.19.4
- @babel/preset-typescript: 7.18.6
- @types/express: ^4.17.13
- @typescript-eslint/typescript-estree: ^7.13.1
- eslint: ^8.24.0
- eslint-config-prettier: ^8.3.0
- eslint-config-react-app: ^7.0.1
- eslint-plugin-jsx-a11y: ^6.6.1
- eslint-plugin-markdown: ^3.0.0
- eslint-plugin-prettier: ^3.4.0
- eslint-plugin-react: ^7.26.1
- eslint-plugin-react-hooks: ^4.6.0
- eslint-plugin-unused-imports: ^2.0.0
- husky: ^8.0.1
- kill-port: ^2.0.1
- ... and 7 more

## Ports
- 8000
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 37.8 MB
- **Files**: 1880
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
