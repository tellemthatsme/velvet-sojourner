#!/usr/bin/env python3
"""
AI Automation Stack - Master Launcher
======================================
Central CLI to launch any component by flag or interactive menu.

Usage:
    python launch.py --voice              # Launch voice assistant
    python launch.py --sync-github        # Sync GitHub repos
    python launch.py --sync-drive         # Sync to Google Drive
    python launch.py --export             # Export and sort chats
    python launch.py --embed              # Run RAG embed pipeline
    python launch.py --wiki               # Build markdown wiki
    python launch.py --posts              # Generate social posts
    python launch.py --dashboard          # Launch web dashboard
    python launch.py --prompt-api         # Start prompt API server
    python launch.py --search-api         # Start search API server
    python launch.py --all                # Launch all modules
    python launch.py --interactive        # Interactive menu mode

Dependencies:
    - Python 3.8+
    - See requirements.txt for all dependencies
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# Configure logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "launcher.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Base directory configuration
BASE_DIR = Path(__file__).parent.resolve()
PROJECTS_DIR = BASE_DIR / "projects"
OBSIDIAN_DIR = Path(__file__).parent.parent.parent / "Obsidian" / "AI-Vault"
EXPORTS_DIR = BASE_DIR / "exports"
SCHEDULE_DIR = BASE_DIR / "schedule"
POSTS_DIR = BASE_DIR / "posts"


class ModuleLauncher:
    """Launcher for all AI Automation modules."""

    def __init__(self):
        self.base_dir = BASE_DIR
        self.modules = {
            "voice": {"file": "run_voice.py", "name": "Voice Assistant", "port": None},
            "sync_github": {"file": "sync.py", "name": "GitHub Sync", "port": None},
            "sync_drive": {"file": "sync_drive.sh", "name": "Drive Sync", "port": None, "shell": True},
            "sync_vault": {"file": "sync_obsidian_vault.sh", "name": "Vault Sync", "port": None, "shell": True},
            "export": {"file": "export_sorter.py", "name": "Chat Exporter", "port": None},
            "embed": {"file": "embed.py", "name": "RAG Embedder", "port": None},
            "wiki": {"file": "mdbook_build.sh", "name": "Wiki Builder", "port": None, "shell": True},
            "posts": {"file": "post_gen.py", "name": "Post Generator", "port": None},
            "scheduler": {"file": "send_posts.py", "name": "Post Scheduler", "port": None},
            "prompt_api": {"file": "prompt_api.py", "name": "Prompt API", "port": 5000},
            "search_api": {"file": "search_server.py", "name": "Search API", "port": 5001},
            "dashboard": {"file": "index.html", "name": "Dashboard", "port": None, "browser": True},
        }

    def run_module(self, module_name: str, background: bool = False) -> Optional[subprocess.Popen]:
        """Run a specific module."""
        if module_name not in self.modules:
            logger.error(f"Unknown module: {module_name}")
            return None

        module_info = self.modules[module_name]
        module_file = self.base_dir / module_info["file"]
        module_path = str(module_file)

        if not module_file.exists():
            logger.error(f"Module file not found: {module_path}")
            return None

        logger.info(f"Launching {module_info['name']}...")

        # Handle browser-based modules
        if module_info.get("browser"):
            import webbrowser
            webbrowser.open(f"file://{module_path}")
            logger.info(f"Opened {module_info['name']} in browser")
            return None

        # Handle shell scripts
        if module_info.get("shell"):
            try:
                if background:
                    proc = subprocess.Popen(
                        ["bash", module_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                    )
                    return proc
                else:
                    result = subprocess.run(
                        ["bash", module_path],
                        capture_output=True,
                        text=True,
                        cwd=self.base_dir,
                    )
                    logger.info(f"Module output: {result.stdout}")
                    if result.returncode != 0:
                        logger.error(f"Module error: {result.stderr}")
                    return None
            except Exception as e:
                logger.error(f"Failed to run shell module: {e}")
                return None

        # Handle Python modules
        cmd = [sys.executable, module_path]
        if module_info.get("port"):
            cmd.extend(["--port", str(module_info["port"])])

        try:
            if background:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                logger.info(f"Started {module_info['name']} (PID: {proc.pid})")
                return proc
            else:
                result = subprocess.run(cmd, cwd=self.base_dir)
                return None
        except Exception as e:
            logger.error(f"Failed to run module: {e}")
            return None

    def run_all(self) -> None:
        """Launch all main modules."""
        logger.info("Starting all AI Automation modules...")

        processes = []

        # Start API servers first
        processes.append(self.run_module("prompt_api", background=True))
        time.sleep(2)
        processes.append(self.run_module("search_api", background=True))
        time.sleep(2)

        # Start voice assistant
        processes.append(self.run_module("voice", background=True))

        # Start scheduler
        processes.append(self.run_module("scheduler", background=True))

        logger.info("All modules started. Use Ctrl+C to stop all.")
        logger.info("Dashboard available at: file://%s", self.base_dir / "index.html")

        try:
            for proc in processes:
                if proc:
                    proc.wait()
        except KeyboardInterrupt:
            logger.info("Shutting down all modules...")
            for proc in processes:
                if proc:
                    proc.terminate()
            logger.info("All modules stopped.")

    def interactive_menu(self) -> None:
        """Show interactive menu for module selection."""
        print("\n" + "=" * 60)
        print("🤖 AI AUTOMATION STACK - LAUNCHER MENU")
        print("=" * 60)
        print("\nAvailable Modules:")
        print("-" * 40)

        modules_list = list(self.modules.keys())
        for i, name in enumerate(modules_list, 1):
            info = self.modules[name]
            status = "🟢" if info.get("running") else "⚪"
            print(f"  {i}. {status} {info['name']:<20} ({name})")

        print("\n  0. Exit")
        print("  a. Run All Modules")
        print("  s. Sync Everything (GitHub + Drive + Vault)")
        print("  d. Build Everything (Embed + Wiki + Posts)")
        print("-" * 40)

        choice = input("\nEnter your choice: ").strip().lower()

        if choice == "0":
            print("Goodbye! 👋")
            sys.exit(0)
        elif choice == "a":
            self.run_all()
        elif choice == "s":
            self.run_module("sync_github")
            self.run_module("sync_drive")
            self.run_module("sync_vault")
        elif choice == "d":
            self.run_module("embed")
            self.run_module("wiki")
            self.run_module("posts")
        elif choice.isdigit() and 1 <= int(choice) <= len(modules_list):
            module_name = modules_list[int(choice) - 1]
            self.run_module(module_name)
        else:
            # Try direct module name
            if choice in self.modules:
                self.run_module(choice)
            else:
                print(f"Invalid choice: {choice}")


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    required = ["python3", "pip", "git"]
    optional = ["rclone", "ffmpeg", "mdbook"]

    print("\n🔍 Checking dependencies...")
    all_ok = True

    for dep in required:
        try:
            subprocess.run([dep, "--version"], capture_output=True, check=True)
            print(f"  ✅ {dep}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {dep} - REQUIRED")
            all_ok = False

    for dep in optional:
        try:
            subprocess.run([dep, "--version"], capture_output=True, check=True)
            print(f"  ✅ {dep}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ⚠️  {dep} - OPTIONAL")

    return all_ok


def check_environment() -> bool:
    """Check environment configuration."""
    print("\n🌍 Checking environment...")
    env_file = BASE_DIR / ".env"

    if not env_file.exists():
        print(f"  ⚠️  No .env file found at {env_file}")
        print("     Copy .env.example to .env and add your API keys")
        return False

    print(f"  ✅ Environment file found")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Automation Stack - Master Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py --voice              Launch voice assistant
  python launch.py --sync-github        Sync GitHub repositories
  python launch.py --export             Run chat exporter
  python launch.py --embed              Run RAG embedding pipeline
  python launch.py --all                Launch all modules
  python launch.py --interactive        Show interactive menu
        """,
    )

    parser.add_argument("--voice", action="store_true", help="Launch voice assistant")
    parser.add_argument("--sync-github", action="store_true", help="Sync GitHub repositories")
    parser.add_argument("--sync-drive", action="store_true", help="Sync to Google Drive")
    parser.add_argument("--sync-vault", action="store_true", help="Sync Obsidian vault")
    parser.add_argument("--export", action="store_true", help="Export and sort chats")
    parser.add_argument("--embed", action="store_true", help="Run RAG embed pipeline")
    parser.add_argument("--wiki", action="store_true", help="Build markdown wiki")
    parser.add_argument("--posts", action="store_true", help="Generate social posts")
    parser.add_argument("--dashboard", action="store_true", help="Launch web dashboard")
    parser.add_argument("--prompt-api", action="store_true", help="Start prompt API server")
    parser.add_argument("--search-api", action="store_true", help="Start search API server")
    parser.add_argument("--scheduler", action="store_true", help="Start post scheduler")
    parser.add_argument("--all", action="store_true", help="Launch all modules")
    parser.add_argument("--interactive", action="store_true", help="Interactive menu mode")
    parser.add_argument("--check", action="store_true", help="Check dependencies and environment")
    parser.add_argument("--sync-all", action="store_true", help="Run all sync operations")

    args = parser.parse_args()

    if args.check:
        check_dependencies()
        check_environment()
        return

    launcher = ModuleLauncher()

    if args.interactive:
        launcher.interactive_menu()
        return

    # Handle single module launches
    if args.all:
        launcher.run_all()
    elif args.sync_all:
        launcher.run_module("sync_github")
        launcher.run_module("sync_drive")
        launcher.run_module("sync_vault")
    elif args.voice:
        launcher.run_module("voice")
    elif args.sync_github:
        launcher.run_module("sync_github")
    elif args.sync_drive:
        launcher.run_module("sync_drive")
    elif args.sync_vault:
        launcher.run_module("sync_vault")
    elif args.export:
        launcher.run_module("export")
    elif args.embed:
        launcher.run_module("embed")
    elif args.wiki:
        launcher.run_module("wiki")
    elif args.posts:
        launcher.run_module("posts")
    elif args.dashboard:
        launcher.run_module("dashboard")
    elif args.prompt_api:
        launcher.run_module("prompt_api")
    elif args.search_api:
        launcher.run_module("search_api")
    elif args.scheduler:
        launcher.run_module("scheduler")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
