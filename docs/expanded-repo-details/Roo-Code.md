# Roo-Code

## Description
No description available

## Tech Stack
JS/TS, Node.js, Next, Docker, GitHub Actions

## Quick Start
```bash
npm run dev  # cd webview-ui && npm run dev
```
```bash
npm run build  # npm run vsix
```
```bash
docker build -t <name> . && docker run <name>
```

## Project Structure
```
Roo-Code/
  assets/
  audio/
  cline_docs/
  e2e/
  evals/
  locales/
  scripts/
  src/
  webview-ui/
  CHANGELOG.md
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  PRIVACY.md
  README.md
  ellipsis.yaml
  esbuild.js
  git
  jest.config.js
  knip.json
  package-lock.json
  package.json
  package.nls.ca.json
  package.nls.de.json
  package.nls.es.json
  package.nls.fr.json
  package.nls.hi.json
  package.nls.it.json
```

## Key Files
- **README.md**: Project overview and setup instructions
- **package.json**: Node.js dependencies and scripts
- **Dockerfile**: Container build instructions
- **tsconfig.json**: TypeScript configuration
- **.github/workflows/changeset-release.yml**: CI/CD workflow
- **.github/workflows/code-qa.yml**: CI/CD workflow
- **.github/workflows/codeql.yml**: CI/CD workflow

## Features
- Unit/integration tests
- Containerized deployment
- CI/CD pipeline
- Node.js/TypeScript ecosystem
- Documentation included
- Open source licensed

## Dependencies
### npm (production)
- @anthropic-ai/bedrock-sdk: ^0.10.2
- @anthropic-ai/sdk: ^0.37.0
- @anthropic-ai/vertex-sdk: ^0.7.0
- @aws-sdk/client-bedrock-runtime: ^3.779.0
- @google/genai: ^0.9.0
- @mistralai/mistralai: ^1.3.6
- @modelcontextprotocol/sdk: ^1.7.0
- @types/clone-deep: ^4.0.4
- @types/pdf-parse: ^1.1.4
- @types/tmp: ^0.2.6
- @types/turndown: ^5.0.5
- @types/vscode: ^1.95.0
- @vscode/codicons: ^0.0.36
- axios: ^1.7.4
- cheerio: ^1.0.0
- chokidar: ^4.0.1
- clone-deep: ^4.0.1
- default-shell: ^2.2.0
- delay: ^6.0.0
- diff: ^5.2.0
- diff-match-patch: ^1.0.5
- fast-deep-equal: ^3.1.3
- fast-xml-parser: ^4.5.1
- fastest-levenshtein: ^1.0.16
- fzf: ^0.5.2
- get-folder-size: ^5.0.0
- i18next: ^24.2.2
- isbinaryfile: ^5.0.2
- mammoth: ^1.8.0
- monaco-vscode-textmate-theme-converter: ^0.1.7
- ... and 27 more

### npm (dev)
- @changesets/cli: ^2.27.10
- @changesets/types: ^6.0.0
- @dotenvx/dotenvx: ^1.34.0
- @types/debug: ^4.1.12
- @types/diff: ^5.2.1
- @types/diff-match-patch: ^1.0.36
- @types/glob: ^8.1.0
- @types/jest: ^29.5.14
- @types/mocha: ^10.0.10
- @types/node: 20.x
- @types/node-cache: ^4.1.3
- @types/node-ipc: ^9.2.3
- @types/string-similarity: ^4.0.2
- @typescript-eslint/eslint-plugin: ^7.14.1
- @typescript-eslint/parser: ^7.11.0
- ... and 21 more

## Ports
- 3000

## Score Breakdown
- **Overall Score**: 108/120
- **Size**: 8.5 MB
- **Files**: 1163
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
