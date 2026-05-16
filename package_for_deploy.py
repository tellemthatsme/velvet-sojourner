import shutil
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("C:/temp/velvet-sojourner")
DEPLOY_DIR = BASE_DIR / "deploy-ready"

def ensure_clean(dir_path):
    if dir_path.exists():
        shutil.rmtree(dir_path)
    dir_path.mkdir(parents=True)

def package_consulting():
    print("Packaging consulting landing page...")
    src = BASE_DIR / "consulting"
    dst = DEPLOY_DIR / "consulting-page"
    shutil.copytree(src, dst, dirs_exist_ok=True)
    
    # Add deploy instructions
    with open(dst / "DEPLOY.md", "w") as f:
        f.write("""# Consulting Page Deployment

## Quick Deploy (Netlify)
1. Drag this folder into https://app.netlify.com/drop
2. Custom domain: Settings > Domain management
3. Forms: Add `netlify` attribute to `<form>` tags

## Or use Netlify CLI
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=.
```

## Before Launch Checklist
- [ ] Update Calendly link in index.html (search for calendly.com)
- [ ] Update email address (ashlee69r@gmail.com)
- [ ] Add Google Analytics or Plausible script
- [ ] Test on mobile
- [ ] Set up contact form endpoint (Formspree/Netlify Forms)
""")
    print(f"  -> {dst}")

def package_gumroad():
    print("Packaging Gumroad product...")
    dst = DEPLOY_DIR / "gumroad-product"
    dst.mkdir(parents=True, exist_ok=True)
    
    # Copy index files
    index_src = BASE_DIR / "index-product"
    for f in ["AI_AGENT_INDEX_2026.md", "GUMROAD_LISTING.txt"]:
        shutil.copy2(index_src / f, dst / f)
    
    # Copy exports
    exports_src = BASE_DIR / "deployment-platform" / "exports"
    if exports_src.exists():
        shutil.copytree(exports_src, dst / "exports", dirs_exist_ok=True)
    
    # Copy audit reports
    audit_src = BASE_DIR / "audit"
    for f in ["full-audit-master.csv", "full-audit-master.json", "MASTER_AUDIT_REPORT.md"]:
        if (audit_src / f).exists():
            shutil.copy2(audit_src / f, dst / f)
    
    # Add README
    with open(dst / "README.txt", "w") as f:
        f.write("""THE AI AGENT INDEX 2026
=======================

Thank you for your purchase!

FILES INCLUDED:
- AI_AGENT_INDEX_2026.md ...... Main catalog (300 top repos)
- GUMROAD_LISTING.txt ......... Product description for your reference
- full-audit-master.csv ....... Complete spreadsheet (740 repos)
- full-audit-master.json ...... Machine-readable full dataset
- MASTER_AUDIT_REPORT.md ...... Executive summary
- exports/ .................... JSON and CSV exports

UPDATES:
Check your email for quarterly update notifications.
Or visit: https://agentforge-consulting.vercel.app/updates

For questions: ashlee69r@gmail.com
For done-for-you deployment: https://agentforge-consulting.vercel.app

LICENSE:
This index is for your personal/business use.
Agency license holders may share with clients.
""")
    
    # Zip it
    zip_path = DEPLOY_DIR / "AI-Agent-Index-2026"
    shutil.make_archive(str(zip_path), 'zip', str(dst))
    print(f"  -> {dst}")
    print(f"  -> {zip_path}.zip")

def package_saas():
    print("Packaging SaaS landing page...")
    src = BASE_DIR / "deployment-platform" / "landing-page"
    dst = DEPLOY_DIR / "saas-landing-page"
    shutil.copytree(src, dst, dirs_exist_ok=True)
    
    with open(dst / "DEPLOY.md", "w") as f:
        f.write("""# SaaS Landing Page Deployment

## Quick Deploy (Vercel)
```bash
npm i -g vercel
vercel --prod
```

## Or (Netlify Drop)
Drag this folder into https://app.netlify.com/drop

## Before Launch Checklist
- [ ] Connect Stripe account in stripe_auth.py
- [ ] Update pricing tables
- [ ] Add testimonials
- [ ] Set up analytics (Google Analytics / Plausible)
- [ ] Connect domain
- [ ] Test mobile responsiveness
- [ ] Add privacy policy + terms
""")
    print(f"  -> {dst}")

