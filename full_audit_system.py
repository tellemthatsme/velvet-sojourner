"""
FULL REPOSITORY AUDIT & DOCUMENTATION SYSTEM
Comprehensive analysis of all 740 repos with per-repo reviews, recommendations,
developer documentation, and actionable advice.
"""
import os
import json
import csv
import shutil
from pathlib import Path
from collections import defaultdict, Counter
import re

REPOS_DIR = Path(r"C:\temp\velvet-sojourner\repos")
AUDIT_DIR = Path(r"C:\temp\velvet-sojourner\audit")
AUDIT_DIR.mkdir(exist_ok=True)
DOCS_DIR = Path(r"C:\temp\velvet-sojourner\docs")
DOCS_DIR.mkdir(exist_ok=True)

def get_owner(name):
    for prefix in ["tellemthatsme_", "woodsai69rme_", "leahmfoots_", "acidlink_", "Ashlee69r_"]:
        if name.startswith(prefix):
            return prefix.rstrip("_"), name[len(prefix):]
    return None, name

def detect_languages(repo_path):
    langs = set()
    # Check marker files first
    if (repo_path / "package.json").exists(): langs.add("javascript")
    if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists() or (repo_path / "setup.py").exists(): langs.add("python")
    if (repo_path / "Cargo.toml").exists(): langs.add("rust")
    if (repo_path / "go.mod").exists(): langs.add("go")
    # Check top-level files for extensions (limit depth to avoid resource exhaustion)
    ext_map = {
        ".ts": "typescript", ".tsx": "react", ".vue": "vue", ".rs": "rust",
        ".cpp": "c/c++", ".c": "c/c++", ".h": "c/c++", ".java": "java",
        ".rb": "ruby", ".php": "php", ".cs": "csharp", ".swift": "swift",
        ".kt": "kotlin", ".scala": "scala", ".r": "r", ".jl": "julia",
        ".dart": "dart", ".ex": "elixir", ".exs": "elixir"
    }
    try:
        for f in repo_path.iterdir():
            if f.is_file() and f.suffix in ext_map:
                langs.add(ext_map[f.suffix])
        # Only check one subdir deep for extensions
        for subdir in repo_path.iterdir():
            if subdir.is_dir() and subdir.name not in [".git", "node_modules", "venv", ".venv", "__pycache__", "target", "dist", "build"]:
                try:
                    for f in subdir.iterdir():
                        if f.is_file() and f.suffix in ext_map:
                            langs.add(ext_map[f.suffix])
                except:
                    pass
    except:
        pass
    return sorted(langs)

