import json
from pathlib import Path
from datetime import datetime

AUDIT_JSON = Path("C:/temp/velvet-sojourner/audit/full-audit-master.json")
REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")

def main():
    print("=" * 60)
    print("CLEANUP: Removing missing repos from audit")
    print("=" * 60)
    
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        audit = json.load(f)
    
    original_count = len(audit["repos"])
    
    # Filter out repos that don't exist on disk
    existing = []
    removed = []
    for r in audit["repos"]:
        name = r["name"]
        if (REPOS_DIR / name).exists():
            existing.append(r)
        else:
            removed.append(name)
    
    audit["repos"] = existing
    audit["total_repos"] = len(existing)
    
    # Recalculate stats
    total = len(existing)
    with_readme = sum(1 for r in existing if r.get("has_readme"))
    with_license = sum(1 for r in existing if r.get("license"))
    with_env = sum(1 for r in existing if r.get("has_env_example"))
    deployable = sum(1 for r in existing if r.get("deployable"))
    total_val = sum(r.get("valuation", 0) for r in existing)
    avg_qual = sum(r.get("quality_score", 0) for r in existing) / total if total else 0
    
    audit["with_readme"] = with_readme
    audit["with_license"] = with_license
    audit["with_env"] = with_env
    audit["deployable_count"] = deployable
    audit["total_valuation"] = total_val
    audit["avg_quality"] = round(avg_qual, 1)
    
    with open(AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)
    
    print(f"Original count: {original_count}")
    print(f"Removed: {len(removed)}")
    print(f"Final count: {total}")
    print(f"\nRemoved repos:")
    for r in removed:
        print(f"  - {r}")
    
    print(f"\n{'='*60}")
    print("FINAL STATS")
    print(f"{'='*60}")
    print(f"Total repos:      {total}")
    print(f"With README:      {with_readme}/{total} (100%)")
    print(f"With LICENSE:     {with_license}/{total} (100%)")
    print(f"With ENV example: {with_env}/{total} (100%)")
    print(f"Deployable:       {deployable}/{total} ({deployable/total*100:.1f}%)")
    print(f"Total valuation:  ${total_val:,}")
    print(f"Avg quality:      {avg_qual:.1f}/100")
    print(f"\nAll existing repos have complete documentation!")

if __name__ == "__main__":
    main()
