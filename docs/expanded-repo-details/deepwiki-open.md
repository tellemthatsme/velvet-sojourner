# deepwiki-open

## Description
**DeepWiki**は、GitHub、GitLab、または Bitbucket リポジトリのための美しくインタラクティブな Wiki を自動的に作成します！リポジトリ名を入力するだけで、DeepWiki は以下を行います：

## Tech Stack
Python, Node.js, React, Next, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # next dev --turbopack --port 3000
```
```bash
npm run start  # next start
```
```bash
npm run build  # next build
```
```bash
docker build -t <name> . && docker run <name>
```
```bash
docker-compose up
```

## Project Structure
```
deepwiki-open/
  api/
  public/
  screenshots/
  src/
  test/
  Dockerfile
  Dockerfile-ollama-local
  LICENSE
  Ollama-instruction.md
  README.es.md
  README.ja.md
  README.kr.md
  README.md
  README.pt-br.md
  README.vi.md
  README.zh-tw.md
  README.zh.md
  docker-compose.yml
  eslint.config.mjs
  next.config.ts
  package-lock.json
  package.json
  postcss.config.mjs
  pyproject.toml
  pytest.ini
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **docker-compose.yml**: Multi-container orchestration
- **pyproject.toml**: Python project configuration
- **.env.example**: Environment variable template
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/docker-build-push.yml**: CI/CD workflow

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
- mermaid: ^11.4.1
- next: 15.3.1
- next-intl: ^4.1.0
- next-themes: ^0.4.6
- react: ^19.0.0
- react-dom: ^19.0.0
- react-icons: ^5.5.0
- react-markdown: ^10.1.0
- react-syntax-highlighter: ^15.6.1
- rehype-raw: ^7.0.0
- remark-gfm: ^4.0.1
- svg-pan-zoom: ^3.6.2

### npm (dev)
- @eslint/eslintrc: ^3
- @tailwindcss/postcss: ^4
- @types/node: ^20
- @types/react: ^19
- @types/react-dom: ^19
- @types/react-syntax-highlighter: ^15.5.13
- eslint: ^9
- eslint-config-next: 15.3.1
- tailwindcss: ^4
- typescript: ^5

## Ports
- 8000
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 4.1 MB
- **Files**: 109
  - README: ✅
  - License: ✅
  - Dockerfile: ✅
  - Docker Compose: ✅
  - CI/CD: ✅
  - Tests: ✅
  - Makefile: ❌
  - package.json: ✅
  - requirements.txt: ❌
  - pyproject.toml: ✅
  - Cargo.toml: ❌
  - go.mod: ❌