def detect_frameworks(repo_path, languages):
    frameworks = set()
    if "python" in languages:
        req = repo_path / "requirements.txt"
        if req.exists():
            try:
                text = req.read_text(encoding="utf-8", errors="ignore").lower()
                if "fastapi" in text: frameworks.add("FastAPI")
                if "flask" in text: frameworks.add("Flask")
                if "django" in text: frameworks.add("Django")
                if "langchain" in text: frameworks.add("LangChain")
                if "crewai" in text: frameworks.add("CrewAI")
                if "openai" in text: frameworks.add("OpenAI")
                if "anthropic" in text: frameworks.add("Anthropic")
                if "transformers" in text: frameworks.add("Transformers")
                if "torch" in text: frameworks.add("PyTorch")
                if "tensorflow" in text: frameworks.add("TensorFlow")
                if "streamlit" in text: frameworks.add("Streamlit")
                if "gradio" in text: frameworks.add("Gradio")
                if "httpx" in text: frameworks.add("HTTPX")
                if "requests" in text: frameworks.add("Requests")
                if "pydantic" in text: frameworks.add("Pydantic")
                if "sqlalchemy" in text: frameworks.add("SQLAlchemy")
                if "docker" in text: frameworks.add("Docker SDK")
            except:
                pass
    if "javascript" in languages or "typescript" in languages or "react" in languages:
        pkg = repo_path / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
                deps = {**(data.get("dependencies", {})), **(data.get("devDependencies", {}))}
                dep_names = [d.lower() for d in deps.keys()]
                if any("react" in d for d in dep_names): frameworks.add("React")
                if any("next" in d for d in dep_names): frameworks.add("Next.js")
                if any("vue" in d for d in dep_names): frameworks.add("Vue")
                if any("angular" in d for d in dep_names): frameworks.add("Angular")
                if any("express" in d for d in dep_names): frameworks.add("Express")
                if any("fastify" in d for d in dep_names): frameworks.add("Fastify")
                if any("nestjs" in d for d in dep_names): frameworks.add("NestJS")
                if any("electron" in d for d in dep_names): frameworks.add("Electron")
                if any("tauri" in d for d in dep_names): frameworks.add("Tauri")
                if any("tailwind" in d for d in dep_names): frameworks.add("TailwindCSS")
                if any("prisma" in d for d in dep_names): frameworks.add("Prisma")
                if any("trpc" in d for d in dep_names): frameworks.add("tRPC")
                if any("openai" in d for d in dep_names): frameworks.add("OpenAI")
                if any("langchain" in d for d in dep_names): frameworks.add("LangChain")
            except:
                pass
    if "rust" in languages:
        cargo = repo_path / "Cargo.toml"
        if cargo.exists():
            try:
                text = cargo.read_text(encoding="utf-8", errors="ignore").lower()
                if "tokio" in text: frameworks.add("Tokio")
                if "axum" in text: frameworks.add("Axum")
                if "actix" in text: frameworks.add("Actix")
                if "rocket" in text: frameworks.add("Rocket")
            except:
                pass
    if "go" in languages:
        mod = repo_path / "go.mod"
        if mod.exists():
            try:
                text = mod.read_text(encoding="utf-8", errors="ignore").lower()
                if "gin" in text: frameworks.add("Gin")
                if "echo" in text: frameworks.add("Echo")
                if "fiber" in text: frameworks.add("Fiber")
            except:
                pass
    return sorted(frameworks)

def get_category(name, frameworks, languages):
    nl = name.lower()
    # Check frameworks first
    if any(f in ["LangChain", "CrewAI", "OpenAI", "Anthropic", "Transformers"] for f in frameworks):
        return "ai-agent"
    # Check name patterns
    if any(k in nl for k in ["agent", "ai-", "llm", "gpt", "claude", "bot", "seek", "operator", "adk", "eliza", "aider", "openai", "anthropic"]):
        return "ai-agent"
    elif any(k in nl for k in ["trade", "crypto", "stock", "forex", "nexus", "market", "portfolio"]):
        return "trading"
    elif any(k in nl for k in ["auto", "n8n", "workflow", "scrape", "crawl", "browser-use", "scheduler"]):
        return "automation"
    elif any(k in nl for k in ["webui", "dashboard", "ui", "chat", "app", "studio", "web", "portal", "interface"]):
        return "web-app"
    elif any(k in nl for k in ["mcp", "server", "api", "gateway", "proxy", "backend"]):
        return "mcp-server"
    elif any(k in nl for k in ["dev", "tool", "cli", "sdk", "coder", "code", "ide", "editor", "debugger"]):
        return "dev-tool"
    return "utility"

def calculate_quality_score(repo):
    score = 0
    # README present
    if repo["has_readme"]: score += 20
    # License present
    if repo["license"]: score += 15
    # Docker present
    if repo["has_dockerfile"]: score += 15
    if repo["has_compose"]: score += 10
    # File count (substantial project)
    if repo["file_count"] > 1000: score += 20
    elif repo["file_count"] > 500: score += 15
    elif repo["file_count"] > 100: score += 10
    elif repo["file_count"] > 50: score += 5
    # Multiple languages (indicates complexity)
    if len(repo["languages"]) >= 3: score += 10
    elif len(repo["languages"]) >= 2: score += 5
    # Frameworks (modern stack)
    if len(repo["frameworks"]) >= 2: score += 10
    elif len(repo["frameworks"]) >= 1: score += 5
    return min(score, 100)

