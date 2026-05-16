"""
Clean duplicate repos, export curated list, and prepare for launch.
"""
import os
import json
import csv
import shutil
from pathlib import Path
from collections import defaultdict

REPOS_DIR = Path(r"C:\temp\velvet-sojourner\repos")
EXPORT_DIR = Path(r"C:\temp\velvet-sojourner\deployment-platform\exports")
EXPORT_DIR.mkdir(exist_ok=True)
DUP_DIR = Path(r"C:\temp\velvet-sojourner\repos_duplicates")
DUP_DIR.mkdir(exist_ok=True)

def get_repo_signature(repo_path):
    """Generate a signature for duplicate detection."""
    files = list(repo_path.rglob("*"))
    file_count = sum(1 for f in files if f.is_file())
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    top_files = sorted([f.name for f in repo_path.iterdir() if f.is_file()])[:20]
    return (file_count, total_size, tuple(top_files))

def get_base_name(name):
    """Remove account prefix to find base repo name."""
    for prefix in ["tellemthatsme_", "woodsai69rme_", "leahmfoots_", "acidlink_", "Ashlee69r_"]:
        if name.startswith(prefix):
            return name[len(prefix):]
    return name

def is_empty(repo_path):
    files = list(repo_path.rglob("*"))
    file_count = sum(1 for f in files if f.is_file())
    return file_count < 5

# Phase 1: Scan all repos
print("Phase 1: Scanning all repos...")
repos = []
for p in REPOS_DIR.iterdir():
    if not p.is_dir():
        continue
    sig = get_repo_signature(p)
    repos.append({
        "name": p.name,
        "path": p,
        "base_name": get_base_name(p.name),
        "file_count": sig[0],
        "total_size": sig[1],
        "top_files": sig[2],
        "empty": is_empty(p)
    })

print(f"  Total scanned: {len(repos)}")
print(f"  Empty repos: {sum(1 for r in repos if r['empty'])}")

# Phase 2: Identify exact duplicates by signature
print("\nPhase 2: Identifying exact duplicates...")
sig_map = defaultdict(list)
for r in repos:
    if not r['empty']:
        sig_map[(r['file_count'], r['total_size'])].append(r)

duplicates = []
keepers = []
for sig, group in sig_map.items():
    if len(group) > 1:
        # Sort: prefer unprefixed names, then shortest name
        group.sort(key=lambda r: (get_base_name(r['name']) != r['name'], len(r['name']), r['name']))
        keepers.append(group[0])
        duplicates.extend(group[1:])
    else:
        keepers.append(group[0])

# Also check empty repos for dedup
empty_repos = [r for r in repos if r['empty']]
empty_by_base = defaultdict(list)
for r in empty_repos:
    empty_by_base[r['base_name']].append(r)

for base, group in empty_by_base.items():
    if len(group) > 1:
        group.sort(key=lambda r: (get_base_name(r['name']) != r['name'], len(r['name']), r['name']))
        keepers.append(group[0])
        duplicates.extend(group[1:])
    else:
        keepers.append(group[0])

print(f"  Unique repos to keep: {len(keepers)}")
print(f"  Duplicates to move: {len(duplicates)}")

# Phase 3: Move duplicates
print("\nPhase 3: Moving duplicate repos...")
moved = 0
for dup in duplicates:
    src = dup['path']
    dst = DUP_DIR / dup['name']
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    try:
        shutil.move(str(src), str(dst))
        moved += 1
    except Exception as e:
        print(f"    ERROR moving {dup['name']}: {e}")

print(f"  Moved {moved} duplicate repos to {DUP_DIR}")

# Phase 4: Remove empty repos (under 5 files, no real code)
print("\nPhase 4: Removing empty placeholder repos...")
remaining = [r for r in keepers if r['path'].exists()]  # some keepers might have been moved
empties_removed = 0
for r in remaining:
    if r['empty']:
        try:
            shutil.rmtree(r['path'], ignore_errors=True)
            empties_removed += 1
        except Exception as e:
            print(f"    ERROR removing {r['name']}: {e}")

print(f"  Removed {empties_removed} empty repos")

