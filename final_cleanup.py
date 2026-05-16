"""Final force removal of all empty repos with error reporting."""
import shutil
from pathlib import Path

REPOS_DIR = Path(r"C:\temp\velvet-sojourner\repos")
removed = 0
failed = []

for p in sorted(REPOS_DIR.iterdir()):
    if not p.is_dir():
        continue
    files = list(p.rglob("*"))
    file_count = sum(1 for f in files if f.is_file())
    if file_count < 5:
        print(f"Removing: {p.name} ({file_count} files)")
        try:
            shutil.rmtree(p)
            removed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append((p.name, str(e)))

print(f"\nRemoved: {removed}")
if failed:
    print(f"Failed: {len(failed)}")
    for name, err in failed:
        print(f"  {name}: {err}")

remaining = sum(1 for p in REPOS_DIR.iterdir() if p.is_dir())
print(f"Remaining repos: {remaining}")
