#!/usr/bin/env python3
"""
PROCEED - Non-Interactive Master Automation
Runs all steps without user prompts
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

print("="*80)
print("MASTER AUTOMATION - PROCEEDING WITH ALL STEPS".center(80))
print("="*80)
print()

# Track results
results = {}
start_time = datetime.now()

def run_cmd(cmd, desc, timeout=60):
    """Run command and return success status"""
    print(f"\n[RUNNING] {desc}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"[OK] {desc}")
            return True
        else:
            print(f"[WARN] {desc} - non-zero exit")
            return False
    except Exception as e:
        print(f"[ERROR] {desc}: {e}")
        return False

# ============================================================================
# STEP 1: Check Tokens
# ============================================================================
print("\n" + "="*80)
print("STEP 1/8: CHECKING GITHUB TOKENS")
print("="*80)

results['tokens'] = run_cmd([sys.executable, "check_tokens.py"], "Token diagnostic", 60)

# Check report
if os.path.exists("token_report.json"):
    with open("token_report.json") as f:
        report = json.load(f)
    invalid = [r for r in report if r.get('status') != 'OK']
    if invalid:
        print(f"\n[WARNING] {len(invalid)} tokens need fixing!")
        print("You MUST fix tokens before downloading private repos:")
        print("  1. Go to https://github.com/settings/tokens")
        print("  2. Generate new Classic token for EACH account")
        print("  3. CHECK the 'repo' scope checkbox")
        print("  4. Update in GitHubDownloader app")
        print("\n  Then run: python check_tokens.py")
        results['tokens'] = False
    else:
        print("\n[OK] All tokens are valid!")
        results['tokens'] = True

# ============================================================================
# STEP 2: Analyze Current Repos (153 already downloaded)
# ============================================================================
print("\n" + "="*80)
print("STEP 2/8: ANALYZING EXISTING REPOSITORIES")
print("="*80)

if os.path.exists("repos"):
    repo_count = len([d for d in Path("repos").iterdir() if d.is_dir()])
    print(f"Found {repo_count} repositories")
    
    results['analyze'] = run_cmd(
        [sys.executable, "github_export_processor.py", "--input", "repos", "--output", "exports", "--analyze"],
        "Repository analysis",
        300
    )
else:
    print("[WARNING] No repos/ directory found")
    results['analyze'] = False

# ============================================================================
# STEP 3: Prepare AI Agent Starter Kit
# ============================================================================
print("\n" + "="*80)
print("STEP 3/8: PREPARING AI AGENT STARTER KIT")
print("="*80)

kit_dir = Path("ai-agent-starter-kit")
if kit_dir.exists():
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    package_name = "ai-agent-starter-kit-v1.0"
    package_dir = dist_dir / package_name
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    try:
        shutil.copytree(kit_dir, package_dir)
        
        # Create ZIP
        zip_base = dist_dir / package_name
        shutil.make_archive(str(zip_base), 'zip', str(package_dir))
        
        zip_path = dist_dir / f"{package_name}.zip"
        size_mb = zip_path.stat().st_size / (1024*1024)
        
        print(f"[OK] Product package created: {zip_path}")
        print(f"[OK] Size: {size_mb:.1f} MB")
        
        # Save product info
        product_info = {
            "name": "AI Agent Starter Kit",
            "version": "1.0.0",
            "package": str(zip_path),
            "size_mb": round(size_mb, 1),
            "created": datetime.now().isoformat(),
            "pricing": {"starter": 99, "pro": 299, "enterprise": 999}
        }
        with open(dist_dir / "product-info.json", "w") as f:
            json.dump(product_info, f, indent=2)
        
        results['product'] = True
    except Exception as e:
        print(f"[ERROR] Failed to create package: {e}")
        results['product'] = False
else:
    print("[WARNING] ai-agent-starter-kit/ not found")
    results['product'] = False

# ============================================================================
# STEP 4: Prepare Landing Page
# ============================================================================
print("\n" + "="*80)
print("STEP 4/8: PREPARING LANDING PAGE")
print("="*80)

deploy_dir = Path("deploy")
deploy_dir.mkdir(exist_ok=True)

landing = Path("ai-agent-starter-kit/marketing/landing-page.html")
if landing.exists():
    shutil.copy2(landing, deploy_dir / "index.html")
    print(f"[OK] Landing page ready: {deploy_dir}/index.html")
    results['landing'] = True
else:
    print("[WARNING] Landing page not found")
    results['landing'] = False

# ============================================================================
# STEP 5: Create Marketing Materials
# ============================================================================
print("\n" + "="*80)
print("STEP 5/8: CREATING MARKETING MATERIALS")
print("="*80)

marketing_dir = Path("marketing")
marketing_dir.mkdir(exist_ok=True)

materials = {
    "tweet.txt": """🚀 Just launched: AI Agent Starter Kit

