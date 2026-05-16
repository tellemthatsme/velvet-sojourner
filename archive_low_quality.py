import json
import shutil
from pathlib import Path

REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
ARCHIVE_DIR = Path("C:/temp/velvet-sojourner/repos_low_quality")
AUDIT_JSON = Path("C:/temp/velvet-sojourner/audit/full-audit-master.json")

def load_audit():
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def remove_readonly(func, path, _):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main():
    print("=" * 60)
    print("AGENTFORGE: Archive Low-Quality Repos (< 20/100)")
    print("=" * 60)
    
    audit = load_audit()
    repos = audit["repos"]
    
    low_quality = [r for r in repos if r.get("quality_score", 100) < 20]
    print(f"Found {len(low_quality)} repos with quality < 20")
    
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    archived = 0
    report_lines = []
    
    for repo in low_quality:
        name = repo["name"]
        repo_path = REPOS_DIR / name
        dest_path = ARCHIVE_DIR / name
        
        if not repo_path.exists():
            report_lines.append(f"SKIP: {name} - not found in repos/")
            continue
        
        try:
            if dest_path.exists():
                shutil.rmtree(dest_path, onerror=remove_readonly)
            shutil.move(str(repo_path), str(dest_path))
            archived += 1
            report_lines.append(f"MOVED: {name} (quality: {repo.get('quality_score', 0)})")
        except Exception as e:
            report_lines.append(f"ERR:  {name} - {e}")
    
    report_path = Path("C:/temp/velvet-sojourner/audit/Low_Quality_Archive_Report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Low-Quality Repository Archive Report\n\n")
        f.write(f"**Date:** 2026-04-30\n")
        f.write(f"**Threshold:** Quality < 20/100\n")
        f.write(f"**Found:** {len(low_quality)}\n")
        f.write(f"**Archived:** {archived}\n\n")
        f.write("## Results\n\n")
        for line in report_lines:
            f.write(line + "\n")
    
    print(f"\nComplete!")
    print(f"Archived: {archived}/{len(low_quality)}")
    print(f"Report:   {report_path}")

if __name__ == "__main__":
    import os, stat
    main()
