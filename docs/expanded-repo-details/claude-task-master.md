# claude-task-master

## Description
[![CI]( [![npm version]( [![Discord](

## Tech Stack
JS/TS, Node.js, Docker, GitHub Actions

## Quick Start
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
claude-task-master/
  apps/
  assets/
  bin/
  context/
  docs/
  mcp-server/
  scripts/
  src/
  tests/
  CHANGELOG.md
  CLAUDE.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README-task-master.md
  README.md
  biome.json
  index.js
  jest.config.js
  llms-install.md
  mcp-test.js
  output.json
  package-lock.json
  package.json
  test-clean-tags.js
  test-config-manager.js
  test-prd.txt
  test-tag-functions.js
  test-version-check-full.js
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **index.js**: JavaScript entry point
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/extension-ci.yml**: CI/CD workflow
- **.github/workflows/extension-release.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies
### npm (production)
- @ai-sdk/amazon-bedrock: ^2.2.9
- @ai-sdk/anthropic: ^1.2.10
- @ai-sdk/azure: ^1.3.17
- @ai-sdk/google: ^1.2.13
- @ai-sdk/google-vertex: ^2.2.23
- @ai-sdk/groq: ^1.2.9
- @ai-sdk/mistral: ^1.2.7
- @ai-sdk/openai: ^1.3.20
- @ai-sdk/perplexity: ^1.1.7
- @ai-sdk/xai: ^1.2.15
- @anthropic-ai/sdk: ^0.39.0
- @aws-sdk/credential-providers: ^3.817.0
- @inquirer/search: ^3.0.15
- @openrouter/ai-sdk-provider: ^0.4.5
- ai: ^4.3.10
- ajv: ^8.17.1
- ajv-formats: ^3.0.1
- boxen: ^8.0.1
- chalk: ^5.4.1
- cli-highlight: ^2.1.11
- cli-table3: ^0.6.5
- commander: ^11.1.0
- cors: ^2.8.5
- dotenv: ^16.3.1
- express: ^4.21.2
- fastmcp: ^3.5.0
- figlet: ^1.8.0
- fuse.js: ^7.1.0
- gpt-tokens: ^1.3.14
- gradient-string: ^3.0.0
- ... and 12 more

### npm (dev)
- @biomejs/biome: ^1.9.4
- @changesets/changelog-github: ^0.5.1
- @changesets/cli: ^2.28.1
- @types/jest: ^29.5.14
- execa: ^8.0.1
- ink: ^5.0.1
- jest: ^29.7.0
- jest-environment-node: ^29.7.0
- mock-fs: ^5.5.0
- prettier: ^3.5.3
- supertest: ^7.1.0
- tsx: ^4.16.2

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 8.0 MB
- **Files**: 662
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
