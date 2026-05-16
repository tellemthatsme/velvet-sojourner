#!/usr/bin/env python3
"""
AgentForge CLI - Command line tool for deploying AI agents.
Usage:
    forge list [--category CATEGORY] [--search QUERY] [--deployable]
    forge deploy <repo_name> [--env KEY=VALUE]...
    forge status
    forge logs <deploy_id>
    forge scan
"""
import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
import httpx

API_BASE = os.getenv("AGENTFORGE_API", "http://localhost:8000")
REPOS_DIR = Path(os.getenv("REPOS_DIR", r"C:\temp\velvet-sojourner\repos"))


def api_get(endpoint):
    try:
        r = httpx.get(f"{API_BASE}{endpoint}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None


def api_post(endpoint, data=None):
    try:
        r = httpx.post(f"{API_BASE}{endpoint}", json=data or {}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None


def cmd_list(args):
    params = []
    if args.category:
        params.append(f"category={args.category}")
    if args.search:
        params.append(f"search={args.search}")
    if args.deployable:
        params.append("deployable_only=true")
    params.append("limit=100")

    url = "/api/repos" + ("?" + "&".join(params) if params else "")
    data = api_get(url)
    if not data:
        return

    repos = data.get("repos", [])
    if not repos:
        print("No repositories found.")
        return

    print(f"\n{'NAME':<45} {'CATEGORY':<14} {'SIZE':>8} {'FILES':>7} {'DOCKER':>6} {'LANGUAGES'}")
    print("-" * 110)
    for r in repos:
        docker = "YES" if r.get("deployable") else "no"
        langs = ", ".join(r.get("languages", [])[:3])
        print(f"{r['name']:<45} {r['category']:<14} {r['size_mb']:>7.1f}M {r['file_count']:>7} {docker:>6} {langs}")
    print(f"\nShowing {len(repos)} of {data.get('total', 0)} repositories")


def cmd_deploy(args):
    repo = args.repo_name
    print(f"Deploying {repo}...")

    env_vars = {}
    if args.env:
        for pair in args.env:
            if "=" in pair:
                k, v = pair.split("=", 1)
                env_vars[k] = v

    data = api_post(f"/api/deploy/{repo}", {"env_vars": env_vars})
    if not data:
        return

    print(f"\nDeployment created!")
    print(f"  ID:     {data.get('deploy_id')}")
    print(f"  Repo:   {data.get('repo')}")
    print(f"  Status: {data.get('status')}")
    print(f"  Path:   {data.get('compose_file')}")
    print(f"\nTo start:")
    print(f"  cd {os.path.dirname(data.get('compose_file', '.'))}")
    print(f"  docker-compose up -d")


def cmd_status(args):
    data = api_get("/api/stats")
    if not data:
        return

    print("\n=== AGENTFORGE STATUS ===")
    print(f"Total Repositories: {data.get('total_repos', 0)}")
    print(f"Total Size:         {data.get('total_size_gb', 0):.2f} GB")
    print(f"Total Files:        {data.get('total_files', 0):,}")
    print(f"Deployable:         {data.get('deployable_repos', 0)}")
    print("\nCategories:")
    for cat, count in (data.get("categories") or {}).items():
        print(f"  {cat:<20} {count:>5}")


def cmd_logs(args):
    print("Logs feature requires deployment tracking database.")
    print("View logs with: docker logs <container_name>")


def cmd_scan(args):
    print("Scanning repositories...")
    data = api_post("/api/scan")
    if data:
        print(data.get("message", "Scan complete"))


def main():
    parser = argparse.ArgumentParser(prog="forge", description="AgentForge CLI")
    subparsers = parser.add_subparsers(dest="command")

    # list
    p_list = subparsers.add_parser("list", help="List repositories")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--search", help="Search query")
    p_list.add_argument("--deployable", action="store_true", help="Only deployable repos")

    # deploy
    p_deploy = subparsers.add_parser("deploy", help="Deploy a repository")
    p_deploy.add_argument("repo_name", help="Repository name")
    p_deploy.add_argument("--env", action="append", help="Environment variable (KEY=VALUE)")

    # status
    subparsers.add_parser("status", help="Show platform status")

    # logs
    p_logs = subparsers.add_parser("logs", help="View deployment logs")
    p_logs.add_argument("deploy_id", help="Deployment ID")

    # scan
    subparsers.add_parser("scan", help="Rescan repositories")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "deploy":
        cmd_deploy(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "logs":
        cmd_logs(args)
    elif args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