def calculate_valuation(repo):
    base = 0
    size_mb = repo["size_mb"]
    files = repo["file_count"]
    quality = repo["quality_score"]

    if size_mb > 300: base = 2000
    elif size_mb > 200: base = 1500
    elif size_mb > 100: base = 1000
    elif size_mb > 50: base = 500
    elif size_mb > 20: base = 250
    elif size_mb > 10: base = 150
    elif size_mb > 5: base = 75
    else: base = 25

    if files > 5000: base += 1000
    elif files > 2000: base += 500
    elif files > 1000: base += 250
    elif files > 500: base += 100
    elif files > 100: base += 50

    cat_multipliers = {
        "ai-agent": 1.5,
        "trading": 1.3,
        "web-app": 1.2,
        "automation": 1.2,
        "mcp-server": 1.1,
        "dev-tool": 1.0,
        "utility": 0.6
    }
    base *= cat_multipliers.get(repo["category"], 0.6)

    # Quality bonus
    base *= (0.5 + quality / 100)

    if repo["has_dockerfile"]: base += 200
    if repo["has_compose"]: base += 100

    return round(base)

def generate_recommendations(repo):
    recs = []
    if not repo["has_readme"]:
        recs.append("CRITICAL: Add README.md with setup instructions, usage examples, and architecture overview")
    if not repo["license"]:
        recs.append("LEGAL: Add LICENSE file (MIT recommended for maximum adoption)")
    if not repo["has_dockerfile"] and not repo["has_compose"]:
        if "python" in repo["languages"]:
            recs.append("DEPLOY: Add Dockerfile (Python template available)")
        elif any(l in repo["languages"] for l in ["javascript", "typescript", "react"]):
            recs.append("DEPLOY: Add Dockerfile with multi-stage Node.js build")
        elif "rust" in repo["languages"]:
            recs.append("DEPLOY: Add Dockerfile with cargo build")
        elif "go" in repo["languages"]:
            recs.append("DEPLOY: Add Dockerfile with static binary build")
    if repo["file_count"] < 20:
        recs.append("CONTENT: Repository appears minimal; expand functionality or merge with related project")
    if not repo["frameworks"] and len(repo["languages"]) > 0:
        recs.append("ARCHITECTURE: Consider adopting a recognized framework for maintainability")
    if repo["quality_score"] < 40:
        recs.append("QUALITY: Low quality score; focus on documentation, testing, and structure")
    if "python" in repo["languages"]:
        recs.append("TESTING: Consider adding pytest test suite")
    if any(l in repo["languages"] for l in ["javascript", "typescript"]):
        recs.append("BUILD: Verify package.json scripts and build process")
    return recs

def generate_use_case(repo):
    cat = repo["category"]
    name = repo["base_name"].lower()
    if cat == "ai-agent":
        return f"Build autonomous AI agents for {name.replace('-', ' ')}. Integrates with LLMs for reasoning and task execution."
    elif cat == "trading":
        return f"Automated trading system for {name.replace('-', ' ')}. Execute strategies across exchanges with risk management."
    elif cat == "automation":
        return f"Workflow automation for {name.replace('-', ' ')}. Connect APIs, process data, and trigger actions automatically."
    elif cat == "web-app":
        return f"Web application providing {name.replace('-', ' ')} functionality. User-facing interface with backend services."
    elif cat == "mcp-server":
        return f"Model Context Protocol server enabling AI agents to interact with {name.replace('-', ' ')} services."
    elif cat == "dev-tool":
        return f"Developer tool for {name.replace('-', ' ')}. Improves productivity and code quality."
    else:
        return f"Utility project for {name.replace('-', ' ')}. Supports broader AI/automation workflows."

