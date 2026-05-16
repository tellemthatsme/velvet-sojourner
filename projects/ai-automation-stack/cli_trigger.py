#!/usr/bin/env python3
"""
CLI Trigger - HTTP-based Module Trigger
=========================================
Triggers modules via HTTP call to local dashboard or direct module execution.

Usage:
    python cli_trigger.py voice           # Launch voice assistant
    python cli_trigger.py sync-github     # Sync GitHub repos
    python cli_trigger.py export          # Run chat exporter
    python cli_trigger.py embed           # Run RAG embed pipeline
    python cli_trigger.py wiki            # Build markdown wiki
    python cli_trigger.py posts           # Generate social posts
    python cli_trigger.py status          # Check module status
    python cli_trigger.py stop all        # Stop all running modules

Dependencies:
    - requests library for HTTP calls
"""

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "localhost")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8080))
DASHBOARD_URL = f"http://{DASHBOARD_HOST}:{DASHBOARD_PORT}"

# Module configuration
MODULES = {
    "voice": {"file": "run_voice.py", "port": None},
    "sync-github": {"file": "sync.py", "port": None},
    "sync-drive": {"file": "sync_drive.sh", "port": None},
    "sync-vault": {"file": "sync_obsidian_vault.sh", "port": None},
    "export": {"file": "export_sorter.py", "port": None},
    "embed": {"file": "embed.py", "port": None},
    "wiki": {"file": "mdbook_build.sh", "port": None},
    "posts": {"file": "post_gen.py", "port": None},
    "scheduler": {"file": "send_posts.py", "port": None},
    "prompt-api": {"file": "prompt_api.py", "port": 5000},
    "search-api": {"file": "search_server.py", "port": 5001},
}