Build production-ready AI agents in minutes:
✅ 10 agent frameworks
✅ 5 MCP servers  
✅ 100+ LLM models
✅ One-command deploy

From 53 curated open-source repos → packaged product

Get it now: [YOUR_GUMROAD_LINK]

#AI #MachineLearning #DeveloperTools""",

    "email.txt": """Subject: Launch: AI Agent Starter Kit ($99-299)

Hey,

Want to add AI to your projects without months of setup?

I built the AI Agent Starter Kit - everything you need:

✓ CrewAI, AutoGen, LangChain (pre-configured)
✓ LiteLLM proxy (100+ models)
✓ MCP servers for docs, DB, Git
✓ Docker deployment

Pricing:
• Starter: $99
• Pro: $299 (most popular)
• Enterprise: $999

[GET IT NOW - YOUR_LINK]

Questions? Just reply.

Best,
[Your Name]""",

    "reddit.txt": """[Showoff Saturday] AI Agent Starter Kit - From 53 repos to product

Built a complete AI agent platform from curated open-source repos:

**What's inside:**
- 10 agent frameworks
- 5 MCP server integrations  
- Universal LLM proxy
- Docker deployment

**Tech:** Python/FastAPI, Docker, Redis

**Pricing:** $99-299

Would love feedback! What else should I include?

[LINK]""",

    "producthunt.txt": """AI Agent Starter Kit

The complete platform for building production-ready AI agents. 

10 pre-configured frameworks, 5 MCP servers, universal LLM proxy.

From open-source to product in minutes.

$99-299 one-time. Lifetime updates.

#AI #DeveloperTools #OpenSource"""
}

for filename, content in materials.items():
    filepath = marketing_dir / filename
    if not filepath.exists():
        filepath.write_text(content, encoding='utf-8')
        print(f"[OK] Created {filename}")

results['marketing'] = True

# ============================================================================
# STEP 6: Generate Deployment Checklist
# ============================================================================
print("\n" + "="*80)
print("STEP 6/8: GENERATING DEPLOYMENT CHECKLIST")
print("="*80)

