# muse-master-dashboard

## Description
> Your complete dashboard for AI video generators, music distribution, social media tools — with promos, discount codes, and the latest industry news.

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
muse-master-dashboard/
  public/
  src/
  supabase/
  Dockerfile
  LICENSE
  README.md
  bun.lock
  bun.lockb
  components.json
  docker-compose.yml
  eslint.config.js
  index.html
  netlify.toml
  nginx.conf
  package-lock.json
  package.json
  playwright-fixture.ts
  playwright.config.ts
  postcss.config.js
  render.yaml
  tailwind.config.ts
  tsconfig.app.json
  tsconfig.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **index.html**: Application entry point
- **vite.config.ts**: Vite build configuration
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/ci.yml**: Configuration file
- **.github/workflows/ci.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Documentation included
- Open source licensed
- Dashboard focused

## Dependencies
### npm (production)
- @hookform/resolvers: ^3.10.0
- @lovable.dev/cloud-auth-js: ^1.0.1
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
- @supabase/supabase-js: ^2.101.1
- ... and 22 more

### npm (dev)
- @eslint/js: ^9.32.0
- @playwright/test: ^1.57.0
- @tailwindcss/typography: ^0.5.16
- @testing-library/jest-dom: ^6.6.0
- @testing-library/react: ^16.0.0
- @types/node: ^22.16.5
- @types/react: ^18.3.23
- @types/react-dom: ^18.3.7
- @vitejs/plugin-react-swc: ^3.11.0
- autoprefixer: ^10.4.21
- eslint: ^9.32.0
- eslint-plugin-react-hooks: ^5.2.0
- eslint-plugin-react-refresh: ^0.4.20
- globals: ^15.15.0
- jsdom: ^20.0.3
- ... and 7 more

## Ports
- 80
- 8080

## Score Breakdown
- **Overall Score**: 103/120
- **Size**: 1.1 MB
- **Files**: 143
  - README: ✅
  - License: ✅
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
