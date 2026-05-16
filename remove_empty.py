"""Remove all repos with fewer than 5 files."""
import shutil
from pathlib import Path

REPOS_DIR = Path(r"C:\temp\velvet-sojourner\repos")
removed = 0

for p in REPOS_DIR.iterdir():
    if not p.is_dir():
        continue
    file_count = sum(1 for _ in p.rglob("*") if _.is_file())
    if file_count < 5:
        print(f"Removing {p.name} ({file_count} files)")
        shutil.rmtree(p, ignore_errors=True)
        removed += 1

print(f"\nRemoved {removed} empty repos")
print(f"Remaining repos: {sum(1 for p in REPOS_DIR.iterdir() if p.is_dir())}")