checklist = f"""# 🚀 DEPLOYMENT CHECKLIST
## Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## ⚡ IMMEDIATE ACTIONS (Do Today)

### 1. Fix GitHub Tokens (REQUIRED)
- [ ] Run: `python check_tokens.py`
- [ ] Go to https://github.com/settings/tokens for EACH account
- [ ] Generate new Classic token with 'repo' scope
- [ ] Update in GitHubDownloader app
- [ ] Re-run check_tokens.py to verify

### 2. Download All Repos
- [ ] Open GitHubDownloader.exe
- [ ] Click "All Accounts" button
- [ ] Wait for completion (1-2 hours)
- [ ] Verify 500+ repos downloaded

### 3. Set Up Payments
- [ ] Create Gumroad account: https://gumroad.com
- [ ] Connect PayPal or Stripe
- [ ] Create product listing:
  - Title: "AI Agent Starter Kit"
  - Price: $299 (Pro tier)
  - Description: Use README.md content
  - Cover image: Create or use placeholder

## 🌐 DEPLOY LANDING PAGE (Do This Week)

### Option 1: GitHub Pages (Free)
```bash
git init deploy
cd deploy
git add index.html
git commit -m "Initial commit"
# Push to gh-pages branch
```

### Option 2: Netlify (Free, Easiest)
1. Go to https://netlify.com
2. Drag `deploy/` folder to upload
3. Get instant URL
4. (Optional) Add custom domain

### Option 3: Vercel (Free)
```bash
npm i -g vercel
vercel deploy deploy/
```

## 📢 LAUNCH MARKETING (Do This Week)

### Day 1: Soft Launch
- [ ] Post tweet (see marketing/tweet.txt)
- [ ] Share on LinkedIn
- [ ] Post on personal social media

### Day 2: Community
- [ ] Post on Reddit r/webdev
- [ ] Post on Reddit r/MachineLearning
- [ ] Share in Discord communities

### Day 3: Product Hunt
- [ ] Submit to Product Hunt
- [ ] Prepare maker comment
- [ ] Share with email list

### Week 1: Content
- [ ] Write blog post about the kit
- [ ] Create video tutorial
- [ ] Post on Medium/Dev.to

## ☁️ SAAS DEPLOYMENT (Optional, Month 2)

### Railway (Easiest)
```bash
npm i -g @railway/cli
railway login
railway init
cd ai-agent-starter-kit
railway up
```

### Environment Variables
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LITELLM_MASTER_KEY=your-master-key
DATABASE_URL=postgresql://...
```

## 📊 POST-LAUNCH (Ongoing)

### Week 1
- [ ] Monitor sales daily
- [ ] Respond to all customer questions
- [ ] Fix any reported bugs
- [ ] Collect feedback

### Month 1
- [ ] Plan v1.1 features
- [ ] Build email list
- [ ] Create documentation site
- [ ] Set up analytics

### Month 3
- [ ] Launch SaaS tier
- [ ] Add affiliate program
- [ ] Explore partnerships
- [ ] Consider white-label deals

## 💰 REVENUE TARGETS

| Timeline | Conservative | Moderate | Aggressive |
|----------|--------------|----------|------------|
| Week 1 | $0-100 | $100-500 | $500-1000 |
| Month 1 | $500-1000 | $1000-3000 | $3000-5000 |
| Month 3 | $3000-5000 | $5000-15000 | $15000-30000 |
| Month 6 | $10000-20000 | $20000-50000 | $50000-100000 |

## 📁 FILE REFERENCE

| File | Purpose |
|------|---------|
| `dist/ai-agent-starter-kit-v1.0.zip` | **Main product package** |
| `deploy/index.html` | Landing page |
| `marketing/tweet.txt` | Twitter post |
| `marketing/email.txt` | Launch email |
| `marketing/reddit.txt` | Reddit post |
| `exports/analytics-report.md` | Repo analytics |
| `ai-agent-starter-kit/README.md` | Product docs |
| `DEPLOYMENT_CHECKLIST.md` | This file |

## 🆘 SUPPORT

If stuck:
1. Check `master_execution.log` for errors
2. Review `exports/analytics-report.md`
3. Open an issue on GitHub
4. Email: support@yourdomain.com

---

## ✅ QUICK START (5 Minutes)

```bash
# 1. Fix tokens
python check_tokens.py

# 2. Check everything is ready
ls dist/*.zip
ls deploy/index.html
ls marketing/

# 3. Upload to Gumroad
# 4. Deploy landing page
# 5. Post on social media
```

**You're ready to launch! 🚀**
"""

with open("DEPLOYMENT_CHECKLIST.md", "w", encoding='utf-8') as f:
    f.write(checklist)

print("[OK] Deployment checklist saved: DEPLOYMENT_CHECKLIST.md")
results['checklist'] = True

# ============================================================================
# STEP 7: Create Quick-Start Script
# ============================================================================
print("\n" + "="*80)
print("STEP 7/8: CREATING QUICK-START SCRIPT")
print("="*80)

