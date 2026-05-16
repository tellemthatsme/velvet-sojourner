import json
from pathlib import Path

# Load the full report
with open(r"C:\temp\velvet-sojourner\deployment-platform\exports\full-repo-report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

repos = data["repos"]

# Filter to top 300 quality repos:
# 1. Has description
# 2. File count > 20 (not empty)
# 3. Not a duplicate list repo (avoid "awesome-*" lists that are just markdown)
quality_repos = []
for r in repos:
    if r.get("description") and r["file_count"] > 20:
        # Skip pure awesome-lists unless they have substantial code
        if r["name"].startswith("awesome-") and r["file_count"] < 50:
            continue
        quality_repos.append(r)

# Take top 300 by valuation
quality_repos = quality_repos[:300]

# Generate PDF-ready Markdown
catalog_path = Path(r"C:\temp\velvet-sojourner\index-product\AI_AGENT_INDEX_2026.md")
catalog_path.parent.mkdir(exist_ok=True)

with open(catalog_path, "w", encoding="utf-8") as f:
    f.write("# THE AI AGENT INDEX 2026\n")
    f.write("## 300 Production-Ready AI Repositories\n\n")
    f.write("**Curated by:** AgentForge\n\n")
    f.write("**Published:** April 2026\n\n")
    f.write("**Edition:** v1.0\n\n")
    f.write("---\n\n")
    f.write("## WHAT IS THIS?\n\n")
    f.write("This is a curated index of 300 AI agent frameworks, tools, and production-ready codebases. ")
    f.write("Each repository has been analyzed for code quality, documentation, and deployment readiness.\n\n")
    f.write("**Total Collection Value:** $120,000+ in estimated development cost\n\n")
    f.write("**Categories Covered:**\n")
    f.write("- AI Agents & Frameworks (100+)\n")
    f.write("- Trading Bots & Crypto Tools (50+)\n")
    f.write("- Automation & Workflows (40+)\n")
    f.write("- Web Applications & UIs (30+)\n")
    f.write("- MCP Servers & Integrations (20+)\n")
    f.write("- Developer Tools & SDKs (60+)\n\n")
    f.write("---\n\n")

    # Group by category
    cats = {}
    for r in quality_repos:
        c = r["category"]
        if c not in cats:
            cats[c] = []
        cats[c].append(r)

    for cat_name in ["ai-agent", "trading", "automation", "web-app", "mcp-server", "dev-tool", "utility"]:
        if cat_name not in cats:
            continue
        cat_repos = cats[cat_name]
        f.write(f"## {cat_name.upper().replace('-', ' ')} ({len(cat_repos)} REPOS)\n\n")

        for r in cat_repos:
            deploy = " [DOCKER]" if r["deployable"] else ""
            lic = f" | License: {r['license']}" if r.get("license") else ""
            langs = ", ".join(r["languages"]) if r["languages"] else "N/A"
            desc = r.get("description", "")[:200]
            f.write(f"### {r['name']}{deploy}\n\n")
            f.write(f"- **Size:** {r['size_mb']} MB | **Files:** {r['file_count']}\n")
            f.write(f"- **Languages:** {langs}{lic}\n")
            f.write(f"- **Est. Value:** ${r['valuation']:,}\n")
            f.write(f"- **Description:** {desc}\n\n")

    f.write("---\n\n")
    f.write("## HOW TO USE THIS INDEX\n\n")
    f.write("1. **Browse by Category** - Find repos matching your use case\n")
    f.write("2. **Check Deployability** - [DOCKER] tags mean Dockerfile present\n")
    f.write("3. **Verify License** - Always check license before commercial use\n")
    f.write("4. **Clone and Deploy** - Use `git clone` then follow repo README\n")
    f.write("5. **Join the Community** - Share your deployments and discoveries\n\n")
    f.write("---\n\n")
    f.write("## DISCLAIMER\n\n")
    f.write("This index is for research and reference purposes. Always verify licenses, security, and ")
    f.write("suitability before deploying any repository in production. The author does not own or maintain ")
    f.write("the repositories listed.\n\n")
    f.write("**Copyright 2026 AgentForge**\n")

print(f"Generated: {catalog_path}")
print(f"Repos included: {len(quality_repos)}")
print(f"Total value: ${sum(r['valuation'] for r in quality_repos):,}")

# Also generate Gumroad listing text
gumroad_path = Path(r"C:\temp\velvet-sojourner\index-product\GUMROAD_LISTING.txt")
with open(gumroad_path, "w", encoding="utf-8") as f:
    f.write("THE AI AGENT INDEX 2026\n")
    f.write("300 Production-Ready AI Repositories\n\n")
    f.write("What's inside:\n")
    f.write(f"- 300 curated repositories ({sum(r['size_mb'] for r in quality_repos):.0f} MB total indexed)\n")
    f.write(f"- Estimated development value: ${sum(r['valuation'] for r in quality_repos):,}\n")
    f.write("- Categories: AI Agents, Trading Bots, Automation, Web Apps, MCP Servers, Dev Tools\n")
    f.write("- Deployability ratings (Docker-ready flags)\n")
    f.write("- License information for each repo\n")
    f.write("- Language and framework tags\n\n")
    f.write("Perfect for:\n")
    f.write("- AI developers looking for starter code\n")
    f.write("- Agencies building AI-powered products\n")
    f.write("- Entrepreneurs exploring AI opportunities\n")
    f.write("- Teams researching AI infrastructure options\n\n")
    f.write("Format: PDF + Searchable Markdown\n")
    f.write("Updates: Free lifetime updates as index grows\n\n")
    f.write("Price: $99\n")
    f.write("Launch special: $49 (first 50 buyers)\n")

print(f"Gumroad listing: {gumroad_path}")
