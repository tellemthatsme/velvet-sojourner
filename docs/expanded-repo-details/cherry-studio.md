# cherry-studio

## Description
No description available

## Tech Stack
JS/TS, Node.js, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # dotenv electron-vite dev
```
```bash
npm run start  # electron-vite preview
```
```bash
npm run build  # npm run typecheck && electron-vite build
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
cherry-studio/
  build/
  docs/
  packages/
  resources/
  scripts/
  src/
  tests/
  AGENTS.md
  CLAUDE.md
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README.md
  SECURITY.md
  biome.jsonc
  components.json
  dev-app-update.yml
  electron-builder.yml
  electron.vite.config.ts
  eslint.config.mjs
  package.json
  playwright.config.ts
  tsconfig.json
  tsconfig.node.json
  tsconfig.web.json
  vitest.config.ts
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/auto-i18n.yml**: CI/CD workflow
- **.github/workflows/claude-code-review.yml**: CI/CD workflow
- **.github/workflows/claude-translator.yml**: CI/CD workflow

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
- @anthropic-ai/claude-agent-sdk: patch:@anthropic-ai/claude-agent-sdk@npm%3A0.1.1#~/.yarn/patches/@anthropic-ai-claude-agent-sdk-npm-0.1.1-d937b73fed.patch
- @libsql/client: 0.14.0
- @libsql/win32-x64-msvc: ^0.4.7
- @napi-rs/system-ocr: patch:@napi-rs/system-ocr@npm%3A1.0.2#~/.yarn/patches/@napi-rs-system-ocr-npm-1.0.2-59e7a78e8b.patch
- @strongtz/win32-arm64-msvc: ^0.4.7
- font-list: ^2.0.0
- graceful-fs: ^4.2.11
- jsdom: 26.1.0
- node-stream-zip: ^1.15.0
- officeparser: ^4.2.0
- os-proxy-config: ^1.1.2
- selection-hook: ^1.0.12
- sharp: ^0.34.3
- swagger-jsdoc: ^6.2.8
- tesseract.js: patch:tesseract.js@npm%3A6.0.1#~/.yarn/patches/tesseract.js-npm-6.0.1-2562a7e46d.patch
- turndown: 7.2.0

### npm (dev)
- @agentic/exa: ^7.3.3
- @agentic/searxng: ^7.3.3
- @agentic/tavily: ^7.3.3
- @ai-sdk/amazon-bedrock: ^3.0.35
- @ai-sdk/google-vertex: ^3.0.40
- @ai-sdk/mistral: ^2.0.19
- @ai-sdk/perplexity: ^2.0.13
- @ant-design/v5-patch-for-react-19: ^1.0.3
- @anthropic-ai/sdk: ^0.41.0
- @anthropic-ai/vertex-sdk: patch:@anthropic-ai/vertex-sdk@npm%3A0.11.4#~/.yarn/patches/@anthropic-ai-vertex-sdk-npm-0.11.4-c19cb41edb.patch
- @aws-sdk/client-bedrock: ^3.840.0
- @aws-sdk/client-bedrock-runtime: ^3.840.0
- @aws-sdk/client-s3: ^3.840.0
- @biomejs/biome: 2.2.4
- @cherrystudio/ai-core: workspace:^1.0.0-alpha.18
- ... and 249 more

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 28.6 MB
- **Files**: 1916
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
