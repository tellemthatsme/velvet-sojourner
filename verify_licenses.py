import json
from pathlib import Path

REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
AUDIT_JSON = Path("C:/temp/velvet-sojourner/audit/full-audit-master.json")

def load_audit():
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def mit_license_text():
    return """MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def main():
    print("=" * 60)
    print("AGENTFORGE: License Verification & Addition (Top 100)")
    print("=" * 60)
    
    audit = load_audit()
    repos = sorted(audit["repos"], key=lambda x: x.get("valuation", 0), reverse=True)[:100]
    
    report_lines = []
    added = 0
    existing = 0
    
    for repo in repos:
        name = repo["name"]
        repo_path = REPOS_DIR / name
        license_path = repo_path / "LICENSE"
        license_md_path = repo_path / "LICENSE.md"
        
        has_license = repo.get("license") is not None
        
        if has_license:
            existing += 1
            report_lines.append(f"EXISTS: {name} - {repo.get('license', 'unknown')}")
            continue
        
        # No license - add MIT
        if repo_path.exists():
            try:
                with open(license_path, "w", encoding="utf-8") as f:
                    f.write(mit_license_text())
                added += 1
                report_lines.append(f"ADDED:  {name} - MIT license added")
            except Exception as e:
                report_lines.append(f"ERROR:  {name} - {e}")
        else:
            report_lines.append(f"MISSING: {name} - repo directory not found")
    
    # Write report
    report_path = Path("C:/temp/velvet-sojourner/audit/License_Verification_Report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# License Verification Report (Top 100 Repos)\n\n")
        f.write(f"**Date:** 2026-04-30\n")
        f.write(f"**Total Reviewed:** 100\n")
        f.write(f"**Already Licensed:** {existing}\n")
        f.write(f"**MIT Licenses Added:** {added}\n")
        f.write(f"**Still Missing:** {100 - existing - added}\n\n")
        f.write("## Results\n\n")
        for line in report_lines:
            f.write(line + "\n")
    
    print(f"\nComplete!")
    print(f"Already licensed: {existing}")
    print(f"MIT added:        {added}")
    print(f"Report:           {report_path}")

if __name__ == "__main__":
    main()
