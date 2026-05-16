# dyad

## Description
Dyad is a local, open-source AI app builder. It's fast, private and fully under your control — like Lovable, v0, or Bolt, but running right on your machine.

## Tech Stack
JS/TS, Node.js, React, Docker, GitHub Actions

## Quick Start
```bash
npm run start  # electron-forge start
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
dyad/
  assets/
  drizzle/
  scaffold/
  scripts/
  src/
  tools/
  Dockerfile
  LICENSE
  README.md
  biome.json
  components.json
  drizzle.config.ts
  forge.config.ts
  forge.env.d.ts
  index.html
  package-lock.json
  package.json
  tsconfig.app.json
  tsconfig.json
  tsconfig.node.json
  vite.main.config.mts
  vite.preload.config.mts
  vite.renderer.config.mts
  vitest.config.ts
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **.env.example**: Environment variable template
- **index.html**: Application entry point
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow
- **.github/workflows/release.yml**: CI/CD workflow

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
- @ai-sdk/anthropic: ^1.2.8
- @ai-sdk/google: ^1.2.10
- @ai-sdk/openai: ^1.3.7
- @ai-sdk/openai-compatible: ^0.2.13
- @biomejs/biome: ^1.9.4
- @dyad-sh/supabase-management-js: v1.0.0
- @monaco-editor/react: ^4.7.0-rc.0
- @openrouter/ai-sdk-provider: ^0.4.5
- @radix-ui/react-accordion: ^1.2.4
- @radix-ui/react-dialog: ^1.1.7
- @radix-ui/react-dropdown-menu: ^2.1.7
- @radix-ui/react-label: ^2.1.4
- @radix-ui/react-popover: ^1.1.7
- @radix-ui/react-select: ^2.2.2
- @radix-ui/react-separator: ^1.1.2
- @radix-ui/react-slot: ^1.1.2
- @radix-ui/react-switch: ^1.2.0
- @radix-ui/react-toggle: ^1.1.3
- @radix-ui/react-toggle-group: ^1.1.3
- @radix-ui/react-tooltip: ^1.1.8
- @rollup/plugin-commonjs: ^28.0.3
- @tailwindcss/typography: ^0.5.16
- @tailwindcss/vite: ^4.1.3
- @tanstack/react-router: ^1.114.34
- @types/uuid: ^10.0.0
- @vitejs/plugin-react: ^4.3.4
- ai: ^4.3.4
- better-sqlite3: ^11.9.1
- class-variance-authority: ^0.7.1
- clsx: ^2.1.1
- ... and 32 more

### npm (dev)
- @electron-forge/cli: ^7.8.0
- @electron-forge/maker-deb: ^7.8.0
- @electron-forge/maker-rpm: ^7.8.0
- @electron-forge/maker-squirrel: ^7.8.0
- @electron-forge/maker-zip: ^7.8.0
- @electron-forge/plugin-auto-unpack-natives: ^7.8.0
- @electron-forge/plugin-fuses: ^7.8.0
- @electron-forge/plugin-vite: ^7.8.0
- @electron-forge/publisher-github: ^7.8.0
- @electron/fuses: ^1.8.0
- @testing-library/react: ^16.3.0
- @types/better-sqlite3: ^7.6.13
- @types/kill-port: ^2.0.3
- @types/node: ^22.14.0
- @types/react: ^19.0.10
- ... and 12 more

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 103/120
- **Size**: 2.9 MB
- **Files**: 285
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