# Track running processes
running_processes: Dict[str, subprocess.Popen] = {}


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def find_process_using_port(port: int) -> Optional[int]:
    """Find process ID using a specific port."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            shell=True,
        )
        for line in result.stdout.split("\n"):
            if f":{port}" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = int(parts[-1])
                    if pid > 0:
                        return pid
    except Exception:
        pass
    return None


def start_module_direct(module_name: str) -> bool:
    """Start a module directly (bypassing HTTP)."""
    if module_name not in MODULES:
        print(f"❌ Unknown module: {module_name}")
        return False

    if module_name in running_processes:
        proc = running_processes[module_name]
        if proc.poll() is None:
            print(f"⚠️  Module {module_name} is already running")
            return True

    module_info = MODULES[module_name]
    module_file = BASE_DIR / module_info["file"]

    if not module_file.exists():
        print(f"❌ Module file not found: {module_file}")
        return False

    print(f"🚀 Starting {module_name}...")

    try:
        if module_file.suffix == ".sh":
            proc = subprocess.Popen(
                ["bash", str(module_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        else:
            cmd = [sys.executable, str(module_file)]
            if module_info["port"]:
                cmd.extend(["--port", str(module_info["port"])])
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

        running_processes[module_name] = proc
        print(f"✅ Started {module_name} (PID: {proc.pid})")
        return True
    except Exception as e:
        print(f"❌ Failed to start {module_name}: {e}")
        return False


def stop_module(module_name: str) -> bool:
    """Stop a running module."""
    if module_name == "all":
        return stop_all_modules()

    if module_name not in running_processes:
        print(f"⚠️  Module {module_name} is not running")
        return True

    proc = running_processes[module_name]
    if proc.poll() is not None:
        del running_processes[module_name]
        print(f"ℹ️  Module {module_name} was not running")
        return True

    try:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        del running_processes[module_name]
        print(f"✅ Stopped {module_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to stop {module_name}: {e}")
        return False


def stop_all_modules() -> bool:
    """Stop all running modules."""
    print("🛑 Stopping all modules...")
    success = True
    for module_name in list(running_processes.keys()):
        if not stop_module(module_name):
            success = False
    print("✅ All modules stopped")
    return success


def check_module_status(module_name: str) -> Dict:
    """Check status of a module."""
    status = {
        "name": module_name,
        "running": False,
        "pid": None,
        "port": None,
        "status": "not configured",
    }

    if module_name not in MODULES:
        status["status"] = "unknown module"
        return status

    module_info = MODULES[module_name]

    # Check if running in our process tracker
    if module_name in running_processes:
        proc = running_processes[module_name]
        if proc.poll() is None:
            status["running"] = True
            status["pid"] = proc.pid
            status["status"] = "running"
        else:
            del running_processes[module_name]

    # Check port if applicable
    if module_info["port"]:
        status["port"] = module_info["port"]
        if is_port_in_use(module_info["port"]):
            status["running"] = True
            if status["status"] == "not configured":
                status["status"] = "running on port"

    return status


def list_all_status() -> None:
    """List status of all modules."""
    print("\n📊 Module Status")
    print("=" * 60)

    for module_name, module_info in MODULES.items():
        status = check_module_status(module_name)
        indicator = "🟢" if status["running"] else "🔴"
        port_info = f":{status['port']}" if status["port"] else ""
        print(f"  {indicator} {module_name:<15} {status['status']}{port_info}")

    print("=" * 60)


def trigger_via_http(endpoint: str, data: Optional[Dict] = None) -> bool:
    """Trigger a module via HTTP call to dashboard."""
    url = f"{DASHBOARD_URL}/api/{endpoint}"

    try:
        response = requests.post(url, json=data or {}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Success')}")
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"⚠️  Cannot connect to dashboard at {DASHBOARD_URL}")
        print("   Falling back to direct execution...")
        return False
    except Exception as e:
        print(f"❌ HTTP Request failed: {e}")
        return False


def call_dashboard_api(action: str, module: Optional[str] = None) -> None:
    """Call dashboard API to trigger or control a module."""
    endpoints = {
        "start": f"modules/{module}/start" if module else "modules/start-all",
        "stop": f"modules/{module}/stop" if module else "modules/stop-all",
        "status": "modules/status",
        "logs": f"modules/{module}/logs" if module else "modules/logs",
    }

    if action not in endpoints:
        print(f"❌ Unknown action: {action}")
        return

    endpoint = endpoints[action]
    trigger_via_http(endpoint, {"module": module} if module else {})


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CLI Trigger - Control AI Automation modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_trigger.py voice              Start voice assistant
  python cli_trigger.py sync-github        Sync GitHub repositories
  python cli_trigger.py export --direct    Run export directly
  python cli_trigger.py status             Check all module statuses
  python cli_trigger.py stop voice         Stop voice assistant
  python cli_trigger.py stop all           Stop all modules
  python cli_trigger.py list               List all modules
        """,
    )

    parser.add_argument("module", nargs="?", help="Module to trigger")
    parser.add_argument(
        "--action",
        choices=["start", "stop", "status", "logs"],
        default="start",
        help="Action to perform (default: start)",
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Run module directly instead of via HTTP",
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Force HTTP call to dashboard (default: auto-fallback)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available modules and their status",
    )

    args = parser.parse_args()

    if args.list:
        list_all_status()
        return

    if not args.module:
        parser.print_help()
        return

    # Handle special commands
    if args.module == "stop" and args.action == "start":
        # User wants to stop something
        target = "all"
        if len(sys.argv) > 2:
            target = sys.argv[2]
        stop_module(target)
        return

    if args.module == "status":
        list_all_status()
        return

    if args.module not in MODULES:
        print(f"❌ Unknown module: {args.module}")
        print("\nAvailable modules:")
        for name in MODULES:
            print(f"  - {name}")
        return

    # Execute action
    if args.action == "start":
        if args.http:
            call_dashboard_api("start", args.module)
        elif not args.direct:
            # Try HTTP first, fall back to direct
            if not trigger_via_http(f"modules/{args.module}/start"):
                start_module_direct(args.module)
        else:
            start_module_direct(args.module)

    elif args.action == "stop":
        stop_module(args.module)

    elif args.action == "status":
        status = check_module_status(args.module)
        print(json.dumps(status, indent=2))

    elif args.action == "logs":
        # Show recent logs for module
        log_file = BASE_DIR / "logs" / f"{args.module}.log"
        if log_file.exists():
            with open(log_file, "r") as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    print(line, end="")
        else:
            print(f"⚠️  No logs found for {args.module}")


if __name__ == "__main__":
    main()