# Phase 5: Re-scan cleaned collection
print("\nPhase 5: Re-scanning cleaned collection...")
cleaned_repos = []
for p in REPOS_DIR.iterdir():
    if not p.is_dir():
        continue
    files = list(p.rglob("*"))
    file_count = sum(1 for f in files if f.is_file())
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    has_dockerfile = (p / "Dockerfile").exists()
    has_compose = (p / "docker-compose.yml").exists() or (p / "docker-compose.yaml").exists()
    has_readme = (p / "README.md").exists()

    # Detect languages
    languages = set()
    if (p / "package.json").exists(): languages.add("javascript")
    if (p / "requirements.txt").exists() or (p / "pyproject.toml").exists(): languages.add("python")
    if (p / "Cargo.toml").exists(): languages.add("rust")
    if (p / "go.mod").exists(): languages.add("go")
    if list(p.rglob("*.ts")): languages.add("typescript")
    if list(p.rglob("*.tsx")): languages.add("react")
    if list(p.rglob("*.vue")): languages.add("vue")
    if list(p.rglob("*.rs")): languages.add("rust")

    # Detect category
    name_lower = p.name.lower()
    category = "utility"
    if any(k in name_lower for k in ["agent", "ai-", "llm", "gpt", "claude", "bot", "seek", "operator"]):
        category = "ai-agent"
    elif any(k in name_lower for k in ["trade", "crypto", "stock", "forex", "nexus", "market"]):
        category = "trading"
    elif any(k in name_lower for k in ["auto", "n8n", "workflow", "scrape", "crawl", "browser-use"]):
        category = "automation"
    elif any(k in name_lower for k in ["webui", "dashboard", "ui", "chat", "app", "studio"]):
        category = "web-app"
    elif any(k in name_lower for k in ["mcp", "server", "api", "gateway"]):
        category = "mcp-server"
    elif any(k in name_lower for k in ["dev", "tool", "cli", "sdk", "awesome-", "coder"]):
        category = "dev-tool"

    # Get description
    description = None
    if has_readme:
        try:
            text = (p / "README.md").read_text(encoding="utf-8", errors="ignore")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines[:10]:
                if not line.startswith("#") and len(line) > 10:
                    description = line[:250]
                    break
        except:
            pass

    # Get license
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

    cleaned_repos.append({
        "name": p.name,
        "base_name": get_base_name(p.name),
        "owner": next((prefix.rstrip("_") for prefix in ["tellemthatsme_", "woodsai69rme_", "leahmfoots_", "acidlink_", "Ashlee69r_"] if p.name.startswith(prefix)), None),
        "file_count": file_count,
        "size_mb": round(total_size / (1024*1024), 2),
        "has_dockerfile": has_dockerfile,
        "has_compose": has_compose,
        "has_readme": has_readme,
        "languages": sorted(languages),
        "category": category,
        "deployable": has_dockerfile or has_compose,
        "description": description,
        "license": license_type
    })

# Sort by size descending
cleaned_repos.sort(key=lambda x: x["size_mb"], reverse=True)

print(f"  Cleaned collection: {len(cleaned_repos)} repos")
print(f"  Total size: {round(sum(r['size_mb'] for r in cleaned_repos)/1024, 2)} GB")
print(f"  Deployable: {sum(1 for r in cleaned_repos if r['deployable'])}")

# Category breakdown
cat_counts = defaultdict(int)
for r in cleaned_repos:
    cat_counts[r['category']] += 1
print("  Categories:")
for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"    {c}: {n}")

# Phase 6: Export JSON
print("\nPhase 6: Exporting curated lists...")
json_path = EXPORT_DIR / "curated-repos.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({
        "generated": "2026-04-30",
        "total_repos": len(cleaned_repos),
        "total_size_gb": round(sum(r['size_mb'] for r in cleaned_repos)/1024, 2),
        "deployable_count": sum(1 for r in cleaned_repos if r['deployable']),
        "categories": dict(sorted(cat_counts.items(), key=lambda x: -x[1])),
        "repos": cleaned_repos
    }, f, indent=2)
print(f"  JSON: {json_path}")

# Phase 7: Export CSV (top 500)
print("\nPhase 7: Exporting CSV (top 500)...")
csv_path = EXPORT_DIR / "curated-repos-top500.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["rank", "name", "owner", "category", "size_mb", "file_count", "languages", "deployable", "has_dockerfile", "has_compose", "license", "description"])
    writer.writeheader()
    for i, r in enumerate(cleaned_repos[:500], 1):
        row = {k: r[k] for k in ["name", "owner", "category", "size_mb", "file_count", "languages", "deployable", "has_dockerfile", "has_compose", "license", "description"]}
        row["rank"] = i
        row["languages"] = ", ".join(row["languages"])
        writer.writerow(row)
print(f"  CSV: {csv_path}")

# Phase 8: Export Markdown catalog
print("\nPhase 8: Exporting Markdown catalog...")
md_path = EXPORT_DIR / "CATALOG.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# AgentForge Repository Catalog\n\n")
    f.write(f"**Generated:** 2026-04-30\n\n")
    f.write(f"**Total Repositories:** {len(cleaned_repos)}\n\n")
    f.write(f"**Total Size:** {round(sum(r['size_mb'] for r in cleaned_repos)/1024, 2)} GB\n\n")
    f.write(f"**Deployable:** {sum(1 for r in cleaned_repos if r['deployable'])}\n\n")
    f.write("## Categories\n\n")
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
        f.write(f"- **{c.title()}**: {n} repos\n")
    f.write("\n## Top 100 Repositories\n\n")
    f.write("| # | Name | Owner | Category | Size | Files | Deployable | License |\n")
    f.write("|---|------|-------|----------|------|-------|------------|---------|\n")
    for i, r in enumerate(cleaned_repos[:100], 1):
        deploy = "YES" if r['deployable'] else "no"
        owner = r['owner'] or "-"
        lic = r['license'] or "?"
        f.write(f"| {i} | {r['name']} | {owner} | {r['category']} | {r['size_mb']} MB | {r['file_count']} | {deploy} | {lic} |\n")
print(f"  Markdown: {md_path}")

print("\n" + "="*60)
print("CLEANUP & EXPORT COMPLETE")
print("="*60)
print(f"Original repos:    {len(repos)}")
print(f"Duplicates moved:  {moved}")
print(f"Empties removed:   {empties_removed}")
print(f"Final collection:  {len(cleaned_repos)}")
print(f"Space saved:       ~{round((len(duplicates) + empties_removed) * 5, 1)} MB estimated")
print(f"\nExports saved to: {EXPORT_DIR}")
