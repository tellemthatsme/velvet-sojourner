# git-mcp

## Description
No description available

## Tech Stack
JS/TS, Node.js, React, Next, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # react-router dev
```
```bash
npm run start  # wrangler dev
```
```bash
npm run build  # react-router build
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
git-mcp/
  app/
  dist/
  img/
  public/
  src/
  static/
  tests/
  Dockerfile
  LICENSE
  README.md
  SECURITY.md
  biome.json
  components.json
  package-lock.json
  package.json
  playwright.config.ts
  pnpm-lock.yaml
  postcss.config.mjs
  react-router.config.ts
  tailwind.config.js
  tsconfig.cloudflare.json
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
  vitest.config.ts
  worker-configuration.d.ts
  wrangler.jsonc
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **vite.config.ts**: Vite build configuration
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/e2e-tests.yml**: CI/CD workflow
- **.github/workflows/run-tests.yml**: CI/CD workflow

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

## Dependencies
### npm (production)
- @ai-sdk/anthropic: ^1.2.10
- @ai-sdk/cohere: ^1.2.9
- @ai-sdk/google: ^1.2.13
- @ai-sdk/groq: ^1.2.8
- @ai-sdk/openai: ^1.3.20
- @ai-sdk/react: ^1.2.9
- @ai-sdk/xai: ^1.2.15
- @cloudflare/workers-oauth-provider: ^0.0.2
- @modelcontextprotocol/sdk: ^1.11.2
- @radix-ui/react-accordion: ^1.2.8
- @radix-ui/react-avatar: ^1.1.7
- @radix-ui/react-dialog: ^1.1.11
- @radix-ui/react-dropdown-menu: ^2.1.12
- @radix-ui/react-label: ^2.1.4
- @radix-ui/react-popover: ^1.1.11
- @radix-ui/react-scroll-area: ^1.2.6
- @radix-ui/react-select: ^2.2.2
- @radix-ui/react-separator: ^1.1.4
- @radix-ui/react-slot: ^1.2.0
- @radix-ui/react-tooltip: ^1.2.4
- @react-router/fs-routes: ^7.5.2
- @remix-run/cloudflare: ^2.16.5
- @types/react: ^19.1.2
- @types/react-dom: ^19.1.2
- agents: ^0.0.84
- ai: ^4.3.10
- class-variance-authority: ^0.7.1
- clsx: ^2.1.1
- dotenv: ^16.5.0
- falkordb: ^6.2.7
- ... and 18 more

### npm (dev)
- @cloudflare/vite-plugin: ^0.1.21
- @cloudflare/workers-types: ^4.20250505.0
- @playwright/test: ^1.52.0
- @react-router/dev: ^7.5.2
- @tailwindcss/postcss: ^4.1.4
- @tailwindcss/vite: ^4.1.4
- @types/node: ^20.17.31
- @types/node-fetch: ^2.6.12
- @types/react: ^19.0.1
- @types/react-dom: ^19.0.1
- husky: ^9.1.7
- lint-staged: ^15.5.1
- marked: ^15.0.11
- node-fetch: ^3.3.2
- prettier: ^3.5.3
- ... and 7 more

## Ports
- 5000
- 3000

## Score Breakdown
- **Overall Score**: 103/120
- **Size**: 80.2 MB
- **Files**: 179
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
