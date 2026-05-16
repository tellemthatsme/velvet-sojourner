"""
Aggressive dedup by base name - removes prefixed duplicates of the same repo.
"""
import shutil
from pathlib import Path
from collections import defaultdict

REPOS_DIR = Path(r"C:\temp\velvet-sojourner\repos")
DUP_DIR = Path(r"C:\temp\velvet-sojourner\repos_duplicates")
DUP_DIR.mkdir(exist_ok=True)

def get_base_name(name):
    for prefix in ["tellemthatsme_", "woodsai69rme_", "leahmfoots_", "acidlink_", "Ashlee69r_"]:
        if name.startswith(prefix):
            return name[len(prefix):]
    return name

# Group by base name
groups = defaultdict(list)
for p in REPOS_DIR.iterdir():
    if not p.is_dir():
        continue
    base = get_base_name(p.name)
    groups[base].append(p)

# Find groups with duplicates (same base name, different full names)
duplicates = []
keepers = []
for base, group in groups.items():
    if len(group) > 1:
        # Sort: prefer unprefixed, then most files, then shortest name
        def sort_key(p):
            file_count = sum(1 for _ in p.rglob("*") if _.is_file())
            is_prefixed = get_base_name(p.name) != p.name
            return (is_prefixed, -file_count, len(p.name), p.name)
        group.sort(key=sort_key)
        keepers.append(group[0])
        duplicates.extend(group[1:])
    else:
        keepers.append(group[0])

print(f"Groups with duplicates: {sum(1 for g in groups.values() if len(g) > 1)}")
print(f"Keepers: {len(keepers)}")
print(f"Duplicates to move: {len(duplicates)}")

if duplicates:
    print("\nDuplicate repos being moved:")
    for dup in duplicates:
        print(f"  -> {dup.name}")
        dst = DUP_DIR / dup.name
        if dst.exists():
            shutil.rmtree(dst, ignore_errors=True)
        try:
            shutil.move(str(dup), str(dst))
        except Exception as e:
            print(f"    ERROR: {e}")

    print(f"\nMoved {len(duplicates)} duplicate repos to {DUP_DIR}")
else:
    print("No duplicates found by base name.")

# Final count
final_count = sum(1 for p in REPOS_DIR.iterdir() if p.is_dir())
print(f"\nFinal repo count: {final_count}")
