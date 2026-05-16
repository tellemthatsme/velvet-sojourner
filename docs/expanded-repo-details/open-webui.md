# open-webui

## Description
[![Discord](

## Tech Stack
Python, Node.js, Next, Svelte, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # npm run pyodide:fetch && vite dev --host
```
```bash
npm run build  # npm run pyodide:fetch && vite build
```
```bash
make  # or make run/dev
```
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
open-webui/
  backend/
  cypress/
  docs/
  kubernetes/
  scripts/
  src/
  static/
  test/
  CHANGELOG.md
  CODE_OF_CONDUCT.md
  CONTRIBUTOR_LICENSE_AGREEMENT
  Dockerfile
  INSTALLATION.md
  LICENSE
  LICENSE_HISTORY
  Makefile
  README.md
  TROUBLESHOOTING.md
  confirm_remove.sh
  contribution_stats.py
  cypress.config.ts
  demo.gif
  docker-compose.a1111-test.yaml
  docker-compose.amdgpu.yaml
  docker-compose.api.yaml
  docker-compose.data.yaml
  docker-compose.gpu.yaml
  docker-compose.otel.yaml
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yaml**: Multi-container orchestration
- **Makefile**: Build automation targets
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **vite.config.ts**: Vite build configuration
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/build-release.yml**: CI/CD workflow
- **.github/workflows/deploy-to-hf-spaces.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Build automation
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed
- Test suite included

## Dependencies
### npm (production)
- @azure/msal-browser: ^4.5.0
- @codemirror/lang-javascript: ^6.2.2
- @codemirror/lang-python: ^6.1.6
- @codemirror/language-data: ^6.5.1
- @codemirror/theme-one-dark: ^6.1.2
- @floating-ui/dom: ^1.7.2
- @huggingface/transformers: ^3.0.0
- @mediapipe/tasks-vision: ^0.10.17
- @pyscript/core: ^0.4.32
- @sveltejs/adapter-node: ^2.0.0
- @sveltejs/svelte-virtual-list: ^3.0.1
- @tiptap/core: ^3.0.7
- @tiptap/extension-bubble-menu: ^2.26.1
- @tiptap/extension-code-block-lowlight: ^3.0.7
- @tiptap/extension-drag-handle: ^3.0.7
- @tiptap/extension-file-handler: ^3.0.7
- @tiptap/extension-floating-menu: ^2.26.1
- @tiptap/extension-highlight: ^3.0.7
- @tiptap/extension-image: ^3.0.7
- @tiptap/extension-link: ^3.0.7
- @tiptap/extension-list: ^3.0.7
- @tiptap/extension-table: ^3.0.7
- @tiptap/extension-typography: ^3.0.7
- @tiptap/extension-youtube: ^3.0.7
- @tiptap/extensions: ^3.0.7
- @tiptap/pm: ^3.0.7
- @tiptap/starter-kit: ^3.0.7
- @xyflow/svelte: ^0.1.19
- async: ^3.2.5
- bits-ui: ^0.21.15
- ... and 55 more

### npm (dev)
- @sveltejs/adapter-auto: 3.2.2
- @sveltejs/adapter-static: ^3.0.2
- @sveltejs/kit: ^2.5.20
- @sveltejs/vite-plugin-svelte: ^3.1.1
- @tailwindcss/container-queries: ^0.1.1
- @tailwindcss/postcss: ^4.0.0
- @tailwindcss/typography: ^0.5.13
- @typescript-eslint/eslint-plugin: ^8.31.1
- @typescript-eslint/parser: ^8.31.1
- cypress: ^13.15.0
- eslint: ^8.56.0
- eslint-config-prettier: ^9.1.0
- eslint-plugin-cypress: ^3.4.0
- eslint-plugin-svelte: ^2.43.0
- i18next-parser: ^9.0.1
- ... and 12 more

## Ports
- 8080

## Score Breakdown
- **Overall Score**: 116/120
- **Size**: 96.7 MB
- **Files**: 4698
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ✅
  - package.json: ✅
  - requirements.txt: ❌
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
