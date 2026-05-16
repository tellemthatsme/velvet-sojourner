"""Remove empty repos with Windows permission fix."""
import os
import stat
import shutil
from pathlib import Path

REPOS_DIR = Path(r"C:\temp\velvet-sojourner\repos")

def onerror(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

removed = 0
for p in sorted(REPOS_DIR.iterdir()):
    if not p.is_dir():
        continue
    file_count = sum(1 for _ in p.rglob("*") if _.is_file())
    if file_count < 5:
        print(f"Removing: {p.name} ({file_count} files)")
        try:
            shutil.rmtree(p, onerror=onerror)
            removed += 1
        except Exception as e:
            print(f"  FAILED: {e}")

print(f"\nRemoved: {removed}")
print(f"Remaining: {sum(1 for p in REPOS_DIR.iterdir() if p.is_dir())}")
