# playwright-mcp

## Description
A Model Context Protocol (MCP) server that provides browser automation capabilities using [Playwright]( This server enables LLMs to interact with web pages through structured accessibility snapshots, 

## Tech Stack
JS/TS, Node.js, Docker, GitHub Actions

## Quick Start
```bash
npm run build  # tsc
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
playwright-mcp/
  examples/
  extension/
  src/
  tests/
  utils/
  Dockerfile
  LICENSE
  README.md
  SECURITY.md
  cli.js
  config.d.ts
  eslint.config.mjs
  index.d.ts
  index.js
  package-lock.json
  package.json
  playwright.config.ts
  tsconfig.all.json
  tsconfig.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **index.js**: JavaScript entry point
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/copilot-setup-steps.yml**: CI/CD workflow
- **.github/workflows/publish.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included
- Mcp focused
- Automation focused
- Llm focused

## Dependencies
### npm (production)
- @modelcontextprotocol/sdk: ^1.16.0
- commander: ^13.1.0
- debug: ^4.4.1
- dotenv: ^17.2.0
- mime: ^4.0.7
- playwright: 1.55.0-alpha-1753913825000
- playwright-core: 1.55.0-alpha-1753913825000
- ws: ^8.18.1
- zod: ^3.24.1
- zod-to-json-schema: ^3.24.4

### npm (dev)
- @anthropic-ai/sdk: ^0.57.0
- @eslint/eslintrc: ^3.2.0
- @eslint/js: ^9.19.0
- @playwright/test: 1.55.0-alpha-1753913825000
- @stylistic/eslint-plugin: ^3.0.1
- @types/debug: ^4.1.12
- @types/node: ^22.13.10
- @types/ws: ^8.18.1
- @typescript-eslint/eslint-plugin: ^8.26.1
- @typescript-eslint/parser: ^8.26.1
- @typescript-eslint/utils: ^8.26.1
- esbuild: ^0.20.1
- eslint: ^9.19.0
- eslint-plugin-import: ^2.31.0
- eslint-plugin-notice: ^1.0.0
- ... and 2 more

## Ports
- Not detected

## Score Breakdown
- **Overall Score**: 103/120
- **Size**: 0.6 MB
- **Files**: 124
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
