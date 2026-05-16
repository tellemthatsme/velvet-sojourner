"""
Generate comprehensive repo-by-repo report with valuations and action items.
"""
import json
import csv
from pathlib import Path
from collections import defaultdict

REPOS_DIR = Path(r"C:\temp\velvet-sojourner\repos")
EXPORT_DIR = Path(r"C:\temp\velvet-sojourner\deployment-platform\exports")
EXPORT_DIR.mkdir(exist_ok=True)

def get_owner(name):
    for prefix in ["tellemthatsme_", "woodsai69rme_", "leahmfoots_", "acidlink_", "Ashlee69r_"]:
        if name.startswith(prefix):
            return prefix.rstrip("_"), name[len(prefix):]
    return None, name

def get_category(name, languages):
    nl = name.lower()
    if any(k in nl for k in ["agent", "ai-", "llm", "gpt", "claude", "bot", "seek", "operator", "adk", "eliza", "aider"]):
        return "ai-agent"
    elif any(k in nl for k in ["trade", "crypto", "stock", "forex", "nexus", "market"]):
        return "trading"
    elif any(k in nl for k in ["auto", "n8n", "workflow", "scrape", "crawl", "browser-use"]):
        return "automation"
    elif any(k in nl for k in ["webui", "dashboard", "ui", "chat", "app", "studio", "web"]):
        return "web-app"
    elif any(k in nl for k in ["mcp", "server", "api", "gateway"]):
        return "mcp-server"
    elif any(k in nl for k in ["dev", "tool", "cli", "sdk", "awesome-", "coder", "code"]):
        return "dev-tool"
    return "utility"

def calculate_valuation(repo):
    """Calculate estimated development value."""
    base = 0
    size_mb = repo.get("size_mb", 0)
    files = repo.get("file_count", 0)
    has_docker = repo.get("has_dockerfile", False)
    has_compose = repo.get("has_compose", False)
    has_readme = repo.get("has_readme", False)
    languages = repo.get("languages", [])
    category = repo.get("category", "utility")

    # Base by size
    if size_mb > 300: base = 2000
    elif size_mb > 200: base = 1500
    elif size_mb > 100: base = 1000
    elif size_mb > 50: base = 500
    elif size_mb > 20: base = 250
    elif size_mb > 10: base = 150
    elif size_mb > 5: base = 75
    else: base = 25

    # File count bonus
    if files > 5000: base += 1000
    elif files > 2000: base += 500
    elif files > 1000: base += 250
    elif files > 500: base += 100
    elif files > 100: base += 50

    # Category multiplier
    multipliers = {
        "ai-agent": 1.5,
        "trading": 1.3,
        "web-app": 1.2,
        "automation": 1.2,
        "mcp-server": 1.1,
        "dev-tool": 1.0,
        "utility": 0.6
    }
    base *= multipliers.get(category, 0.6)

    # Docker bonus
    if has_docker: base += 200
    if has_compose: base += 100

    # README bonus
    if has_readme: base += 50

    # Language bonus
    if "python" in languages: base += 50
    if "typescript" in languages or "react" in languages: base += 75
    if "rust" in languages: base += 100

    return round(base)

def get_action_items(repo):
    """Identify what needs to be done for each repo."""
    actions = []
    if not repo.get("has_readme", False):
        actions.append("ADD README")
    if not repo.get("has_dockerfile", False) and not repo.get("has_compose", False):
        actions.append("ADD DOCKERFILE")
    if not repo.get("license"):
        actions.append("CHECK LICENSE")
    if repo.get("file_count", 0) < 20:
        actions.append("LOW CONTENT")
    if "javascript" in repo.get("languages", []) and not (repo.get("has_dockerfile") or repo.get("has_compose")):
        actions.append("NEEDS DOCKERIZE")
    return actions

