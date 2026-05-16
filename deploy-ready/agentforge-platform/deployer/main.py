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
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx


REPOS_DIR = Path(os.getenv("REPOS_DIR", "/repos"))
DEPLOYMENTS_DIR = Path("/deployments")
DEPLOYMENTS_DIR.mkdir(exist_ok=True)

repo_index: List[Dict[str, Any]] = []
_scan_done = False


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
    status: str
    url: Optional[str] = None
    logs: List[str] = []
    started_at: Optional[str] = None


OWNER_PREFIXES = ["tellemthatsme_", "woodsai69rme_", "leahmfoots_", "acidlink_", "Ashlee69r_"]


def scan_repos():
    """Scan repos directory and build index efficiently (top-level only, no deep rglob)."""
    global repo_index
    repo_index = []

    if not REPOS_DIR.exists():
        print("REPOS_DIR does not exist: %s" % REPOS_DIR)
        return

    entries = sorted(os.listdir(str(REPOS_DIR)))
    for name in entries:
        repo_path = REPOS_DIR / name
        if not repo_path.is_dir():
            continue

        try:
            file_count = 0
            total_size = 0
            has_dockerfile = (repo_path / "Dockerfile").exists()
            has_compose = (repo_path / "docker-compose.yml").exists() or (repo_path / "docker-compose.yaml").exists()
            has_readme = (repo_path / "README.md").exists()

            # Quick file counting using scandir (no deep rglob)
            dirs_to_check = [repo_path]
            while dirs_to_check:
                current = dirs_to_check.pop()
                try:
                    with os.scandir(str(current)) as it:
                        for entry in it:
                            if entry.is_file():
                                file_count += 1
                                try:
                                    total_size += entry.stat().st_size
                                except OSError:
                                    pass
                            elif entry.is_dir():
                                dn = entry.name
                                if dn not in (".git", "__pycache__", "node_modules", ".venv", "venv", ".next", "build", "dist", ".git"):
                                    dirs_to_check.append(Path(entry.path))
                except PermissionError:
                    pass
        except Exception:
            continue

        owner = None
        for prefix in OWNER_PREFIXES:
            if name.startswith(prefix):
                owner = prefix.rstrip("_")
                break

        languages = set()
        if (repo_path / "package.json").exists():
            languages.add("javascript")
        if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists():
            languages.add("python")
        if (repo_path / "Cargo.toml").exists():
            languages.add("rust")
        if (repo_path / "go.mod").exists():
            languages.add("go")

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
        elif any(k in name_lower for k in ["dev", "tool", "cli", "sdk"]):
            category = "dev-tool"

        description = None
        if has_readme:
            try:
                readme_text = (repo_path / "README.md").read_text(encoding="utf-8", errors="ignore")
                lines = [l.strip() for l in readme_text.split("\n") if l.strip()]
                if lines:
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

    repo_index.sort(key=lambda x: x["size_mb"], reverse=True)


async def scan_repos_background():
    """Run scan in thread pool to avoid blocking startup."""
    global _scan_done, repo_index
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, scan_repos)
    _scan_done = True
    print("Indexed %d repositories" % len(repo_index))


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(scan_repos_background())
    yield


app = FastAPI(title="AgentForge Deployer", version="1.0.0", lifespan=lifespan)


def _wait_for_scan():
    """If scan not done within 5 seconds, return empty index."""
    import time
    deadline = time.time() + 5
    while time.time() < deadline:
        if _scan_done:
            return True
        time.sleep(0.1)
    return False


@app.get("/", response_class=HTMLResponse)
async def dashboard():
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
    if not _scan_done:
        ready = _wait_for_scan()
        if not ready:
            return {"total": 0, "offset": offset, "limit": limit, "repos": [], "scanning": True}
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
    return {"total": total, "offset": offset, "limit": limit, "repos": paginated, "scanning": False}


@app.get("/api/repos/{repo_name}")
async def get_repo(repo_name: str):
    for r in repo_index:
        if r["name"] == repo_name:
            return r
    raise HTTPException(status_code=404, detail="Repository not found")


@app.get("/api/categories")
async def get_categories():
    cats = {}
    for r in repo_index:
        c = r["category"]
        cats[c] = cats.get(c, 0) + 1
    return cats


@app.get("/api/stats")
async def get_stats():
    if not _scan_done:
        ready = _wait_for_scan()
        if not ready:
            return {"total_repos": 0, "scanning": True}
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
    repo = None
    for r in repo_index:
        if r["name"] == repo_name:
            repo = r
            break
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if not repo["deployable"]:
        raise HTTPException(status_code=400, detail="Repository has no Dockerfile or docker-compose.yml")
    deploy_id = "%s-%s" % (repo_name, datetime.now().strftime('%Y%m%d%H%M%S'))
    deploy_dir = DEPLOYMENTS_DIR / deploy_id
    deploy_dir.mkdir(exist_ok=True)
    repo_path = Path(repo["path"])
    if (repo_path / "docker-compose.yml").exists():
        compose_content = (repo_path / "docker-compose.yml").read_text()
    else:
        compose_content = generate_compose(repo_name, repo_path, req)
    (deploy_dir / "docker-compose.yml").write_text(compose_content)
    env_vars = req.env_vars or {}
    env_lines = ["%s=%s" % (k, v) for k, v in env_vars.items()]
    (deploy_dir / ".env").write_text("\n".join(env_lines))
    return {
        "deploy_id": deploy_id,
        "repo": repo_name,
        "status": "ready",
        "compose_file": str(deploy_dir / "docker-compose.yml"),
        "instructions": "cd %s && docker-compose up -d" % deploy_dir
    }


def generate_compose(repo_name: str, repo_path: Path, req: DeployRequest) -> str:
    service_name = repo_name.replace("_", "-").lower()[:30]
    compose = {
        "services": {
            service_name: {
                "build": str(repo_path),
                "ports": ["8080:8080"],
                "environment": req.env_vars or {},
                "networks": ["agentforge"],
                "labels": [
                    "traefik.enable=true",
                    "traefik.http.routers.%s.rule=Host(`%s.localhost`)" % (service_name, service_name)
                ]
            }
        },
        "networks": {
            "agentforge": {"external": True}
        }
    }
    return yaml.dump(compose, default_flow_style=False)


@app.get("/api/deployments")
async def list_deployments():
    deployments = []
    if DEPLOYMENTS_DIR.exists():
        for d in DEPLOYMENTS_DIR.iterdir():
            if d.is_dir():
                deployments.append({
                    "id": d.name,
                    "compose_exists": (d / "docker-compose.yml").exists(),
                    "path": str(d)
                })
    return deployments


@app.post("/api/scan")
async def rescan():
    await scan_repos_background()
    return {"message": "Rescan started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