def generate_difficulty(repo):
    score = repo["quality_score"]
    if repo["has_dockerfile"] and repo["has_readme"]:
        return "Easy"
    elif repo["has_dockerfile"] or repo["has_readme"]:
        return "Medium"
    elif score > 50:
        return "Medium"
    else:
        return "Hard"

def scan_repo(repo_path):
    name = repo_path.name
    owner, base_name = get_owner(name)
    files = list(repo_path.rglob("*"))
    file_count = sum(1 for f in files if f.is_file())
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    size_mb = round(total_size / (1024*1024), 2)

    has_dockerfile = (repo_path / "Dockerfile").exists()
    has_compose = (repo_path / "docker-compose.yml").exists() or (repo_path / "docker-compose.yaml").exists()
    has_readme = (repo_path / "README.md").exists()
    has_gitignore = (repo_path / ".gitignore").exists()
    has_env_example = (repo_path / ".env.example").exists() or (repo_path / ".env.sample").exists()

    # License
    license_type = None
    for lic_name in ["LICENSE", "LICENSE.md", "LICENSE.txt", "license", "license.md"]:
        if (repo_path / lic_name).exists():
            try:
                lic_text = (repo_path / lic_name).read_text(encoding="utf-8", errors="ignore").upper()
                if "MIT" in lic_text: license_type = "MIT"
                elif "APACHE" in lic_text: license_type = "Apache-2.0"
                elif "GPL" in lic_text: license_type = "GPL"
                elif "BSD" in lic_text: license_type = "BSD"
                elif "UNLICENSE" in lic_text: license_type = "Unlicense"
                elif "MOZILLA" in lic_text: license_type = "MPL"
                elif "CC0" in lic_text: license_type = "CC0"
                else: license_type = "Other"
            except:
                pass
            break

    languages = detect_languages(repo_path)
    frameworks = detect_frameworks(repo_path, languages)
    category = get_category(name, frameworks, languages)

    # Description
    description = None
    if has_readme:
        try:
            text = (repo_path / "README.md").read_text(encoding="utf-8", errors="ignore")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines[:20]:
                if not line.startswith("#") and not line.startswith("!") and not line.startswith("[") and not line.startswith("<") and len(line) > 15:
                    description = line[:350]
                    break
        except:
            pass

    repo = {
        "name": name,
        "base_name": base_name,
        "owner": owner,
        "category": category,
        "size_mb": size_mb,
        "file_count": file_count,
        "has_dockerfile": has_dockerfile,
        "has_compose": has_compose,
        "has_readme": has_readme,
        "has_gitignore": has_gitignore,
        "has_env_example": has_env_example,
        "languages": languages,
        "frameworks": frameworks,
        "license": license_type,
        "description": description,
        "deployable": has_dockerfile or has_compose
    }

    repo["quality_score"] = calculate_quality_score(repo)
    repo["valuation"] = calculate_valuation(repo)
    repo["recommendations"] = generate_recommendations(repo)
    repo["use_case"] = generate_use_case(repo)
    repo["difficulty"] = generate_difficulty(repo)

    return repo

# MAIN SCAN
print("=" * 70)
print("FULL REPOSITORY AUDIT & DOCUMENTATION SYSTEM")
print("=" * 70)
print("\nPhase 1: Scanning all 740 repositories...")

all_repos = []
for p in sorted(REPOS_DIR.iterdir()):
    if not p.is_dir():
        continue
    repo = scan_repo(p)
    all_repos.append(repo)

all_repos.sort(key=lambda x: x["valuation"], reverse=True)

print(f"  Scanned: {len(all_repos)} repos")
print(f"  Total size: {round(sum(r['size_mb'] for r in all_repos)/1024, 2)} GB")
print(f"  Total valuation: ${sum(r['valuation'] for r in all_repos):,}")
print(f"  Avg quality: {round(sum(r['quality_score'] for r in all_repos)/len(all_repos))}/100")

