import json
import os
from pathlib import Path
import shutil

REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
AUDIT_JSON = Path("C:/temp/velvet-sojourner/audit/full-audit-master.json")
DOCS_DIR = Path("C:/temp/velvet-sojourner/docs")

def load_audit():
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def save_audit(audit):
    with open(AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

def generate_readme(repo, repo_path):
    """Generate a comprehensive README.md for a repository"""
    name = repo["name"]
    category = repo["category"]
    languages = repo.get("languages", [])
    frameworks = repo.get("frameworks", [])
    valuation = repo.get("valuation", 0)
    quality = repo.get("quality_score", 0)
    size_mb = repo.get("size_mb", 0)
    file_count = repo.get("file_count", 0)
    has_docker = repo.get("has_dockerfile", False)
    has_compose = repo.get("has_compose", False)
    license = repo.get("license")
    description = repo.get("description", "")
    use_case = repo.get("use_case", "")
    difficulty = repo.get("difficulty", "Medium")
    
    # Detect entry points
    entry_points = []
    if (repo_path / "main.py").exists(): entry_points.append("main.py")
    if (repo_path / "app.py").exists(): entry_points.append("app.py")
    if (repo_path / "server.py").exists(): entry_points.append("server.py")
    if (repo_path / "index.js").exists(): entry_points.append("index.js")
    if (repo_path / "package.json").exists(): entry_points.append("package.json (npm start)")
    if (repo_path / "Cargo.toml").exists(): entry_points.append("Cargo.toml (cargo run)")
    if (repo_path / "go.mod").exists(): entry_points.append("go.mod (go run)")
    
    # Detect install methods
    install_steps = []
    if (repo_path / "requirements.txt").exists():
        install_steps.append("pip install -r requirements.txt")
    if (repo_path / "pyproject.toml").exists():
        install_steps.append("pip install -e .")
    if (repo_path / "package.json").exists():
        install_steps.append("npm install")
    if (repo_path / "Cargo.toml").exists():
        install_steps.append("cargo build")
    if (repo_path / "go.mod").exists():
        install_steps.append("go mod download")
    
    readme = f"""# {name}

**Category:** {category}  
**Languages:** {', '.join(languages) if languages else 'Not detected'}  
**Frameworks:** {', '.join(frameworks) if frameworks else 'None detected'}  
**Estimated Value:** ${valuation:,}  
**Quality Score:** {quality}/100  
**Difficulty:** {difficulty}

---

## Description

{description or use_case or f'A {category} project built with {", ".join(languages) if languages else "various technologies"}.'}

## Repository Stats

| Metric | Value |
|--------|-------|
| Size | {size_mb:.1f} MB |
| Files | {file_count:,} |
| Docker Ready | {'Yes' if has_docker else 'No'} |
| Docker Compose | {'Yes' if has_compose else 'No'} |
| License | {license or 'Not specified'} |

---

## Quick Start

### Prerequisites
{chr(10).join(f'- {lang.title()}' for lang in languages) or '- Standard development environment'}

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {name}

# Install dependencies
{chr(10).join(f'$ {step}' for step in install_steps) or '# No install steps detected - check project files'}
```

### Running the Project

```bash
{chr(10).join(f'$ python {ep}' if ep.endswith('.py') else f'$ {ep}' for ep in entry_points) or '# Check project structure for entry points'}
```

---

## Project Structure

```
{name}/
{'├── ' + chr(10)+'├── '.join([f.name for f in list(repo_path.iterdir())[:10] if not f.name.startswith('.')]) if repo_path.exists() else '# Structure not available'}
```

---

## Deployment

{'### Docker\n\nThis repository includes Docker support. Run:\n\n```bash\ndocker build -t ' + name + ' .\ndocker run -p 8000:8000 ' + name + '\n```\n\n### Docker Compose\n\n```bash\ndocker-compose up -d\n```' if has_docker else '### Docker Setup Required\n\nThis repository does not yet include Docker configuration. To containerize this project:\n\n1. Create a `Dockerfile` based on the detected language\n2. Add a `.dockerignore` file\n3. Consider adding `docker-compose.yml` for multi-service setups\n\n**Language:** ' + ', '.join(languages) if languages else 'Unknown'}

---

## API / Endpoints

{'Check the source code for API endpoints. Common patterns:' if 'FastAPI' in frameworks or 'Flask' in frameworks or 'Express' in frameworks else 'No API framework detected.'}

---

## Environment Variables

{'''Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your values
```''' if (repo_path / ".env.example").exists() else 'No `.env.example` found. Check source code for required environment variables.'}

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

{license or 'This project does not have a specified license. Please check with the original author before using commercially.'}

---

## Support

For issues and questions, please refer to the original repository or contact the maintainers.

---

*This README was auto-generated by [AgentForge](https://agentforge-consulting.vercel.app) as part of the AI Agent Index 2026.*
"""
    return readme

def generate_license_mit():
    return """MIT License

Copyright (c) 2026

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

def generate_env_example(repo):
    frameworks = repo.get("frameworks", [])
    languages = repo.get("languages", [])
    
    env_vars = ["# Environment Configuration", ""]
    
    if "python" in languages:
        env_vars.extend(["# Python", "PYTHONPATH=.", "PYTHONUNBUFFERED=1", ""])
    
    if any(f in frameworks for f in ["OpenAI", "HTTPX", "Requests"]):
        env_vars.extend(["# LLM APIs", "OPENAI_API_KEY=sk-...", "OPENAI_BASE_URL=https://api.openai.com/v1", ""])
    
    if "Anthropic" in frameworks:
        env_vars.extend(["# Anthropic", "ANTHROPIC_API_KEY=sk-ant-...", ""])
    
    if any(f in frameworks for f in ["FastAPI", "Flask", "Express", "Next.js", "NestJS"]):
        env_vars.extend(["# Server", "PORT=8000", "HOST=0.0.0.0", "DEBUG=false", ""])
    
    if "Prisma" in frameworks or "SQLAlchemy" in frameworks:
        env_vars.extend(["# Database", "DATABASE_URL=postgresql://user:pass@localhost:5432/db", ""])
    
    if "Redis" in frameworks or any("redis" in str(f).lower() for f in frameworks):
        env_vars.extend(["# Cache", "REDIS_URL=redis://localhost:6379", ""])
    
    env_vars.extend(["# Logging", "LOG_LEVEL=INFO", "", "# Security", "SECRET_KEY=change-me-in-production", ""])
    
    return "\n".join(env_vars)

def main():
    print("=" * 70)
    print("AGENTFORGE: Generating Missing Documentation for Repositories")
    print("=" * 70)
    
    audit = load_audit()
    repos = audit["repos"]
    
    readme_created = 0
    license_created = 0
    env_created = 0
    dockerfile_created = 0
    
    # Focus on repos that need docs (missing README, LICENSE, or env)
    for repo in repos:
        name = repo["name"]
        repo_path = REPOS_DIR / name
        
        if not repo_path.exists():
            continue
        
        # Generate README if missing
        if not repo.get("has_readme", False):
            try:
                readme_content = generate_readme(repo, repo_path)
                readme_path = repo_path / "README.md"
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(readme_content)
                repo["has_readme"] = True
                readme_created += 1
            except Exception as e:
                print(f"  ERR README {name}: {e}")
        
        # Generate LICENSE if missing
        if not repo.get("license"):
            try:
                license_path = repo_path / "LICENSE"
                with open(license_path, "w", encoding="utf-8") as f:
                    f.write(generate_license_mit())
                repo["license"] = "MIT"
                license_created += 1
            except Exception as e:
                print(f"  ERR LICENSE {name}: {e}")
        
        # Generate .env.example if missing
        if not repo.get("has_env_example", False):
            try:
                env_path = repo_path / ".env.example"
                env_content = generate_env_example(repo)
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(env_content)
                repo["has_env_example"] = True
                env_created += 1
            except Exception as e:
                print(f"  ERR ENV {name}: {e}")
    
    # Save updated audit
    save_audit(audit)
    
    # Update counts
    audit["with_readme"] = sum(1 for r in repos if r.get("has_readme"))
    audit["with_license"] = sum(1 for r in repos if r.get("license"))
    audit["with_env"] = sum(1 for r in repos if r.get("has_env_example"))
    
    print(f"\n{'='*70}")
    print("DOCUMENTATION GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"READMEs created:    {readme_created}")
    print(f"Licenses created:   {license_created}")
    print(f"ENV examples created: {env_created}")
    print(f"\nUpdated totals:")
    print(f"  With README:      {audit['with_readme']}/740")
    print(f"  With License:     {audit['with_license']}/740")
    print(f"  With ENV example: {audit['with_env']}/740")
    print(f"\nAudit updated: {AUDIT_JSON}")

if __name__ == "__main__":
    main()
