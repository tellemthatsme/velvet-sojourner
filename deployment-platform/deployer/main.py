"""
AgentForge Deployer API
FastAPI backend for browsing, searching, and deploying repos.
"""
import os
import json
import subprocess
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx

app = FastAPI(title="AgentForge Deployer", version="1.0.0")

REPOS_DIR = Path(os.getenv("REPOS_DIR", "/repos"))
DEPLOYMENTS_DIR = Path("/deployments")
DEPLOYMENTS_DIR.mkdir(exist_ok=True)

# In-memory index (in production, use postgres + redis)
repo_index: List[Dict[str, Any]] = []


class RepoInfo(BaseModel):
    name: str
    owner: Optional[str] = None
    size_mb: float
    file_count: int
    has_dockerfile: bool
    has_compose: bool
    has_readme: bool
    languages: List[str]
    description: Optional[str] = None
    category: str = "unknown"
    deployable: bool = False


class DeployRequest(BaseModel):
    repo_name: str
    env_vars: Optional[Dict[str, str]] = None
    port_mapping: Optional[Dict[str, int]] = None


class DeployStatus(BaseModel):
    repo_name: str
    status: str  # pending, running, failed, stopped
    url: Optional[str] = None
    logs: List[str] = []
    started_at: Optional[str] = None


def scan_repos():
    """Scan repos directory and build index."""
    global repo_index
    repo_index = []

    if not REPOS_DIR.exists():
        return

    for repo_path in REPOS_DIR.iterdir():
        if not repo_path.is_dir():
            continue

        name = repo_path.name
        files = list(repo_path.rglob("*"))
        file_count = sum(1 for f in files if f.is_file())
        total_size = sum(f.stat().st_size for f in files if f.is_file())

        # Detect owner from prefix
        owner = None
        for prefix in ["tellemthatsme_", "woodsai69rme_", "leahmfoots_", "acidlink_", "Ashlee69r_"]:
            if name.startswith(prefix):
                owner = prefix.rstrip("_")
                break

        # Detect languages
        languages = set()
        if (repo_path / "package.json").exists():
            languages.add("javascript")
        if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists():
            languages.add("python")
        if (repo_path / "Cargo.toml").exists():
            languages.add("rust")
        if (repo_path / "go.mod").exists():
            languages.add("go")
        if list(repo_path.rglob("*.ts")):
            languages.add("typescript")
        if list(repo_path.rglob("*.tsx")):
            languages.add("react")

        # Detect category
        category = "utility"
        name_lower = name.lower()
        if any(k in name_lower for k in ["agent", "ai-", "llm", "gpt", "claude", "bot"]):
            category = "ai-agent"
        elif any(k in name_lower for k in ["trade", "crypto", "stock", "forex", "nexus"]):
            category = "trading"
        elif any(k in name_lower for k in ["auto", "n8n", "workflow", "scrape", "crawl"]):
            category = "automation"
        elif any(k in name_lower for k in ["webui", "dashboard", "ui", "chat", "app"]):
            category = "web-app"
        elif any(k in name_lower for k in ["mcp", "server", "api", "gateway"]):
            category = "mcp-server"
        elif any(k in name_lower for k in ["dev", "tool", "cli", "sdk", "awesome-"]):
            category = "dev-tool"

        # Check deployability
        has_dockerfile = (repo_path / "Dockerfile").exists()
        has_compose = (repo_path / "docker-compose.yml").exists() or (repo_path / "docker-compose.yaml").exists()
        has_readme = (repo_path / "README.md").exists()

        # Get description from README
        description = None
        if has_readme:
            try:
                readme_text = (repo_path / "README.md").read_text(encoding="utf-8", errors="ignore")
                lines = [l.strip() for l in readme_text.split("\n") if l.strip()]
                if lines:
                    # Skip markdown headers
                    for line in lines[:5]:
                        if not line.startswith("#") and len(line) > 10:
                            description = line[:200]
                            break
            except Exception:
                pass

        repo_index.append({
            "name": name,
            "owner": owner,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "has_dockerfile": has_dockerfile,
            "has_compose": has_compose,
            "has_readme": has_readme,
            "languages": sorted(languages),
            "description": description,
            "category": category,
            "deployable": has_dockerfile or has_compose,
            "path": str(repo_path)
        })

    # Sort by size descending
    repo_index.sort(key=lambda x: x["size_mb"], reverse=True)