def package_platform():
    print("Packaging AgentForge platform...")
    src = BASE_DIR / "deployment-platform"
    dst = DEPLOY_DIR / "agentforge-platform"
    
    # Only copy deployer API and docker-compose, not node_modules
    shutil.copytree(src, dst, dirs_exist_ok=True)
    
    # Remove large/generated dirs if they exist
    for bad in ["node_modules", "__pycache__", ".venv", "venv"]:
        for p in dst.rglob(bad):
            if p.is_dir():
                shutil.rmtree(p)
    
    with open(dst / "QUICKSTART.md", "w") as f:
        f.write("""# AgentForge Platform Quickstart

## Requirements
- Docker + Docker Compose
- 4GB RAM minimum
- Domain (optional, localhost works)

## Start Everything
```bash
docker-compose up -d
```

## Access Points
- Dashboard: http://localhost:8080
- API Docs: http://localhost:8000/docs
- n8n: http://localhost:5678
- Open WebUI: http://localhost:3000
- Grafana: http://localhost:3001

## Add Your API Keys
Edit `.env`:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

## First Deploy
```bash
cd deployer
pip install -r requirements.txt
uvicorn main:app --reload
```

For full docs see AGENTFORGE.md in project root.
""")
    print(f"  -> {dst}")

def generate_master_deploy_report():
    report = DEPLOY_DIR / "DEPLOY_GUIDE.md"
    with open(report, "w") as f:
        f.write("""# AgentForge Launch Deployment Guide

## Three Revenue Streams — Ready to Deploy

---

### 1. CONSULTING SERVICES
**Package:** `deploy-ready/consulting-page/`
**Deploy:** Netlify Drop (drag folder) or Vercel CLI
**Price:** $2,500 setup + $500/mo support
**Target:** 5 clients/month
**Revenue potential:** $12,500/month

### 2. CURATED INDEX PRODUCT
**Package:** `deploy-ready/gumroad-product/`
**Platform:** Gumroad / LemonSqueezy
**Price:** $49 launch / $99 standard / $299 agency
**Target:** 100 sales/month
**Revenue potential:** $4,900-$29,900/month

### 3. SAAS PLATFORM
**Package:** `deploy-ready/saas-landing-page/` + `deploy-ready/agentforge-platform/`
**Deploy:** Landing page to Vercel/Netlify, platform to VPS/Render
**Price:** $49-$299/mo subscriptions
**Target:** 50 subscribers
**Revenue potential:** $2,450-$14,950/month

---

## Launch Sequence

### Day 1-2: Consulting
1. Deploy consulting page to Netlify
2. Connect Calendly
3. Send 50 LinkedIn DMs using templates in consulting/OUTREACH_TEMPLATES.md
4. Post on Twitter/X about "AI infrastructure in 48 hours"

### Day 3-5: Index Product
1. Upload AI-Agent-Index-2026.zip to Gumroad
2. Set price to $49 (launch special)
3. Share on Hacker News, Reddit r/LocalLLaMA, IndieHackers
4. Email 100 AI developers

### Day 6-7: SaaS
1. Deploy landing page
2. Connect Stripe
3. Set up waitlist or early access
4. Announce on Twitter/X and LinkedIn

---

## Revenue Projections (Month 1)

| Stream | Conservative | Moderate | Aggressive |
|--------|-------------|----------|------------|
| Consulting | $5,000 (2 clients) | $12,500 (5 clients) | $25,000 (10 clients) |
| Index | $1,000 (20 sales) | $4,900 (100 sales) | $9,900 (200 sales) |
| SaaS | $0 (waitlist) | $1,000 (20 subs) | $5,000 (100 subs) |
| **Total** | **$6,000** | **$18,400** | **$39,900** |

---

## Files Ready

- [x] Consulting page (HTML/CSS, no build step)
- [x] Gumroad product (ZIP with index + reports)
- [x] SaaS landing page (HTML/CSS)
- [x] AgentForge platform (Docker Compose)
- [x] Outreach templates (8 messages)
- [x] Audit reports (JSON, CSV, MD)

---

**Status: READY FOR LAUNCH**
""")
    print(f"  -> {report}")

def main():
    print("=" * 60)
    print("AGENTFORGE: Building Deployment Packages")
    print("=" * 60)
    
    ensure_clean(DEPLOY_DIR)
    
    package_consulting()
    package_gumroad()
    package_saas()
    package_platform()
    generate_master_deploy_report()
    
    # Summary
    print("\n" + "=" * 60)
    print("DEPLOYMENT PACKAGES READY")
    print("=" * 60)
    
    for item in DEPLOY_DIR.iterdir():
        if item.is_dir():
            size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
            print(f"  {item.name:30} {size/1024/1024:.1f} MB")
        else:
            size = item.stat().st_size
            print(f"  {item.name:30} {size/1024:.1f} KB")
    
    print(f"\nAll packages in: {DEPLOY_DIR}")
    print("Next: Deploy consulting page, upload Gumroad product, deploy SaaS landing page")

if __name__ == "__main__":
    main()
