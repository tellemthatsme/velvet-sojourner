import sys, os
sys.path.insert(0, r"C:\temp\velvet-sojourner\deployment-platform\deployer")
import main
main.REPOS_DIR = __import__('pathlib').Path(r"C:\temp\velvet-sojourner\repos")
main.scan_repos()
print("Indexed:", len(main.repo_index))
print("\nTop 10 repos by size:")
for r in main.repo_index[:10]:
    print(f"  {r['name']}: {r['size_mb']} MB, {r['file_count']} files, cat={r['category']}, deployable={r['deployable']}")
print("\nCategories:")
from collections import Counter
cats = Counter(r['category'] for r in main.repo_index)
for c, n in cats.most_common():
    print(f"  {c}: {n}")
print("\nDeployable repos:", sum(1 for r in main.repo_index if r['deployable']))
print("Total size GB:", round(sum(r['size_mb'] for r in main.repo_index) / 1024, 2))
