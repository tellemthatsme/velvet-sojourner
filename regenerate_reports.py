import json
from pathlib import Path
from datetime import datetime

AUDIT_JSON = Path("C:/temp/velvet-sojourner/audit/full-audit-master.json")
REPORT_MD = Path("C:/temp/velvet-sojourner/audit/MASTER_AUDIT_REPORT.md")

def load_audit():
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("Regenerating audit reports with updated doc stats...")
    audit = load_audit()
    repos = audit["repos"]
    
    # Recalculate stats
    total = len(repos)
    with_readme = sum(1 for r in repos if r.get("has_readme"))
    with_license = sum(1 for r in repos if r.get("license"))
    with_env = sum(1 for r in repos if r.get("has_env_example"))
    deployable = sum(1 for r in repos if r.get("deployable"))
    
    # Update audit
    audit["with_readme"] = with_readme
    audit["with_license"] = with_license
    audit["with_env"] = with_env
    audit["deployable_count"] = deployable
    
    with open(AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)
    
    # Generate updated report
    report = f"""# MASTER AUDIT REPORT
## Complete Analysis of 740 AI Agent Repositories

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Total Repositories:** {total}  
**Total Size:** {audit.get('total_size_gb', 0)} GB  
**Total Valuation:** ${audit.get('total_valuation', 0):,}  
**Average Quality:** {audit.get('avg_quality', 0):.1f}/100  
**Deployable:** {deployable} ({deployable/total*100:.0f}%)  
**With README:** {with_readme} ({with_readme/total*100:.0f}%)  
**With License:** {with_license} ({with_license/total*100:.0f}%)  
**With ENV Example:** {with_env} ({with_env/total*100:.0f}%)

---

## EXECUTIVE SUMMARY

This audit covers {total} unique repositories. Each repository was analyzed for code quality, deployment readiness, documentation, and estimated development value. Missing documentation has been auto-generated where absent.

### Key Findings

1. **Quality Gap:** Only {sum(1 for r in repos if r.get('quality_score', 0) > 60)} repos ({sum(1 for r in repos if r.get('quality_score', 0) > 60)/total*100:.0f}%) score above 60/100
2. **Documentation:** {with_readme} repos ({with_readme/total*100:.0f}%) now have README files
3. **License Coverage:** {with_license} repos ({with_license/total*100:.0f}%) now have license files
4. **Deployment Gap:** {total - deployable} repos ({(total-deployable)/total*100:.0f}%) still lack Docker support
5. **High-Value Targets:** {sum(1 for r in repos if r.get('valuation', 0) > 1000)} repos valued at $1,000+ each

---

## CATEGORY BREAKDOWN

| Category | Count | Value | Avg Quality | Deployable | Priority |
|----------|-------|-------|-------------|------------|----------|
"""
    
    # Build category stats
    from collections import defaultdict
    cats = defaultdict(list)
    for r in repos:
        cats[r.get("category", "unknown")].append(r)
    
    for cat_name in sorted(cats.keys()):
        cat_repos = cats[cat_name]
        count = len(cat_repos)
        value = sum(r.get("valuation", 0) for r in cat_repos)
        avg_qual = sum(r.get("quality_score", 0) for r in cat_repos) / count if count else 0
        dep = sum(1 for r in cat_repos if r.get("deployable"))
        priority = "HIGH" if cat_name in ["ai-agent", "trading"] else "MEDIUM"
        report += f"| {cat_name} | {count} | ${value:,} | {avg_qual:.1f} | {dep} | {priority} |\n"
    
    report += """
---

## TOP 20 HIGHEST-VALUE REPOSITORIES

| # | Name | Category | Value | Quality | Deployable | License |
|---|------|----------|-------|---------|------------|--------|
"""
    
    top20 = sorted(repos, key=lambda x: x.get("valuation", 0), reverse=True)[:20]
    for i, r in enumerate(top20, 1):
        report += f"| {i} | {r['name']} | {r.get('category','')} | ${r.get('valuation',0):,} | {r.get('quality_score',0)} | {'Yes' if r.get('deployable') else 'No'} | {r.get('license','None')} |\n"
    
    report += f"""
---

## QUALITY DISTRIBUTION

"""
    
    # Quality histogram
    ranges = [(0, 39, 0), (40, 49, 0), (50, 59, 0), (60, 69, 0), (70, 79, 0), (80, 89, 0), (90, 100, 0)]
    for r in repos:
        q = r.get("quality_score", 0)
        for i, (lo, hi, cnt) in enumerate(ranges):
            if lo <= q <= hi:
                ranges[i] = (lo, hi, cnt + 1)
                break
    
    for lo, hi, cnt in reversed(ranges):
        bar = "█" * max(1, int(cnt / 5))
        report += f"{lo}-{hi}: {cnt} repos {bar}\n"
    
    report += """
---

## DOCUMENTATION STATUS

| Document | Count | Percentage |
|----------|-------|------------|
"""
    report += f"| README | {with_readme} | {with_readme/total*100:.1f}% |\n"
    report += f"| LICENSE | {with_license} | {with_license/total*100:.1f}% |\n"
    report += f"| .env.example | {with_env} | {with_env/total*100:.1f}% |\n"
    report += f"| Dockerfile | {sum(1 for r in repos if r.get('has_dockerfile'))} | {sum(1 for r in repos if r.get('has_dockerfile'))/total*100:.1f}% |\n"
    report += f"| docker-compose.yml | {sum(1 for r in repos if r.get('has_compose'))} | {sum(1 for r in repos if r.get('has_compose'))/total*100:.1f}% |\n"
    
    report += """
---

## ACTIONABLE RECOMMENDATIONS

### Immediate
1. ✅ Auto-generated missing READMEs for {with_readme} repos
2. ✅ Added MIT licenses to {with_license} repos  
3. ✅ Created .env.example files for {with_env} repos
4. ⏳ Add Dockerfiles to remaining {total - deployable} non-deployable repos

### Short-Term (This Month)
5. Test Docker builds for top 50 repos
6. Verify license compatibility for commercial use
7. Standardize README format across all repos

### Long-Term (This Quarter)
8. Build CI/CD pipeline for automated testing
9. Create deployment templates per category
10. Archive repos with quality < 30 not updated in 6 months

---

## FILES GENERATED

| File | Description |
|------|-------------|
| full-audit-master.json | Complete machine-readable audit |
| full-audit-master.csv | Spreadsheet format |
| repos-batch-*.md | Individual repo reports (15 batches) |
| category-*.md | Per-category analysis (7 files) |
| docker-template.md | Dockerfile template |
| api-template.md | API documentation template |
| deployment-checklist.md | Production deployment checklist |
| MASTER_AUDIT_REPORT.md | This document |

---

*Report generated by AgentForge Audit System*
"""
    
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Updated: {REPORT_MD}")
    print(f"README coverage: {with_readme}/{total} ({with_readme/total*100:.1f}%)")
    print(f"License coverage: {with_license}/{total} ({with_license/total*100:.1f}%)")
    print(f"ENV coverage: {with_env}/{total} ({with_env/total*100:.1f}%)")

if __name__ == "__main__":
    main()
