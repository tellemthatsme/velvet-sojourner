# prompts.chat

## Description
No description available

## Tech Stack
JS/TS, Node.js, React, Next, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # next dev
```
```bash
npm run start  # next start
```
```bash
npm run build  # prisma generate && next build
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
prompts.chat/
  docker/
  messages/
  packages/
  plugins/
  prisma/
  public/
  scripts/
  src/
  AGENTS.md
  CLAUDE-PLUGIN.md
  CLAUDE.md
  CONTRIBUTING.md
  DOCKER.md
  Dockerfile
  LICENSE
  PROMPTS.md
  README.md
  SELF-HOSTING.md
  components.json
  context7.json
  eslint.config.mjs
  mdx-components.tsx
  next.config.ts
  package-lock.json
  package.json
  postcss.config.mjs
  prisma.config.ts
  prompts.config.ts
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/docker-publish.yml**: CI/CD workflow
- **.github/workflows/reset-credits.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Chat focused

## Dependencies
### npm (production)
- @auth/prisma-adapter: ^2.11.1
- @aws-sdk/client-s3: ^3.948.0
- @hookform/resolvers: ^5.2.2
- @mdx-js/loader: ^3.1.1
- @mdx-js/react: ^3.1.1
- @modelcontextprotocol/sdk: ^1.24.3
- @monaco-editor/react: ^4.7.0
- @next/mdx: ^16.1.1
- @prisma/client: ^6.19.0
- @radix-ui/react-alert-dialog: ^1.1.15
- @radix-ui/react-avatar: ^1.1.11
- @radix-ui/react-checkbox: ^1.3.3
- @radix-ui/react-context-menu: ^2.2.16
- @radix-ui/react-dialog: ^1.1.15
- @radix-ui/react-dropdown-menu: ^2.1.16
- @radix-ui/react-label: ^2.1.8
- @radix-ui/react-popover: ^1.1.15
- @radix-ui/react-progress: ^1.1.8
- @radix-ui/react-scroll-area: ^1.2.10
- @radix-ui/react-select: ^2.2.6
- @radix-ui/react-separator: ^1.1.8
- @radix-ui/react-slot: ^1.2.4
- @radix-ui/react-switch: ^1.2.6
- @radix-ui/react-tabs: ^1.1.13
- @radix-ui/react-tooltip: ^1.2.8
- @sentry/nextjs: ^10.32.1
- @tailwindcss/typography: ^0.5.19
- @types/d3: ^7.4.3
- bcryptjs: ^3.0.3
- class-variance-authority: ^0.7.1
- ... and 23 more

### npm (dev)
- @clack/prompts: ^0.11.0
- @tailwindcss/postcss: ^4
- @testing-library/jest-dom: ^6.6.3
- @testing-library/react: ^16.1.0
- @testing-library/user-event: ^14.5.2
- @types/bcryptjs: ^2.4.6
- @types/node: ^20
- @types/react: ^19
- @types/react-dom: ^19
- @vitejs/plugin-react: ^4.3.4
- @vitest/coverage-v8: ^2.1.8
- @vitest/ui: ^2.1.8
- babel-plugin-react-compiler: 1.0.0
- eslint: ^9
- eslint-config-next: 16.0.7
- ... and 9 more

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 127.8 MB
- **Files**: 1483
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
