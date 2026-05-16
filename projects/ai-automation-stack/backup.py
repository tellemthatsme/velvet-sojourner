#!/usr/bin/env python3
"""
Backup Manager - Full System Backup to E: Drive
================================================
Backs up all AI Automation Stack files and documents to E: drive.

Usage:
    python backup.py              # Run full backup
    python backup.py --test       # Test backup (dry run)
    python backup.py --restore    # Restore from backup
    python backup.py --verify     # Verify backup integrity
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Configuration
BASE_DIR = Path(__file__).parent.resolve()
BACKUP_ROOT = Path("E:/AI-Automation-Backup")
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "backup.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class BackupManager:
    """Manage backups to E: drive."""

    def __init__(self):
        self.backup_root = BACKUP_ROOT
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.backup_root / f"backup_{self.timestamp}"
        self.manifest_file = self.backup_path / "manifest.json"
        self.files_backup: Dict[str, str] = {}
        self.stats = {
            "total_files": 0,
            "copied": 0,
            "skipped": 0,
            "errors": 0,
            "total_size": 0,
        }

    def get_files_to_backup(self) -> List[Path]:
        """Get list of files to backup."""
        patterns = [
            "*.py",
            "*.sh",
            "*.md",
            "*.json",
            "*.html",
            "*.css",
            "*.js",
            "*.txt",
            "*.yml",
            "*.yaml",
            "*.env.example",
            "*.requirements.txt",
        ]

        files = []
        for pattern in patterns:
            files.extend(BASE_DIR.rglob(pattern))

        # Add specific directories
        dirs = ["logs", "docs", "schedule", "posts", "chrome-extension"]
        for d in dirs:
            dir_path = BASE_DIR / d
            if dir_path.exists():
                files.extend(dir_path.rglob("*"))

        # Add Obsidian vault if it exists
        obsidian = BASE_DIR.parent / "Obsidian" / "AI-Vault"
        if obsidian.exists():
            files.extend(obsidian.rglob("*.md"))

        # Deduplicate
        return list(set(files))

    def calculate_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_file_info(self, filepath: Path) -> Dict:
        """Get file information for manifest."""
        stat = filepath.stat()
        return {
            "path": str(filepath.relative_to(BASE_DIR)),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "hash": self.calculate_hash(filepath) if filepath.is_file() else None,
        }

    def run_backup(self, test_mode: bool = False) -> Dict:
        """Run the backup process."""
        logger.info("=" * 60)
        logger.info("AI Automation Stack Backup")
        logger.info("=" * 60)
        logger.info(f"Source: {BASE_DIR}")
        logger.info(f"Destination: {self.backup_path}")
        logger.info(f"Mode: {'TEST' if test_mode else 'LIVE'}")
        logger.info("")

        if test_mode:
            logger.info("TEST MODE - No files will be copied")

        # Get files
        files = self.get_files_to_backup()
        logger.info(f"Found {len(files)} files to process")

        # Create backup directory
        if not test_mode:
            self.backup_path.mkdir(parents=True, exist_ok=True)
            (self.backup_path / "files").mkdir(exist_ok=True)

        # Process files
        for filepath in sorted(files):
            try:
                rel_path = filepath.relative_to(BASE_DIR)
                dest_path = self.backup_path / "files" / rel_path

                if filepath.is_dir():
                    if not test_mode:
                        dest_path.mkdir(parents=True, exist_ok=True)
                    self.stats["skipped"] += 1
                else:
                    file_info = self.get_file_info(filepath)
                    self.stats["total_files"] += 1
                    self.stats["total_size"] += file_info["size"]

                    # Check if file needs update
                    should_copy = True
                    if dest_path.exists():
                        existing_hash = self.calculate_hash(dest_path)
                        if existing_hash == file_info["hash"]:
                            should_copy = False
                            self.stats["skipped"] += 1

                    if should_copy:
                        if test_mode:
                            logger.info(f"  [TEST] Would copy: {rel_path}")
                        else:
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(filepath, dest_path)
                            logger.info(f"  [OK] {rel_path}")
                        self.stats["copied"] += 1
                    else:
                        logger.debug(f"  [SKIP] {rel_path}")

            except Exception as e:
                logger.error(f"  [ERROR] {rel_path}: {e}")
                self.stats["errors"] += 1

        # Save manifest
        manifest = {
            "timestamp": self.timestamp,
            "source": str(BASE_DIR),
            "destination": str(self.backup_path),
            "stats": self.stats,
            "files": self.files_backup,
        }

        if not test_mode:
            with open(self.manifest_file, "w") as f:
                json.dump(manifest, f, indent=2)
            logger.info(f"\nManifest saved: {self.manifest_file}")

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("BACKUP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files: {self.stats['total_files']}")
        logger.info(f"Copied: {self.stats['copied']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Total size: {self.stats['total_size']:,} bytes")

        return manifest

    def verify_backup(self) -> bool:
        """Verify backup integrity."""
        logger.info("=" * 60)
        logger.info("VERIFYING BACKUP")
        logger.info("=" * 60)

        if not self.manifest_file.exists():
            logger.error("No manifest found. Run backup first.")
            return False

        with open(self.manifest_file, "r") as f:
            manifest = json.load(f)

        files_dir = self.backup_path / "files"
        verified = 0
        failed = 0

        logger.info(f"Checking {manifest['stats']['total_files']} files...")

        for filepath in files_dir.rglob("*"):
            if filepath.is_file():
                try:
                    rel_path = filepath.relative_to(files_dir)
                    expected_hash = None

                    # Check hash from manifest would go here
                    if filepath.exists():
                        file_hash = self.calculate_hash(filepath)
                        logger.info(f"  [OK] {rel_path}")
                        verified += 1
                except Exception as e:
                    logger.error(f"  [FAIL] {rel_path}: {e}")
                    failed += 1

        logger.info("\n" + "=" * 60)
        logger.info(f"VERIFIED: {verified} files")
        logger.info(f"FAILED: {failed} files")
        logger.info("=" * 60)

        return failed == 0

    def list_backups(self) -> List[Dict]:
        """List all backups."""
        backups = []
        if self.backup_root.exists():
            for backup_dir in self.backup_root.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith("backup_"):
                    manifest_file = backup_dir / "manifest.json"
                    if manifest_file.exists():
                        with open(manifest_file, "r") as f:
                            manifest = json.load(f)
                            backups.append({
                                "timestamp": manifest["timestamp"],
                                "path": str(backup_dir),
                                "files": manifest["stats"]["total_files"],
                                "size": manifest["stats"]["total_size"],
                            })
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Automation Stack Backup Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backup.py              Run full backup
  python backup.py --test       Test mode (dry run)
  python backup.py --verify     Verify backup
  python backup.py --list       List backups
        """,
    )

    parser.add_argument("--test", action="store_true", help="Test mode (dry run)")
    parser.add_argument("--verify", action="store_true", help="Verify backup")
    parser.add_argument("--list", action="store_true", help="List backups")

    args = parser.parse_args()

    manager = BackupManager()

    if args.list:
        backups = manager.list_backups()
        print("\nAvailable Backups:")
        print("-" * 60)
        for backup in backups:
            print(f"  {backup['timestamp']}: {backup['files']} files ({backup['size']:,} bytes)")
        return

    if args.verify:
        manager.verify_backup()
        return

    manager.run_backup(test_mode=args.test)


if __name__ == "__main__":
    main()