# Scan all repos
print("Scanning all 740 repos for detailed report...")
repos = []
for p in sorted(REPOS_DIR.iterdir()):
    if not p.is_dir():
        continue

    files = list(p.rglob("*"))
    file_count = sum(1 for f in files if f.is_file())
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    size_mb = round(total_size / (1024*1024), 2)

    has_dockerfile = (p / "Dockerfile").exists()
    has_compose = (p / "docker-compose.yml").exists() or (p / "docker-compose.yaml").exists()
    has_readme = (p / "README.md").exists()

    # Languages
    languages = set()
    if (p / "package.json").exists(): languages.add("javascript")
    if (p / "requirements.txt").exists() or (p / "pyproject.toml").exists(): languages.add("python")
    if (p / "Cargo.toml").exists(): languages.add("rust")
    if (p / "go.mod").exists(): languages.add("go")
    if list(p.rglob("*.ts")): languages.add("typescript")
    if list(p.rglob("*.tsx")): languages.add("react")
    if list(p.rglob("*.vue")): languages.add("vue")
    if list(p.rglob("*.rs")): languages.add("rust")
    if list(p.rglob("*.cpp")) or list(p.rglob("*.c")): languages.add("c/c++")
    if list(p.rglob("*.java")): languages.add("java")
    if list(p.rglob("*.rb")): languages.add("ruby")
    if list(p.rglob("*.php")): languages.add("php")

    # License
    license_type = None
    for lic_name in ["LICENSE", "LICENSE.md", "LICENSE.txt", "license", "license.md"]:
        if (p / lic_name).exists():
            try:
                lic_text = (p / lic_name).read_text(encoding="utf-8", errors="ignore").upper()
                if "MIT" in lic_text: license_type = "MIT"
                elif "APACHE" in lic_text: license_type = "Apache-2.0"
                elif "GPL" in lic_text: license_type = "GPL"
                elif "BSD" in lic_text: license_type = "BSD"
                elif "UNLICENSE" in lic_text: license_type = "Unlicense"
                else: license_type = "Other"
            except:
                pass
            break

    # Description
    description = None
    if has_readme:
        try:
            text = (p / "README.md").read_text(encoding="utf-8", errors="ignore")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines[:15]:
                if not line.startswith("#") and not line.startswith("!") and not line.startswith("[") and len(line) > 10:
                    description = line[:300]
                    break
        except:
            pass

    owner, base_name = get_owner(p.name)
    category = get_category(p.name, languages)

    repo_data = {
        "name": p.name,
        "base_name": base_name,
        "owner": owner,
        "category": category,
        "size_mb": size_mb,
        "file_count": file_count,
        "has_dockerfile": has_dockerfile,
        "has_compose": has_compose,
        "has_readme": has_readme,
        "languages": sorted(languages),
        "license": license_type,
        "description": description,
        "deployable": has_dockerfile or has_compose
    }

    repo_data["valuation"] = calculate_valuation(repo_data)
    repo_data["actions"] = get_action_items(repo_data)

    repos.append(repo_data)

# Sort by valuation descending
repos.sort(key=lambda x: x["valuation"], reverse=True)

# Generate reports
print(f"\nScanned {len(repos)} repos")

# 1. Full JSON
json_path = EXPORT_DIR / "full-repo-report.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({
        "generated": "2026-04-30",
        "total_repos": len(repos),
        "total_valuation": sum(r["valuation"] for r in repos),
        "avg_valuation": round(sum(r["valuation"] for r in repos) / len(repos)),
        "total_size_gb": round(sum(r["size_mb"] for r in repos) / 1024, 2),
        "deployable_count": sum(1 for r in repos if r["deployable"]),
        "repos": repos
    }, f, indent=2)
print(f"JSON: {json_path}")

# 2. Full CSV
csv_path = EXPORT_DIR / "full-repo-report.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["rank", "name", "base_name", "owner", "category", "size_mb", "file_count", "languages", "has_dockerfile", "has_compose", "has_readme", "license", "deployable", "valuation", "actions", "description"])
    writer.writeheader()
    for i, r in enumerate(repos, 1):
        row = dict(r)
        row["rank"] = i
        row["languages"] = ", ".join(row["languages"])
        row["actions"] = "; ".join(row["actions"])
        writer.writerow(row)
print(f"CSV: {csv_path}")

