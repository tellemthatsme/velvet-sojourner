# pipedream

## Description
No description available

## Tech Stack
JS/TS, Node.js, Vue, Docker, GitHub Actions

## Quick Start
```bash
npm run build  # npx tsc --build | node scripts/tsPostBuild.mjs
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
pipedream/
  blog/
  components/
  docs-v2/
  helpers/
  images/
  modelcontextprotocol/
  packages/
  platform/
  scripts/
  sources/
  types/
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README.md
  SECURITY.md
  _config.yml
  eslint.config.mjs
  glama.json
  jest.config.js
  package-lock.json
  package.json
  pnpm-lock.yaml
  pnpm-workspace.yaml
  tsconfig.json
  vercel.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed

## Dependencies
### npm (production)
- @actions/core: ^1.10.0
- @pipedream/platform: ^1.5.1
- @sentry/node: ^7.7.0
- @types/node: ^20.17.6
- crypto: ^1.0.1
- linkup-sdk: ^1.0.3
- uuid: ^8.3.2
- vue: ^2.6.14

### npm (dev)
- @eslint/eslintrc: ^3.2.0
- @eslint/js: ^9.15.0
- @next/eslint-plugin-next: ^14.2.5
- @pipedream/eslint-plugin-pipedream: 0.2.5
- @pipedream/types: 0.1.4
- @tsconfig/node14: ^1.0.1
- @types/jest: ^27.4.1
- @typescript-eslint/eslint-plugin: ^8
- @typescript-eslint/parser: ^8
- eslint: ^8
- eslint-config-next: ^15
- eslint-plugin-import: ^2.31.0
- eslint-plugin-jest: ^28
- eslint-plugin-jsonc: ^1.6.0
- eslint-plugin-putout: ^23
- ... and 14 more

## Ports
- 8000
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 336.4 MB
- **Files**: 22120
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
