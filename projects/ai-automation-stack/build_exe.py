#!/usr/bin/env python3
"""
Build EXE - Create Windows Executables
=======================================
Build standalone Windows executables for AI Automation Stack.

Usage:
    python build_exe.py              # Build all executables
    python build_exe.py --single launch.py  # Build single script
    python build_exe.py --clean     # Clean build artifacts

Prerequisites:
    pip install pyinstaller
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# Configuration
BASE_DIR = Path(__file__).parent.resolve()
BUILD_DIR = BASE_DIR / "build"
DIST_DIR = BASE_DIR / "dist"
SPEC_DIR = BASE_DIR / "specs"

# Scripts to build
SCRIPTS = {
    "launch": {
        "file": "launch.py",
        "name": "AI-Launcher",
        "icon": None,
        "hidden": [],
    },
    "cli_trigger": {
        "file": "cli_trigger.py",
        "name": "AI-CLI-Trigger",
        "icon": None,
        "hidden": [],
    },
    "backup": {
        "file": "backup.py",
        "name": "AI-Backup",
        "icon": None,
        "hidden": [],
    },
    "export_sorter": {
        "file": "export_sorter.py",
        "name": "AI-Export-Sorter",
        "icon": None,
        "hidden": [],
    },
    "post_gen": {
        "file": "post_gen.py",
        "name": "AI-Post-Generator",
        "icon": None,
        "hidden": [],
    },
    "prompt_api": {
        "file": "prompt_api.py",
        "name": "AI-Prompt-API",
        "icon": None,
        "hidden": [],
    },
    "search_server": {
        "file": "search_server.py",
        "name": "AI-Search-Server",
        "icon": None,
        "hidden": [],
    },
    "embed": {
        "file": "embed.py",
        "name": "AI-RAG-Embedder",
        "icon": None,
        "hidden": [],
    },
    "sync": {
        "file": "sync.py",
        "name": "AI-GitHub-Sync",
        "icon": None,
        "hidden": [],
    },
}

# Common hidden imports
COMMON_HIDDEN = [
    "flask",
    "flask_cors",
    "requests",
    "dotenv",
    "openai",
    "langchain",
    "langchain_openai",
    "faiss",
    "pypdf",
    "beautifulsoup4",
    "yaml",
]


def clean_build():
    """Clean build directories."""
    print("Cleaning build directories...")
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_path}")
    print("Done.\n")


def build_single(script_key: str, onefile: bool = True) -> bool:
    """Build a single executable."""
    if script_key not in SCRIPTS:
        print(f"Unknown script: {script_key}")
        return False

    script_info = SCRIPTS[script_key]
    script_file = BASE_DIR / script_info["file"]
    script_name = script_info["name"]

    if not script_file.exists():
        print(f"Script not found: {script_file}")
        return False

    print(f"Building {script_name}...")
    print(f"  Source: {script_file}")

    # Build command
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile" if onefile else "--onedir",
        "--name", script_name,
        "--clean",
        "--noconfirm",
    ]

    # Add hidden imports
    for imp in COMMON_HIDDEN:
        cmd.extend(["--hidden-import", imp])

    # Add data files
    cmd.extend(["--add-data", f"{BASE_DIR / 'commands.json'};."])
    cmd.extend(["--add-data", f"{BASE_DIR / 'schedule.json'};."])

    # Icon
    if script_info.get("icon"):
        cmd.extend(["--icon", script_info["icon"]])

    # Add script
    cmd.append(str(script_file))

    # Run
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, check=True)
        print(f"  SUCCESS: {script_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  FAILED: {e}")
        return False


def build_all():
    """Build all executables."""
    print("=" * 60)
    print("AI Automation Stack - Build EXE")
    print("=" * 60)
    print()

    # Clean first
    clean_build()

    # Create dist directory
    DIST_DIR.mkdir(exist_ok=True)

    # Build each script
    success = 0
    failed = 0

    for key in SCRIPTS:
        if build_single(key):
            success += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"BUILD COMPLETE")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Output: {DIST_DIR}")
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Windows EXE for AI Automation Stack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_exe.py              Build all executables
  python build_exe.py --single launch.py  Build single script
  python build_exe.py --clean     Clean build artifacts
        """,
    )

    parser.add_argument(
        "--single",
        metavar="SCRIPT",
        help="Build single script (filename without .py)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories",
    )
    parser.add_argument(
        "--dir",
        action="store_true",
        help="Build directory mode (not onefile)",
    )

    args = parser.parse_args()

    if args.clean:
        clean_build()
        return

    if args.single:
        build_single(args.single, onefile=not args.dir)
        return

    build_all()


if __name__ == "__main__":
    main()
