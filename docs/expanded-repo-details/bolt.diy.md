# bolt.diy

## Description
[![bolt.diy: AI-Powered Full-Stack Web Development in the Browser](./public/social_preview_index.jpg)](

## Tech Stack
JS/TS, Node.js, React, Vue, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # node pre-start.cjs  && remix vite:dev
```
```bash
npm run start  # node -e "const { spawn } = require('child_process'); const isWindows = process.platform === 'win32'; const cmd = isWindows ? 'npm run start:windows' : 'npm run start:unix'; const child = spawn(cmd, { shell: true, stdio: 'inherit' }); child.on('exit', code => process.exit(code));"
```
```bash
npm run build  # remix vite:build
```
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
bolt.diy/
  app/
  assets/
  docs/
  electron/
  functions/
  icons/
  public/
  scripts/
  types/
  CHANGES.md
  CONTRIBUTING.md
  Dockerfile
  FAQ.md
  LICENSE
  PROJECT.md
  README.md
  bindings.sh
  changelog.md
  docker-compose.yaml
  electron-builder.yml
  electron-update.yml
  eslint.config.mjs
  load-context.ts
  notarize.cjs
  package.json
  pnpm-lock.yaml
  pre-start.cjs
  tsconfig.json
  uno.config.ts
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yaml**: Multi-container orchestration
- **.env.example**: Environment variable template
- **vite.config.ts**: Vite build configuration
- **tsconfig.json**: TypeScript configuration

## Features
- Unit/integration tests
- Containerized deployment
- Multi-service orchestration
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Environment configuration
- Documentation included
- Open source licensed

## Dependencies
### npm (production)
- @ai-sdk/amazon-bedrock: 1.0.6
- @ai-sdk/anthropic: 0.0.39
- @ai-sdk/cohere: 1.0.3
- @ai-sdk/deepseek: 0.1.3
- @ai-sdk/google: 0.0.52
- @ai-sdk/mistral: 0.0.43
- @ai-sdk/openai: 1.1.2
- @codemirror/autocomplete: ^6.18.3
- @codemirror/commands: ^6.7.1
- @codemirror/lang-cpp: ^6.0.2
- @codemirror/lang-css: ^6.3.1
- @codemirror/lang-html: ^6.4.9
- @codemirror/lang-javascript: ^6.2.2
- @codemirror/lang-json: ^6.0.1
- @codemirror/lang-markdown: ^6.3.1
- @codemirror/lang-python: ^6.1.6
- @codemirror/lang-sass: ^6.0.2
- @codemirror/lang-vue: ^0.1.3
- @codemirror/lang-wast: ^6.0.2
- @codemirror/language: ^6.10.6
- @codemirror/search: ^6.5.8
- @codemirror/state: ^6.4.1
- @codemirror/view: ^6.35.0
- @headlessui/react: ^2.2.0
- @heroicons/react: ^2.2.0
- @iconify-json/svg-spinners: ^1.2.1
- @lezer/highlight: ^1.2.1
- @nanostores/react: ^0.7.3
- @octokit/rest: ^21.0.2
- @octokit/types: ^13.6.2
- ... and 79 more

### npm (dev)
- @blitz/eslint-plugin: 0.1.0
- @cloudflare/workers-types: ^4.20241127.0
- @electron/notarize: ^2.5.0
- @iconify-json/ph: ^1.2.1
- @iconify/types: ^2.0.0
- @remix-run/dev: ^2.15.2
- @remix-run/serve: ^2.15.2
- @testing-library/jest-dom: ^6.6.3
- @testing-library/react: ^16.2.0
- @types/diff: ^5.2.3
- @types/dom-speech-recognition: ^0.0.4
- @types/electron: ^1.6.12
- @types/file-saver: ^2.0.7
- @types/js-cookie: ^3.0.6
- @types/path-browserify: ^1.0.3
- ... and 30 more

## Ports
- 1
- 5173

## Score Breakdown
- **Overall Score**: 113/120
- **Size**: 4.4 MB
- **Files**: 464
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