# Generate reports
print("\nPhase 2: Generating reports...")

# JSON master
data = {
    "audit_date": "2026-04-30",
    "total_repos": len(all_repos),
    "total_size_gb": round(sum(r['size_mb'] for r in all_repos)/1024, 2),
    "total_valuation": sum(r['valuation'] for r in all_repos),
    "avg_quality": round(sum(r['quality_score'] for r in all_repos)/len(all_repos), 1),
    "avg_valuation": round(sum(r['valuation'] for r in all_repos)/len(all_repos)),
    "deployable_count": sum(1 for r in all_repos if r['deployable']),
    "repos": all_repos
}
with open(AUDIT_DIR / "full-audit-master.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("  full-audit-master.json")

# CSV master
with open(AUDIT_DIR / "full-audit-master.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "rank", "name", "base_name", "owner", "category", "size_mb", "file_count",
        "languages", "frameworks", "has_dockerfile", "has_compose", "has_readme",
        "has_gitignore", "has_env_example", "license", "deployable", "quality_score",
        "valuation", "difficulty", "use_case", "recommendations", "description"
    ])
    writer.writeheader()
    for i, r in enumerate(all_repos, 1):
        row = dict(r)
        row["rank"] = i
        row["languages"] = ", ".join(row["languages"])
        row["frameworks"] = ", ".join(row["frameworks"])
        row["recommendations"] = " | ".join(row["recommendations"])
        writer.writerow(row)
print("  full-audit-master.csv")

# Per-repo Markdown reports
print("\nPhase 3: Generating individual repo reports...")
repo_reports_dir = AUDIT_DIR / "repo-reports"
repo_reports_dir.mkdir(exist_ok=True)

