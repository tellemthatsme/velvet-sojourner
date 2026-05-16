# cogno-control-center

## Description
**URL**:

## Tech Stack
JS/TS, Node.js, React, Next, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # vite
```
```bash
npm run build  # vite build
```
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
cogno-control-center/
  docker/
  docs/
  public/
  scripts/
  src/
  supabase/
  tests/
  Dockerfile
  LICENSE
  README.md
  bun.lockb
  components.json
  docker-compose.dev.yml
  docker-compose.yml
  eslint.config.js
  index.html
  nginx.conf
  nginx.default.conf
  package-lock.json
  package.json
  playwright.config.ts
  postcss.config.js
  tailwind.config.ts
  tsconfig.app.json
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **.env.example**: Environment variable template
- **index.html**: Application entry point
- **vite.config.ts**: Vite build configuration
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/ci-cd.yml**: Configuration file
- **.github/workflows/ci-cd.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies
### npm (production)
- @hookform/resolvers: ^3.10.0
- @playwright/test: ^1.55.0
- @radix-ui/react-accordion: ^1.2.11
- @radix-ui/react-alert-dialog: ^1.1.14
- @radix-ui/react-aspect-ratio: ^1.1.7
- @radix-ui/react-avatar: ^1.1.10
- @radix-ui/react-checkbox: ^1.3.2
- @radix-ui/react-collapsible: ^1.1.11
- @radix-ui/react-context-menu: ^2.2.15
- @radix-ui/react-dialog: ^1.1.14
- @radix-ui/react-dropdown-menu: ^2.1.15
- @radix-ui/react-hover-card: ^1.1.14
- @radix-ui/react-label: ^2.1.7
- @radix-ui/react-menubar: ^1.1.15
- @radix-ui/react-navigation-menu: ^1.2.13
- @radix-ui/react-popover: ^1.1.14
- @radix-ui/react-progress: ^1.1.7
- @radix-ui/react-radio-group: ^1.3.7
- @radix-ui/react-scroll-area: ^1.2.9
- @radix-ui/react-select: ^2.2.5
- @radix-ui/react-separator: ^1.1.7
- @radix-ui/react-slider: ^1.3.5
- @radix-ui/react-slot: ^1.2.3
- @radix-ui/react-switch: ^1.2.5
- @radix-ui/react-tabs: ^1.1.12
- @radix-ui/react-toast: ^1.2.14
- @radix-ui/react-toggle: ^1.1.9
- @radix-ui/react-toggle-group: ^1.1.10
- @radix-ui/react-tooltip: ^1.2.7
- @supabase/supabase-js: ^2.89.0
- ... and 29 more

### npm (dev)
- @eslint/js: ^9.32.0
- @tailwindcss/typography: ^0.5.16
- @types/node: ^22.16.5
- @types/react: ^18.3.23
- @types/react-dom: ^18.3.7
- @vitejs/plugin-react-swc: ^3.11.0
- autoprefixer: ^10.4.21
- eslint: ^9.32.0
- eslint-plugin-react-hooks: ^5.2.0
- eslint-plugin-react-refresh: ^0.4.20
- globals: ^15.15.0
- lovable-tagger: ^1.1.9
- postcss: ^8.5.6
- tailwindcss: ^3.4.17
- typescript: ^5.8.3
- ... and 2 more

## Ports
- 5672
- 5432
- 3000
- 3001
- 6333

## Score Breakdown
- **Overall Score**: 98/120
- **Size**: 1.0 MB
- **Files**: 133
  - README: ✅
  - License: ❌
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ✅
  - requirements.txt: ❌
  - pyproject.toml: ❌
  - Cargo.toml: ❌
  - go.mod: ❌
