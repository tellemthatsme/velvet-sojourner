"""
Phase 2: Batch Repo Enhancer
Adds missing LICENSE, .gitignore, Dockerfile, README improvements
Processes repos by tier (A first, then B)
"""
import os
import json
import shutil
from datetime import datetime

REPOS_DIR = r'C:\temp\velvet-sojourner\repos'
SCAN_FILE = os.path.join(REPOS_DIR, '_SCAN_ALL_RESULTS.json')
LOG_FILE = r'C:\temp\velvet-sojourner\enhance_log.txt'

MIT_LICENSE = """MIT License

Copyright (c) 2026 AgentForge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

GITIGNORE_PYTHON = """# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
build/
.eggs/
*.egg
.env
.venv
venv/
*.log
.DS_Store
"""

GITIGNORE_NODE = """# Node
node_modules/
dist/
build/
.env
.env.local
*.log
.DS_Store
npm-debug.log*
yarn-debug.log*
yarn-error.log*
"""

GITIGNORE_GENERIC = """# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build
dist/
build/
*.exe
*.dll
*.so

# Env
.env
.env.local

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
"""

DOCKERFILE_PYTHON = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
"""

DOCKERFILE_NODE = """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000
CMD ["node", "index.js"]
"""

DOCKERFILE_GENERIC = """FROM ubuntu:22.04

WORKDIR /app

COPY . .

CMD ["/bin/bash"]
"""


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def add_license(repo_path, repo_name):
    """Add MIT license if missing"""
    if not repo_name.startswith('_') and not os.path.exists(os.path.join(repo_path, 'LICENSE')):
        has_lic = any(f.lower().startswith('license') or f.lower().startswith('licence')
                      for f in os.listdir(repo_path))
        if not has_lic:
            with open(os.path.join(repo_path, 'LICENSE'), 'w', encoding='utf-8') as f:
                f.write(MIT_LICENSE)
            return True
    return False


def add_gitignore(repo_path, languages):
    """Add .gitignore based on languages"""
    if os.path.exists(os.path.join(repo_path, '.gitignore')):
        return False

    if 'Python' in languages and 'JS/TS' in languages:
        content = GITIGNORE_PYTHON + '\n' + GITIGNORE_NODE
    elif 'Python' in languages:
        content = GITIGNORE_PYTHON
    elif 'JS/TS' in languages:
        content = GITIGNORE_NODE
    else:
        content = GITIGNORE_GENERIC

    with open(os.path.join(repo_path, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def add_dockerfile(repo_path, languages):
    """Add Dockerfile if missing"""
    if os.path.exists(os.path.join(repo_path, 'Dockerfile')):
        return False

    if 'Python' in languages:
        with open(os.path.join(repo_path, 'Dockerfile'), 'w', encoding='utf-8') as f:
            f.write(DOCKERFILE_PYTHON)
    elif 'JS/TS' in languages:
        with open(os.path.join(repo_path, 'Dockerfile'), 'w', encoding='utf-8') as f:
            f.write(DOCKERFILE_NODE)
    else:
        with open(os.path.join(repo_path, 'Dockerfile'), 'w', encoding='utf-8') as f:
            f.write(DOCKERFILE_GENERIC)
    return True


def enhance_readme(repo_path, repo_name):
    """Enhance README if missing or very short"""
    readme_file = None
    for f in os.listdir(repo_path):
        if f.lower().startswith('readme'):
            readme_file = f
            break

    if readme_file:
        path = os.path.join(repo_path, readme_file)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if len(content.strip()) < 50:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# {repo_name}\n\nAI-powered automation tool.\n\n## Usage\n\nSee source code for usage instructions.\n")
            return True
        return False
    else:
        with open(os.path.join(repo_path, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(f"# {repo_name}\n\nAI-powered automation tool.\n\n## Usage\n\nSee source code for usage instructions.\n")
        return True


def process_tier(results, tier_name):
    """Process all repos in a tier"""
    tier_repos = [r for r in results if r.get('tier') == tier_name]
    log(f"\n{'='*50}")
    log(f"Processing {tier_name}-Tier: {len(tier_repos)} repos")
    log(f"{'='*50}")

    stats = {'license_added': 0, 'gitignore_added': 0,
             'docker_added': 0, 'readme_enhanced': 0}

    for i, repo in enumerate(tier_repos):
        name = repo['name']
        path = os.path.join(REPOS_DIR, name)

        if not os.path.isdir(path):
            continue

        if (i + 1) % 50 == 0:
            log(f"  {tier_name}-Tier progress: {i+1}/{len(tier_repos)}")

        try:
            if add_license(path, name):
                stats['license_added'] += 1

            if add_gitignore(path, repo.get('languages', [])):
                stats['gitignore_added'] += 1

            if add_dockerfile(path, repo.get('languages', [])):
                stats['docker_added'] += 1

            if enhance_readme(path, name):
                stats['readme_enhanced'] += 1
        except Exception as e:
            log(f"  Error processing {name}: {e}")

    log(f"\n{tier_name}-Tier Results:")
    for k, v in stats.items():
        log(f"  {k}: {v}")
    return stats


def main():
    open(LOG_FILE, 'w').close()

    log("=" * 60)
    log("PHASE 2: BATCH REPO ENHANCER")
    log("=" * 60)

    if not os.path.exists(SCAN_FILE):
        log(f"ERROR: Scan file not found. Run scan_all_repos.py first.")
        return

    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['repos']
    log(f"Loaded {len(results)} repos from scan data")

    total_stats = {'license_added': 0, 'gitignore_added': 0,
                   'docker_added': 0, 'readme_enhanced': 0}

    for tier in ['A', 'B', 'C']:
        stats = process_tier(results, tier)
        for k, v in stats.items():
            total_stats[k] += v

    log(f"\n{'='*50}")
    log("FINAL TOTALS")
    log(f"{'='*50}")
    log(f"Repos processed: {len(results)}")
    for k, v in total_stats.items():
        log(f"  {k}: {v}")
    log(f"\nLog saved to: {LOG_FILE}")


if __name__ == '__main__':
    main()
