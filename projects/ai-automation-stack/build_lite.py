#!/usr/bin/env python3
"""
Build Lite EXE - Create Windows Executables (Optimized)
========================================================
Build standalone Windows executables for AI Automation Stack.
This version excludes heavy dependencies for faster builds.

Usage:
    python build_lite.py              # Build all executables
    python build_lite.py --single launch  # Build single module
    python build_lite.py --clean     # Clean build artifacts
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

# Scripts to build (only core modules)
SCRIPTS = {
    "launch": {
        "file": "launch.py",
        "name": "AI-Launcher",
        "hidden": ["flask", "flask_cors", "requests", "dotenv"],
    },
    "cli_trigger": {
        "file": "cli_trigger.py",
        "name": "AI-CLI-Trigger",
        "hidden": ["requests"],
    },
    "export_sorter": {
        "file": "export_sorter.py",
        "name": "AI-Export-Sorter",
        "hidden": ["requests", "dotenv", "yaml"],
    },
    "post_gen": {
        "file": "post_gen.py",
        "name": "AI-Post-Generator",
        "hidden": ["requests", "openai", "dotenv"],
    },
    "prompt_api": {
        "file": "prompt_api.py",
        "name": "AI-Prompt-API",
        "hidden": ["flask", "flask_cors", "dotenv"],
    },
    "search_server": {
        "file": "search_server.py",
        "name": "AI-Search-Server",
        "hidden": ["flask", "flask_cors", "dotenv"],
    },
    "sync": {
        "file": "sync.py",
        "name": "AI-GitHub-Sync",
        "hidden": ["requests", "dotenv"],
    },
}

# Excludes to speed up build (only third-party heavy packages)
EXCLUDES = [
    "torch",
    "tensorflow",
    "keras",
    "scipy",
    "numpy.f2py",
    "pandas",
    "matplotlib",
    "PIL",
    "cv2",
    "sklearn",
    "pytest",
    "black",
    "pylint",
    "jupyter",
    "IPython",
    "notebook",
    "sphinx",
    "transformers",
    "langchain",
    "langchain_openai",
    "openai",
    "whisper",
    "librosa",
    "soundfile",
    "yt_dlp",
    "imageio",
    "numba",
    "llvmlite",
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
        "--log-level", "WARN",
    ]

    # Add excludes
    for exc in EXCLUDES:
        cmd.extend(["--exclude-module", exc])

    # Add hidden imports
    for imp in script_info.get("hidden", []):
        cmd.extend(["--hidden-import", imp])

    # Add data files if they exist
    commands_json = BASE_DIR / "commands.json"
    schedule_json = BASE_DIR / "schedule.json"
    
    if commands_json.exists():
        cmd.extend(["--add-data", f"{commands_json};."])
    if schedule_json.exists():
        cmd.extend(["--add-data", f"{schedule_json};."])

    # Add script
    cmd.append(str(script_file))

    # Run
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, check=True, capture_output=True, text=True)
        exe_path = DIST_DIR / f"{script_name}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"  SUCCESS: {script_name}.exe ({size_mb:.1f} MB)")
            return True
        else:
            print(f"  FAILED: EXE not created")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  FAILED: {e}")
        if e.stdout:
            print(f"  STDOUT: {e.stdout[:500]}")
        if e.stderr:
            print(f"  STDERR: {e.stderr[:500]}")
        return False


def build_all():
    """Build all executables."""
    print("=" * 60)
    print("AI Automation Stack - Lite Build")
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
    
    # List built files
    if success > 0:
        print("\nBuilt executables:")
        for f in DIST_DIR.glob("*.exe"):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  - {f.name} ({size_mb:.1f} MB)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Windows EXE for AI Automation Stack (Lite)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_lite.py              Build all executables
  python build_lite.py --single launch  Build single module
  python build_lite.py --clean     Clean build artifacts
        """,
    )

    parser.add_argument(
        "--single",
        metavar="MODULE",
        help="Build single module (launch, cli_trigger, etc.)",
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
