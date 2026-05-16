import json, os, re, textwrap
from pathlib import Path

SCAN_PATH = r"C:\temp\velvet-sojourner\repos\_SCAN_ALL_RESULTS.json"
OUT_DIR = r"C:\temp\velvet-sojourner\docs\expanded-repo-details"
REPOS_BASE = r"C:\temp\velvet-sojourner\repos"

with open(SCAN_PATH) as f:
    data = json.load(f)

repos = [r for r in data['repos'] if r.get('tier') == 'A' and r.get('score', 0) >= 75]
repos.sort(key=lambda x: x['score'], reverse=True)
top50 = repos[:50]

def get_clean_description(repo):
    d = repo.get('description', '') or ''
    d = re.sub(r'<[^>]+>', '', d)
    d = re.sub(r'https?://\S+', '', d)
    d = re.sub(r'\s+', ' ', d).strip()
    return d[:200] if len(d) > 200 else d

def read_file_safe(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except:
        return None

def get_top_listing(repo_path):
    try:
        items = list(Path(repo_path).iterdir())
        dirs = sorted([p.name + '/' for p in items if p.is_dir() and not p.name.startswith('.')])
        files = sorted([p.name for p in items if p.is_file() and not p.name.startswith('.')])
        return dirs[:20] + files[:20]
    except:
        return []

def parse_package_json(repo_path):
    p = os.path.join(repo_path, 'package.json')
    content = read_file_safe(p)
    if not content:
        return None, None, None
    try:
        pkg = json.loads(content)
        deps = pkg.get('dependencies', {})
        dev_deps = pkg.get('devDependencies', {})
        scripts = pkg.get('scripts', {})
        return deps, dev_deps, scripts
    except:
        return None, None, None

def parse_requirements_txt(repo_path):
    p = os.path.join(repo_path, 'requirements.txt')
    content = read_file_safe(p)
    if not content:
        return []
    return [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]

def parse_pyproject_toml(repo_path):
    p = os.path.join(repo_path, 'pyproject.toml')
    content = read_file_safe(p)
    if not content:
        return None
    deps = []
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('['):
            parts = line.split('=')
            if len(parts) == 2:
                key = parts[0].strip().strip('"').strip("'")
                val = parts[1].strip().strip('"').strip("'")
                if key and val and not key.startswith('#') and not key.startswith('['):
                    deps.append(f"{key}={val}")
    return deps

def parse_cargo_toml(repo_path):
    p = os.path.join(repo_path, 'Cargo.toml')
    content = read_file_safe(p)
    if not content:
        return None
    return content[:2000]

def parse_go_mod(repo_path):
    p = os.path.join(repo_path, 'go.mod')
    content = read_file_safe(p)
    if not content:
        return None
    return content[:2000]

def detect_run_commands(repo_path, scripts):
    commands = []
    if scripts:
        for key in ['dev', 'start', 'serve', 'run', 'build']:
            if key in scripts:
                commands.append(f"npm run {key}  # {scripts[key]}")
    if os.path.exists(os.path.join(repo_path, 'Makefile')):
        commands.append("make  # or make run/dev")
    if os.path.exists(os.path.join(repo_path, 'Dockerfile')):
        commands.append("docker build -t <name> . && docker run <name>")
    if os.path.exists(os.path.join(repo_path, 'docker-compose.yml')) or os.path.exists(os.path.join(repo_path, 'docker-compose.yaml')):
        commands.append("docker-compose up")
    if not commands:
        commands.append("Check README for run instructions")
    return commands

def detect_ports(repo_path):
    ports = []
    df = os.path.join(repo_path, 'Dockerfile')
    content = read_file_safe(df)
    if content:
        for m in re.finditer(r'EXPOSE\s+(\d+)', content):
            ports.append(m.group(1))
    dcf = os.path.join(repo_path, 'docker-compose.yml')
    if not os.path.exists(dcf):
        dcf = os.path.join(repo_path, 'docker-compose.yaml')
    content = read_file_safe(dcf)
    if content:
        for m in re.finditer(r'"(\d+):\d+"', content):
            ports.append(m.group(1).strip('"'))
        for m in re.finditer(r'(\d+):\d+', content):
            parts = m.group(1).split('\n')[0].strip()
            if parts.isdigit() and parts not in ports:
                ports.append(parts)
    if os.path.exists(os.path.join(repo_path, '.env.example')):
        env = read_file_safe(os.path.join(repo_path, '.env.example'))
        if env:
            for m in re.finditer(r'PORT=(\d+)', env):
                ports.append(m.group(1))
            for m in re.finditer(r'(?:API|APP|SERVER)_PORT=(\d+)', env):
                ports.append(m.group(1))
    if not ports:
        if scripts := json.loads(read_file_safe(os.path.join(repo_path, 'package.json')) or '{}').get('scripts', {}):
            for s in scripts.values():
                for m in re.finditer(r'--port[= ](\d+)', s):
                    ports.append(m.group(1))
                for m in re.finditer(r':(\d{4,5})', s):
                    ports.append(m.group(1))
    return list(set(ports))[:5] if ports else ['Not detected']

def detect_ci_type(repo):
    ci_actions = {
        'has_ci': 'GitHub Actions',
        'has_gitlab_ci': 'GitLab CI',
        'has_jenkins': 'Jenkins',
        'has_circle': 'CircleCI',
        'has_travis': 'Travis CI',
    }
    for key, name in ci_actions.items():
        if repo.get(key):
            return name
    return None

def get_related_repos(repo, all_repos, category_key='category'):
    name = repo['name'].lower()
    related = []
    words = set(re.split(r'[-_\s]+', name))
    for r in all_repos[:200]:
        if r['name'] == repo['name']:
            continue
        rname = r['name'].lower()
        rwords = set(re.split(r'[-_\s]+', rname))
        common = words & rwords
        if len(common) >= 2:
            related.append(r['name'])
    return related[:5]

def generate_md(repo):
    name = repo['name']
    repo_path = repo['path']
    score = repo['score']
    size = repo['size_mb']
    files = repo['file_count']
    description = get_clean_description(repo)
    
    deps, dev_deps, scripts = parse_package_json(repo_path)
    reqs = parse_requirements_txt(repo_path)
    cargo = parse_cargo_toml(repo_path)
    go_mod = parse_go_mod(repo_path)
    listing = get_top_listing(repo_path)
    run_cmds = detect_run_commands(repo_path, scripts)
    ports = detect_ports(repo_path)
    
    tech_stack = []
    lang = repo.get('languages', ['Unknown'])[0]
    if lang != 'Unknown':
        tech_stack.append(lang)
    if deps:
        tech_stack.append('Node.js')
        for key in ['react', 'vue', 'next', 'nuxt', 'svelte', 'angular']:
            if any(key in d.lower() for d in deps):
                tech_stack.append(key.title())
    if reqs:
        tech_stack.append('Python')
    if cargo:
        tech_stack.append('Rust')
    if go_mod:
        tech_stack.append('Go')
    if repo.get('has_dockerfile') or repo.get('has_docker_compose'):
        tech_stack.append('Docker')
    if repo.get('has_ci'):
        ci_name = detect_ci_type(repo)
        if ci_name:
            tech_stack.append(ci_name)
    tech_stack = list(dict.fromkeys(tech_stack))
    
    md = f"""# {name}

## Description
{description or 'No description available'}

## Tech Stack
{', '.join(tech_stack) if tech_stack else 'Not detected'}

## Quick Start
"""
    for cmd in run_cmds:
        md += f"```bash\n{cmd}\n```\n"
    
    md += f"\n## Project Structure\n```\n{name}/\n"
    for item in listing:
        md += f"  {item}\n"
    md += "```\n"
    
    md += f"\n## Key Files\n"
    key_files = []
    for fname in ['README.md', 'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml',
                  'docker-compose.yaml', 'Makefile', 'pyproject.toml', 'Cargo.toml', 'go.mod',
                  '.env.example', 'index.html', 'main.py', 'app.py', 'server.py', 'index.js', 'main.ts',
                  'config.ts', 'config.json', 'vite.config.ts', 'next.config.js', 'tsconfig.json',
                  '.github/workflows/ci.yml', '.github/workflows/ci-cd.yml']:
        if os.path.exists(os.path.join(repo_path, fname)):
            desc_map = {
                'README.md': 'Project overview and setup instructions',
                'package.json': 'Node.js dependencies and scripts',
                'requirements.txt': 'Python dependencies',
                'Dockerfile': 'Container build instructions',
                'docker-compose.yml': 'Multi-container orchestration',
                'docker-compose.yaml': 'Multi-container orchestration',
                'Makefile': 'Build automation targets',
                'pyproject.toml': 'Python project configuration',
                'Cargo.toml': 'Rust project configuration',
                'go.mod': 'Go module definition',
                '.env.example': 'Environment variable template',
                'index.html': 'Application entry point',
                'main.py': 'Main Python entry point',
                'app.py': 'Main Python application',
                'server.py': 'Server entry point',
                'index.js': 'JavaScript entry point',
                'main.ts': 'TypeScript entry point',
                'tsconfig.json': 'TypeScript configuration',
                'vite.config.ts': 'Vite build configuration',
                'next.config.js': 'Next.js configuration',
            }
            key_files.append((fname, desc_map.get(fname, 'Configuration file')))
    
    for gf_wild in ['.github/workflows/*.yml']:
        base = os.path.join(repo_path, '.github', 'workflows')
        if os.path.isdir(base):
            for wf in sorted(os.listdir(base))[:3]:
                if wf.endswith('.yml'):
                    key_files.append((f'.github/workflows/{wf}', 'CI/CD workflow'))
    
    if key_files:
        for kf, desc in key_files:
            md += f"- **{kf}**: {desc}\n"
    else:
        md += "- No key config files detected\n"
    
    md += "\n## Features\n"
    features = []
    
    if repo.get('has_tests'):
        features.append('Unit/integration tests')
    if repo.get('has_dockerfile'):
        features.append('Containerized deployment')
    if repo.get('has_docker_compose'):
        features.append('Multi-service orchestration')
    if repo.get('has_ci'):
        features.append('CI/CD pipeline')
    if repo.get('has_makefile'):
        features.append('Build automation')
    if deps:
        features.append('Node.js/TypeScript ecosystem')
    if reqs:
        features.append('Python ecosystem')
    if cargo:
        features.append('Rust native performance')
    if os.path.exists(os.path.join(repo_path, '.env.example')):
        features.append('Environment configuration')
    if any(f.lower().endswith(('.md', '.rst')) for f in listing):
        features.append('Documentation included')
    if os.path.exists(os.path.join(repo_path, 'LICENSE')):
        features.append('Open source licensed')
    if any('test' in f.lower() for f in listing):
        features.append('Test suite included')
    
    for kw in ['api', 'agent', 'cli', 'dashboard', 'bot', 'trading', 'crypto', 'mcp',
               'monitoring', 'analytics', 'automation', 'platform', 'framework', 'sdk',
               'rag', 'llm', 'chat', 'search', 'database', 'streaming', 'visualization']:
        if kw in name.lower() or kw in description.lower():
            features.append(f'{kw.capitalize()} focused')
    
    features = list(dict.fromkeys(features))
    for f in features[:12]:
        md += f"- {f}\n"
    
    md += "\n## Dependencies\n"
    has_deps = False
    
    if deps:
        has_deps = True
        md += "### npm (production)\n"
        sorted_deps = sorted(deps.items(), key=lambda x: x[0])
        for pkg, ver in sorted_deps[:30]:
            md += f"- {pkg}: {ver}\n"
        if len(deps) > 30:
            md += f"- ... and {len(deps)-30} more\n"
    if dev_deps:
        has_deps = True
        md += "\n### npm (dev)\n"
        sorted_dd = sorted(dev_deps.items(), key=lambda x: x[0])
        for pkg, ver in sorted_dd[:15]:
            md += f"- {pkg}: {ver}\n"
        if len(dev_deps) > 15:
            md += f"- ... and {len(dev_deps)-15} more\n"
    if reqs:
        has_deps = True
        md += "\n### Python (pip)\n"
        for r in reqs[:20]:
            md += f"- {r}\n"
        if len(reqs) > 20:
            md += f"- ... and {len(reqs)-20} more\n"
    
    if not has_deps:
        md += "No dependency files detected\n"
    
    md += "\n## Ports\n"
    for p in ports:
        md += f"- {p}\n"
    
    md += "\n## Score Breakdown\n"
    md += f"- **Overall Score**: {score}/120\n"
    md += f"- **Size**: {size} MB\n"
    md += f"- **Files**: {files}\n"
    
    scan_fields = {
        'has_readme': 'README',
        'has_license': 'License',
        'has_dockerfile': 'Dockerfile',
        'has_docker_compose': 'Docker Compose',
        'has_ci': 'CI/CD',
        'has_tests': 'Tests',
        'has_makefile': 'Makefile',
        'has_package_json': 'package.json',
        'has_requirements': 'requirements.txt',
        'has_pyproject': 'pyproject.toml',
        'has_cargo': 'Cargo.toml',
        'has_go_mod': 'go.mod',
    }
    for key, label in scan_fields.items():
        val = repo.get(key, False)
        md += f"  - {label}: {'✅' if val else '❌'}\n"
    
    return md

generated = []
for repo in top50:
    name = repo['name']
    print(f"Generating: {name} (score={repo['score']})")
    md = generate_md(repo)
    out_path = os.path.join(OUT_DIR, f"{name}.md")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(md)
    generated.append((name, repo['score']))

# Generate INDEX.md
total_size = sum(os.path.getsize(os.path.join(OUT_DIR, f"{name}.md")) for name, _ in generated)
index = "# Expanded Repo Documentation - Top 50 A-Tier Repos\n\n"
index += f"**Generated**: 2026-05-10\n\n"
index += f"**Total docs**: {len(generated)}\n\n"
index += f"**Total size**: {total_size:,} bytes ({total_size/1024:.1f} KB)\n\n"
index += "## Repos by Score\n\n"
index += "| # | Repo | Score | Size (MB) | Files |\n"
index += "|---|------|-------|-----------|-------|\n"

for i, (name, _) in enumerate(generated, 1):
    r = next(r for r in top50 if r['name'] == name)
    index += f"| {i} | [{name}]({name}.md) | {r['score']} | {r['size_mb']} | {r['file_count']} |\n"

index += "\n## Summary Statistics\n"
scores = [r['score'] for r in top50]
sizes = [r['size_mb'] for r in top50]
files = [r['file_count'] for r in top50]
index += f"- **Score range**: {min(scores)}-{max(scores)}\n"
index += f"- **Average score**: {sum(scores)/len(scores):.1f}\n"
index += f"- **Total size**: {sum(sizes):.1f} MB\n"
index += f"- **Total files**: {sum(files):,}\n"
index += f"- **Docs directory**: `docs/expanded-repo-details/`\n"

with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write(index)

print(f"\nDone! Generated {len(generated)} expanded docs")
print(f"INDEX.md: {os.path.join(OUT_DIR, 'INDEX.md')}")
print(f"Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