# Summary per repo (batch into one file per 50)
for batch_idx in range(0, len(all_repos), 50):
    batch = all_repos[batch_idx:batch_idx+50]
    batch_num = batch_idx // 50 + 1
    with open(repo_reports_dir / f"repos-batch-{batch_num}.md", "w", encoding="utf-8") as f:
        f.write(f"# Repository Reports - Batch {batch_num} (Repos {batch_idx+1}-{batch_idx+len(batch)})\n\n")
        for r in batch:
            f.write(f"## {r['name']}\n\n")
            f.write(f"**Base Name:** {r['base_name']}  \n")
            f.write(f"**Owner:** {r['owner'] or 'unprefixed'}  \n")
            f.write(f"**Category:** {r['category']}  \n")
            f.write(f"**Size:** {r['size_mb']} MB | **Files:** {r['file_count']}  \n")
            f.write(f"**Languages:** {', '.join(r['languages']) or 'N/A'}  \n")
            f.write(f"**Frameworks:** {', '.join(r['frameworks']) or 'N/A'}  \n")
            f.write(f"**License:** {r['license'] or 'Unknown'}  \n")
            f.write(f"**Quality Score:** {r['quality_score']}/100  \n")
            f.write(f"**Valuation:** ${r['valuation']:,}  \n")
            f.write(f"**Deployable:** {'YES' if r['deployable'] else 'No'}  \n")
            f.write(f"**Difficulty:** {r['difficulty']}  \n")
            f.write(f"**Use Case:** {r['use_case']}  \n\n")
            if r['recommendations']:
                f.write("**Recommendations:**\n")
                for rec in r['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")
            if r['description']:
                f.write(f"**Description:** {r['description'][:200]}\n\n")
            f.write("---\n\n")
    print(f"  repos-batch-{batch_num}.md ({len(batch)} repos)")

# Category reports
print("\nPhase 4: Generating category reports...")
cats = defaultdict(list)
for r in all_repos:
    cats[r['category']].append(r)

for cat_name, cat_repos in cats.items():
    with open(AUDIT_DIR / f"category-{cat_name}.md", "w", encoding="utf-8") as f:
        f.write(f"# CATEGORY AUDIT: {cat_name.upper().replace('-', ' ')}\n\n")
        f.write(f"**Repos:** {len(cat_repos)}  \n")
        f.write(f"**Total Value:** ${sum(r['valuation'] for r in cat_repos):,}  \n")
        f.write(f"**Avg Quality:** {round(sum(r['quality_score'] for r in cat_repos)/len(cat_repos), 1)}/100  \n")
        f.write(f"**Deployable:** {sum(1 for r in cat_repos if r['deployable'])}  \n\n")
        f.write("## TOP REPOSITORIES\n\n")
        f.write("| Rank | Name | Size | Quality | Value | Deployable | Difficulty |\n")
        f.write("|------|------|------|---------|-------|------------|------------|\n")
        for i, r in enumerate(sorted(cat_repos, key=lambda x: -x['valuation'])[:50], 1):
            deploy = "YES" if r['deployable'] else "no"
            f.write(f"| {i} | {r['name']} | {r['size_mb']} MB | {r['quality_score']} | ${r['valuation']:,} | {deploy} | {r['difficulty']} |\n")
        f.write("\n## RECOMMENDATIONS FOR THIS CATEGORY\n\n")
        f.write(f"1. Focus on repos with quality score > 60 (top {sum(1 for r in cat_repos if r['quality_score'] > 60)} repos)\n")
        f.write(f"2. Prioritize Dockerizing repos with value > $500 ({sum(1 for r in cat_repos if r['valuation'] > 500 and not r['deployable'])} need Docker)\n")
        f.write(f"3. Verify licenses for {sum(1 for r in cat_repos if not r['license'])} repos missing LICENSE\n")
    print(f"  category-{cat_name}.md")

# Developer documentation templates
print("\nPhase 5: Generating developer documentation...")

# Docker template
docker_template = """# Docker Setup Guide
## For {repo_name}

### Prerequisites
- Docker installed
- Docker Compose installed

### Quick Start
```bash
# Clone the repository
git clone <repo-url>
cd {repo_name}

# Build and run
{build_cmd}

# Access the application
{access_info}
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your values
```

### Production Deployment
```bash
docker-compose -f docker-compose.yml up -d
```
"""

with open(DOCS_DIR / "docker-template.md", "w", encoding="utf-8") as f:
    f.write(docker_template.format(repo_name="[REPO_NAME]", build_cmd="docker build -t myapp . && docker run -p 8080:8080 myapp", access_info="Open http://localhost:8080"))

# API documentation template
api_template = """# API Documentation
## {repo_name}

### Base URL
```
http://localhost:{port}/api/v1
```

### Authentication
{auth_info}

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /deploy | Deploy service |

### Example Request
```bash
curl -X POST http://localhost:{port}/api/v1/deploy \\
  -H "Content-Type: application/json" \\
  -d '{{"repo": "my-repo"}}'
```
"""

with open(DOCS_DIR / "api-template.md", "w", encoding="utf-8") as f:
    f.write(api_template.format(repo_name="[REPO_NAME]", port="8000", auth_info="Bearer token required"))

# Deployment checklist
checklist = """# Deployment Checklist

## Pre-Deployment
- [ ] README.md reviewed
- [ ] .env.example configured
- [ ] Dependencies installed (`pip install -r requirements.txt` or `npm install`)
- [ ] Tests passing (`pytest` or `npm test`)
- [ ] Dockerfile present
- [ ] docker-compose.yml present (optional but recommended)

## Docker Build
- [ ] Image builds successfully: `docker build -t {repo_name} .`
- [ ] Container runs: `docker run -p 8080:8080 {repo_name}`
- [ ] Health endpoint responds: `curl http://localhost:8080/health`

## Production
- [ ] Environment variables set
- [ ] SSL configured (Traefik/Nginx)
- [ ] Logging enabled
- [ ] Monitoring configured (Prometheus/Grafana)
- [ ] Backup strategy defined
"""

with open(DOCS_DIR / "deployment-checklist.md", "w", encoding="utf-8") as f:
    f.write(checklist)

# Master audit report
print("\nPhase 6: Generating master audit report...")
with open(AUDIT_DIR / "MASTER_AUDIT_REPORT.md", "w", encoding="utf-8") as f:
    f.write("# MASTER AUDIT REPORT\n")
    f.write("## Complete Analysis of 740 AI Agent Repositories\n\n")
    f.write(f"**Date:** 2026-04-30  \n")
    f.write(f"**Total Repositories:** {len(all_repos)}  \n")
    f.write(f"**Total Size:** {round(sum(r['size_mb'] for r in all_repos)/1024, 2)} GB  \n")
    f.write(f"**Total Valuation:** ${sum(r['valuation'] for r in all_repos):,}  \n")
    f.write(f"**Average Quality:** {round(sum(r['quality_score'] for r in all_repos)/len(all_repos), 1)}/100  \n")
    f.write(f"**Deployable:** {sum(1 for r in all_repos if r['deployable'])} ({round(100*sum(1 for r in all_repos if r['deployable'])/len(all_repos))}%)  \n")
    f.write(f"**With README:** {sum(1 for r in all_repos if r['has_readme'])}  \n")
    f.write(f"**With License:** {sum(1 for r in all_repos if r['license'])}  \n\n")

    f.write("---\n\n")
    f.write("## EXECUTIVE SUMMARY\n\n")
    f.write("This audit covers 740 unique repositories collected from 5 GitHub accounts. ")
    f.write("Each repository was analyzed for code quality, deployment readiness, documentation, ")
    f.write("and estimated development value.\n\n")

    f.write("### Key Findings\n\n")
    f.write(f"1. **Quality Gap:** Only {sum(1 for r in all_repos if r['quality_score'] >= 60)} repos ({round(100*sum(1 for r in all_repos if r['quality_score'] >= 60)/len(all_repos))}%) score above 60/100\n")
    f.write(f"2. **Documentation Crisis:** {sum(1 for r in all_repos if not r['has_readme'])} repos ({round(100*sum(1 for r in all_repos if not r['has_readme'])/len(all_repos))}%) lack README files\n")
    f.write(f"3. **License Uncertainty:** {sum(1 for r in all_repos if not r['license'])} repos ({round(100*sum(1 for r in all_repos if not r['license'])/len(all_repos))}%) have no visible license\n")
    f.write(f"4. **Deployment Gap:** {sum(1 for r in all_repos if not r['deployable'])} repos ({round(100*sum(1 for r in all_repos if not r['deployable'])/len(all_repos))}%) lack Docker support\n")
    f.write(f"5. **High-Value Targets:** {sum(1 for r in all_repos if r['valuation'] >= 1000)} repos valued at $1,000+ each\n\n")

    f.write("---\n\n")
    f.write("## CATEGORY BREAKDOWN\n\n")
    f.write("| Category | Count | Value | Avg Quality | Deployable | Priority |\n")
    f.write("|----------|-------|-------|-------------|------------|----------|\n")
    for cat_name in sorted(cats.keys(), key=lambda x: -len(cats[x])):
        cr = cats[cat_name]
        f.write(f"| {cat_name} | {len(cr)} | ${sum(r['valuation'] for r in cr):,} | {round(sum(r['quality_score'] for r in cr)/len(cr), 1)} | {sum(1 for r in cr if r['deployable'])} | {'HIGH' if cat_name in ['ai-agent', 'trading'] else 'MEDIUM'} |\n")

    f.write("\n---\n\n")
    f.write("## TOP 50 HIGHEST-VALUE REPOSITORIES\n\n")
    f.write("| # | Name | Category | Value | Quality | Deployable | Difficulty | Key Action |\n")
    f.write("|---|------|----------|-------|---------|------------|------------|------------|\n")
    for i, r in enumerate(all_repos[:50], 1):
        deploy = "YES" if r['deployable'] else "ADD DOCKER"
        action = r['recommendations'][0] if r['recommendations'] else "OK"
        f.write(f"| {i} | {r['name']} | {r['category']} | ${r['valuation']:,} | {r['quality_score']} | {deploy} | {r['difficulty']} | {action.split(':')[0]} |\n")

    f.write("\n---\n\n")
    f.write("## QUALITY DISTRIBUTION\n\n")
    q_ranges = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "50-59": 0, "40-49": 0, "0-39": 0}
    for r in all_repos:
        q = r['quality_score']
        if q >= 90: q_ranges["90-100"] += 1
        elif q >= 80: q_ranges["80-89"] += 1
        elif q >= 70: q_ranges["70-79"] += 1
        elif q >= 60: q_ranges["60-69"] += 1
        elif q >= 50: q_ranges["50-59"] += 1
        elif q >= 40: q_ranges["40-49"] += 1
        else: q_ranges["0-39"] += 1
    for rng, cnt in q_ranges.items():
        bar = "█" * (cnt // 5)
        f.write(f"{rng}: {cnt} repos {bar}\n")

    f.write("\n---\n\n")
    f.write("## ACTIONABLE RECOMMENDATIONS\n\n")
    f.write("### Immediate (This Week)\n")
    f.write(f"1. Add Dockerfiles to top 50 repos (currently {sum(1 for r in all_repos[:50] if not r['deployable'])} missing)\n")
    f.write(f"2. Verify licenses for top 100 repos ({sum(1 for r in all_repos[:100] if not r['license'])} unknown)\n")
    f.write(f"3. Remove or archive {sum(1 for r in all_repos if r['quality_score'] < 20)} repos with quality < 20\n\n")

    f.write("### Short-Term (This Month)\n")
    f.write(f"4. Dockerize all repos with valuation > $500 ({sum(1 for r in all_repos if r['valuation'] > 500 and not r['deployable'])} repos)\n")
    f.write(f"5. Add README files to {sum(1 for r in all_repos if not r['has_readme'])} repos missing documentation\n")
    f.write(f"6. Standardize .env.example across {sum(1 for r in all_repos if not r['has_env_example'])} repos\n\n")

    f.write("### Long-Term (This Quarter)\n")
    f.write("7. Build CI/CD pipeline to auto-test Docker builds\n")
    f.write("8. Create deployment templates for each category\n")
    f.write("9. Build automated quality scoring dashboard\n")
    f.write("10. Archive repos not updated in 12+ months\n\n")

    f.write("---\n\n")
    f.write("## FILES GENERATED\n\n")
    f.write("| File | Description |\n")
    f.write("|------|-------------|\n")
    f.write("| full-audit-master.json | Complete machine-readable audit |\n")
    f.write("| full-audit-master.csv | Spreadsheet format |\n")
    f.write("| repos-batch-*.md | Individual repo reports (15 batches) |\n")
    f.write("| category-*.md | Per-category analysis (7 files) |\n")
    f.write("| docker-template.md | Dockerfile template |\n")
    f.write("| api-template.md | API documentation template |\n")
    f.write("| deployment-checklist.md | Production deployment checklist |\n")
    f.write("| MASTER_AUDIT_REPORT.md | This document |\n")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
print(f"\nGenerated files in {AUDIT_DIR}:")
for f in sorted(AUDIT_DIR.iterdir()):
    size = f.stat().st_size / 1024
    print(f"  {f.name:<35} {size:>8.1f} KB")
print(f"\nGenerated files in {DOCS_DIR}:")
for f in sorted(DOCS_DIR.iterdir()):
    size = f.stat().st_size / 1024
    print(f"  {f.name:<35} {size:>8.1f} KB")
print(f"\nTotal audit size: {sum(f.stat().st_size for f in AUDIT_DIR.rglob('*') if f.is_file()) / 1024 / 1024:.2f} MB")