# 3. Comprehensive Markdown Report
md_path = EXPORT_DIR / "FULL_REPORT.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# COMPLETE REPOSITORY REPORT\n")
    f.write("## AgentForge Collection - 740 Curated Repositories\n\n")
    f.write(f"**Generated:** 2026-04-30\n\n")
    f.write(f"**Total Repositories:** {len(repos)}\n\n")
    f.write(f"**Total Size:** {round(sum(r['size_mb'] for r in repos)/1024, 2)} GB\n\n")
    f.write(f"**Total Valuation:** ${sum(r['valuation'] for r in repos):,}\n\n")
    f.write(f"**Average Valuation:** ${round(sum(r['valuation'] for r in repos)/len(repos)):,}\n\n")
    f.write(f"**Deployable:** {sum(1 for r in repos if r['deployable'])}\n\n")

    # Category summary
    f.write("## CATEGORY SUMMARY\n\n")
    cat_stats = defaultdict(lambda: {"count": 0, "total_val": 0, "total_size": 0, "deployable": 0})
    for r in repos:
        c = r["category"]
        cat_stats[c]["count"] += 1
        cat_stats[c]["total_val"] += r["valuation"]
        cat_stats[c]["total_size"] += r["size_mb"]
        if r["deployable"]:
            cat_stats[c]["deployable"] += 1

    f.write("| Category | Count | Valuation | Size | Deployable |\n")
    f.write("|----------|-------|-----------|------|------------|\n")
    for cat in sorted(cat_stats.keys(), key=lambda x: -cat_stats[x]["count"]):
        s = cat_stats[cat]
        f.write(f"| {cat} | {s['count']} | ${s['total_val']:,} | {round(s['total_size']/1024, 1)} GB | {s['deployable']} |\n")

    # Account summary
    f.write("\n## ACCOUNT SUMMARY\n\n")
    acct_stats = defaultdict(lambda: {"count": 0, "total_val": 0, "total_size": 0})
    for r in repos:
        a = r["owner"] or "unprefixed"
        acct_stats[a]["count"] += 1
        acct_stats[a]["total_val"] += r["valuation"]
        acct_stats[a]["total_size"] += r["size_mb"]

    f.write("| Account | Count | Valuation | Size |\n")
    f.write("|---------|-------|-----------|------|\n")
    for acct in sorted(acct_stats.keys(), key=lambda x: -acct_stats[x]["count"]):
        s = acct_stats[acct]
        f.write(f"| {acct} | {s['count']} | ${s['total_val']:,} | {round(s['total_size']/1024, 1)} GB |\n")

    # Action items summary
    f.write("\n## ACTION ITEMS SUMMARY\n\n")
    action_counts = defaultdict(int)
    for r in repos:
        for a in r["actions"]:
            action_counts[a] += 1

    f.write("| Action Needed | Count |\n")
    f.write("|---------------|-------|\n")
    for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
        f.write(f"| {action} | {count} |\n")

    # Top 100 detailed
    f.write("\n## TOP 100 REPOSITORIES (Detailed)\n\n")
    f.write("| # | Name | Owner | Category | Size | Files | Valuation | Deployable | License | Actions |\n")
    f.write("|---|------|-------|----------|------|-------|-----------|------------|---------|---------|\n")
    for i, r in enumerate(repos[:100], 1):
        owner = r["owner"] or "-"
        deploy = "YES" if r["deployable"] else "no"
        lic = r["license"] or "?"
        actions = "; ".join(r["actions"]) if r["actions"] else "OK"
        f.write(f"| {i} | {r['name']} | {owner} | {r['category']} | {r['size_mb']} MB | {r['file_count']} | ${r['valuation']:,} | {deploy} | {lic} | {actions} |\n")

    # All repos (condensed)
    f.write("\n## ALL REPOSITORIES (Ranked by Valuation)\n\n")
    for i, r in enumerate(repos, 1):
        owner = r["owner"] or "-"
        deploy = "DOCKER" if r["deployable"] else "-"
        actions = "; ".join(r["actions"]) if r["actions"] else "OK"
        desc = (r["description"] or "")[:80]
        f.write(f"### {i}. {r['name']} (${r['valuation']:,})\n\n")
        f.write(f"- **Owner:** {owner}\n")
        f.write(f"- **Category:** {r['category']}\n")
        f.write(f"- **Size:** {r['size_mb']} MB | **Files:** {r['file_count']}\n")
        f.write(f"- **Languages:** {', '.join(r['languages']) or 'N/A'}\n")
        f.write(f"- **License:** {r['license'] or 'Unknown'}\n")
        f.write(f"- **Deployable:** {deploy}\n")
        f.write(f"- **Actions:** {actions}\n")
        if desc:
            f.write(f"- **Description:** {desc}\n")
        f.write("\n")

print(f"Markdown: {md_path}")
print(f"\n{'='*60}")
print("COMPLETE REPORT GENERATED")
print(f"{'='*60}")
print(f"Total repos: {len(repos)}")
print(f"Total valuation: ${sum(r['valuation'] for r in repos):,}")
print(f"Avg valuation: ${round(sum(r['valuation'] for r in repos)/len(repos)):,}")
print(f"Deployable: {sum(1 for r in repos if r['deployable'])}")
print(f"\nFiles created:")
print(f"  {json_path}")
print(f"  {csv_path}")
print(f"  {md_path}")