quickstart = '''#!/usr/bin/env python3
"""
QUICK START - Deploy Everything in 5 Minutes
"""

import os
import sys
import webbrowser
from pathlib import Path

print("="*80)
print("AI AGENT STARTER KIT - QUICK DEPLOY".center(80))
print("="*80)
print()

# Check prerequisites
checks = {
    "Product Package": Path("dist/ai-agent-starter-kit-v1.0.zip").exists(),
    "Landing Page": Path("deploy/index.html").exists(),
    "Marketing": Path("marketing").exists(),
}

print("PREREQUISITES:")
for name, ok in checks.items():
    status = "✓" if ok else "✗"
    print(f"  [{status}] {name}")

if not all(checks.values()):
    print("\nSome items missing. Run: python proceed.py")
    sys.exit(1)

print("\n" + "="*80)
print("DEPLOY OPTIONS:")
print("="*80)
print()
print("1. OPEN LANDING PAGE (Local)")
print("   File: deploy/index.html")
print("   Action: Opening in browser...")
webbrowser.open("file://" + str(Path("deploy/index.html").absolute()))
print()
print("2. GUMROAD SETUP")
print("   URL: https://gumroad.com")
print("   Action: Upload dist/ai-agent-starter-kit-v1.0.zip")
print("   Price: $299 (Pro tier)")
print()
print("3. DEPLOY ONLINE")
print("   Options:")
print("   a) Netlify: Drag deploy/ folder to netlify.com")
print("   b) Vercel: Run 'vercel deploy'")
print("   c) GitHub Pages: Push deploy/ to gh-pages")
print()
print("4. MARKETING")
print("   Tweet: marketing/tweet.txt")
print("   Email: marketing/email.txt")
print("   Reddit: marketing/reddit.txt")
print()
print("="*80)
print()
input("Press ENTER to open Gumroad...")
webbrowser.open("https://gumroad.com")
'''

with open("quickstart.py", "w", encoding='utf-8') as f:
    f.write(quickstart)

print("[OK] Quick-start script created: quickstart.py")
results['quickstart'] = True

# ============================================================================
# STEP 8: Final Summary
# ============================================================================
print("\n" + "="*80)
print("STEP 8/8: FINAL SUMMARY")
print("="*80)

elapsed = (datetime.now() - start_time).total_seconds()
print(f"\nTotal time: {elapsed:.1f} seconds")
print()

print("RESULTS:")
print("-" * 60)
for name, result in results.items():
    status = "OK" if result else "REVIEW"
    print(f"  {name:20} {status}")

print()
print("="*80)
print("DELIVERABLES CREATED:")
print("="*80)

deliverables = [
    ("dist/ai-agent-starter-kit-v1.0.zip", "Product package"),
    ("deploy/index.html", "Landing page"),
    ("marketing/", "Marketing materials"),
    ("exports/analytics-report.md", "Repo analytics"),
    ("DEPLOYMENT_CHECKLIST.md", "Deployment guide"),
    ("quickstart.py", "Quick-start script"),
]

for path, desc in deliverables:
    exists = "OK" if os.path.exists(path) else "MISSING"
    print(f"  [{exists:8}] {desc:25} {path}")

print()
print("="*80)
print("NEXT ACTIONS:")
print("="*80)
print()
print("1. FIX TOKENS (if not done):")
print("   python check_tokens.py")
print()
print("2. DEPLOY LANDING PAGE:")
print("   python quickstart.py")
print("   OR drag deploy/ to netlify.com")
print()
print("3. UPLOAD TO GUMROAD:")
print("   - Product: dist/ai-agent-starter-kit-v1.0.zip")
print("   - Price: $299")
print()
print("4. START MARKETING:")
print("   - Tweet: marketing/tweet.txt")
print("   - Reddit: marketing/reddit.txt")
print("   - Email: marketing/email.txt")
print()
print("="*80)
print("READY TO LAUNCH!".center(80))
print("="*80)