@app.on_event("startup")
async def startup():
    scan_repos()
    print(f"Indexed {len(repo_index)} repositories")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the web dashboard."""
    static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        return HTMLResponse(content=static_path.read_text())
    return HTMLResponse(content="<h1>AgentForge Deployer</h1><p>Dashboard not found.</p>")


@app.get("/api/repos")
async def list_repos(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    deployable_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List repositories with filtering."""
    results = repo_index

    if search:
        s = search.lower()
        results = [r for r in results if s in r["name"].lower() or (r["description"] and s in r["description"].lower())]

    if category:
        results = [r for r in results if r["category"] == category]

    if language:
        results = [r for r in results if language.lower() in [l.lower() for l in r["languages"]]]

    if deployable_only:
        results = [r for r in results if r["deployable"]]

    total = len(results)
    paginated = results[offset:offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "repos": paginated
    }


@app.get("/api/repos/{repo_name}")
async def get_repo(repo_name: str):
    """Get details for a specific repo."""
    for r in repo_index:
        if r["name"] == repo_name:
            return r
    raise HTTPException(status_code=404, detail="Repository not found")


@app.get("/api/categories")
async def get_categories():
    """Get category counts."""
    cats = {}
    for r in repo_index:
        c = r["category"]
        cats[c] = cats.get(c, 0) + 1
    return cats


@app.get("/api/stats")
async def get_stats():
    """Get overall collection stats."""
    total_size = sum(r["size_mb"] for r in repo_index)
    total_files = sum(r["file_count"] for r in repo_index)
    deployable = sum(1 for r in repo_index if r["deployable"])

    return {
        "total_repos": len(repo_index),
        "total_size_gb": round(total_size / 1024, 2),
        "total_files": total_files,
        "deployable_repos": deployable,
        "categories": await get_categories(),
        "top_repos": repo_index[:10]
    }


@app.post("/api/deploy/{repo_name}")
async def deploy_repo(repo_name: str, req: DeployRequest, background_tasks: BackgroundTasks):
    """Generate deployment config for a repo."""
    repo = None
    for r in repo_index:
        if r["name"] == repo_name:
            repo = r
            break

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not repo["deployable"]:
        raise HTTPException(status_code=400, detail="Repository has no Dockerfile or docker-compose.yml")

    # Generate deployment compose file
    deploy_id = f"{repo_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    deploy_dir = DEPLOYMENTS_DIR / deploy_id
    deploy_dir.mkdir(exist_ok=True)

    repo_path = Path(repo["path"])

    if (repo_path / "docker-compose.yml").exists():
        # Copy and modify existing compose
        compose_content = (repo_path / "docker-compose.yml").read_text()
    else:
        # Generate compose from Dockerfile
        compose_content = generate_compose(repo_name, repo_path, req)

    (deploy_dir / "docker-compose.yml").write_text(compose_content)

    # Generate .env file
    env_vars = req.env_vars or {}
    env_lines = [f"{k}={v}" for k, v in env_vars.items()]
    (deploy_dir / ".env").write_text("\n".join(env_lines))

    return {
        "deploy_id": deploy_id,
        "repo": repo_name,
        "status": "ready",
        "compose_file": str(deploy_dir / "docker-compose.yml"),
        "instructions": f"cd {deploy_dir} && docker-compose up -d"
    }


def generate_compose(repo_name: str, repo_path: Path, req: DeployRequest) -> str:
    """Generate a docker-compose.yml for a repo with just a Dockerfile."""
    service_name = repo_name.replace("_", "-").lower()[:30]
    port = 8080

    compose = {
        "version": "3.8",
        "services": {
            service_name: {
                "build": str(repo_path),
                "ports": [f"{port}:{port}"],
                "environment": req.env_vars or {},
                "networks": ["agentforge"],
                "labels": [
                    "traefik.enable=true",
                    f"traefik.http.routers.{service_name}.rule=Host(`{service_name}.localhost`)"
                ]
            }
        },
        "networks": {
            "agentforge": {
                "external": True
            }
        }
    }

    return yaml.dump(compose, default_flow_style=False)


@app.get("/api/deployments")
async def list_deployments():
    """List active deployments."""
    deployments = []
    if DEPLOYMENTS_DIR.exists():
        for d in DEPLOYMENTS_DIR.iterdir():
            if d.is_dir():
                compose_exists = (d / "docker-compose.yml").exists()
                deployments.append({
                    "id": d.name,
                    "compose_exists": compose_exists,
                    "path": str(d)
                })
    return deployments


@app.post("/api/scan")
async def rescan():
    """Rescan repos directory."""
    scan_repos()
    return {"message": f"Scanned {len(repo_index)} repositories"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
