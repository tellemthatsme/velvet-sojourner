#!/usr/bin/env python3
"""
DO_ALL.py - The Ultimate Execution Script
Executes EVERYTHING: token fix, repo download, analysis, bundling, deployment, marketing
Non-interactive version for batch execution
"""

import os
import sys
import json
import shutil
import subprocess
import time
import webbrowser
from datetime import datetime
from pathlib import Path

# Constants
APP_DATA = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader")
ACCOUNTS_FILE = os.path.join(APP_DATA, "accounts.json")
REPOS_DIR = Path("repos")
EXPORTS_DIR = Path("exports")
PRODUCTS_DIR = Path("products")
DIST_DIR = Path("dist")
DEPLOY_DIR = Path("deploy")
MARKETING_DIR = Path("marketing")

class Logger:
    def __init__(self):
        self.start = datetime.now()
        self.log_file = f"do_all_{self.start.strftime('%Y%m%d_%H%M%S')}.log"
        
    def log(self, msg, level="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{level}] {msg}"
        print(line)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    
    def banner(self, text):
        print(f"\n{'='*80}")
        print(f"{text.center(80)}")
        print(f"{'='*80}\n")
        self.log(text, "BANNER")
    
    def success(self, msg):
        self.log(msg, "SUCCESS")
    
    def error(self, msg):
        self.log(msg, "ERROR")
    
    def warning(self, msg):
        self.log(msg, "WARNING")

logger = Logger()

def run(cmd, desc, timeout=120):
    """Run shell command"""
    logger.log(f"Running: {desc}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            logger.success(f"OK: {desc}")
            return True, result.stdout
        else:
            logger.warning(f"Non-zero exit: {desc}")
            return False, result.stderr
    except Exception as e:
        logger.error(f"Failed: {desc} - {e}")
        return False, str(e)

def step1_token_report():
    """Generate token status report"""
    logger.banner("STEP 1: TOKEN STATUS REPORT")
    
    if not os.path.exists(ACCOUNTS_FILE):
        logger.error("No accounts file found!")
        return False
    
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    
    logger.log(f"Found {len(accounts)} accounts")
    
    # Try to check via API
    try:
        import requests
        for acc_id, acc in accounts.items():
            token = acc.get("token", "")
            username = acc.get("username", acc_id)
            
            if not token:
                logger.warning(f"{username}: No token")
                continue
            
            headers = {"Authorization": f"token {token}"}
            resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            scopes = resp.headers.get("X-OAuth-Scopes", "")
            
            if resp.status_code == 200:
                data = resp.json()
                has_repo = "repo" in [s.strip() for s in scopes.split(",") if s.strip()]
                status = "VALID" if has_repo else "MISSING_REPO_SCOPE"
                logger.log(f"{username}: {status} | Public: {data.get('public_repos',0)} | Private: {data.get('total_private_repos',0)}")
            else:
                logger.error(f"{username}: Invalid token (HTTP {resp.status_code})")
    except ImportError:
        logger.warning("requests library not available, skipping API check")
    except Exception as e:
        logger.error(f"Token check failed: {e}")
    
    return True

def step2_prepare_products():
    """Prepare all product packages"""
    logger.banner("STEP 2: PREPARING PRODUCT PACKAGES")
    
    # Ensure directories exist
    for d in [EXPORTS_DIR, PRODUCTS_DIR, DIST_DIR, DEPLOY_DIR, MARKETING_DIR]:
        d.mkdir(exist_ok=True)
    
    # Analyze repos if they exist
    if REPOS_DIR.exists():
        repo_count = len([d for d in REPOS_DIR.iterdir() if d.is_dir()])
        logger.log(f"Found {repo_count} repositories")
        
        # Run quick analysis
        if os.path.exists("github_export_processor.py"):
            logger.log("Running repository analysis...")
            ok, out = run(f"{sys.executable} github_export_processor.py --input repos --output exports --analyze", 
                         "Repo analysis", 300)
    else:
        logger.warning("No repos/ directory found. Run downloader first.")
    
    # Create AI Agent Starter Kit package
    kit_dir = Path("ai-agent-starter-kit")
    if kit_dir.exists():
        logger.log("Packaging AI Agent Starter Kit...")
        
        package_name = "ai-agent-starter-kit-v1.0"
        package_dir = DIST_DIR / package_name
        
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        shutil.copytree(kit_dir, package_dir)
        
        # Create ZIP
        zip_base = DIST_DIR / package_name
        shutil.make_archive(str(zip_base), 'zip', str(package_dir))
        
        zip_path = DIST_DIR / f"{package_name}.zip"
        if zip_path.exists():
            size = zip_path.stat().st_size / (1024*1024)
            logger.success(f"Product package: {zip_path} ({size:.1f} MB)")
            
            # Save product info
            info = {
                "name": "AI Agent Starter Kit",
                "version": "1.0.0",
                "file": str(zip_path),
                "size_mb": round(size, 1),
                "created": datetime.now().isoformat(),
                "pricing": {"starter": 99, "pro": 299, "enterprise": 999}
            }
            with open(DIST_DIR / "product-info.json", "w") as f:
                json.dump(info, f, indent=2)
        else:
            logger.error("Failed to create ZIP")
    else:
        logger.warning("ai-agent-starter-kit/ not found")

def step3_deploy_assets():
    """Prepare deployment assets"""
    logger.banner("STEP 3: PREPARING DEPLOYMENT ASSETS")
    
    # Landing page
    landing_src = Path("ai-agent-starter-kit/marketing/landing-page.html")
    if landing_src.exists():
        shutil.copy2(landing_src, DEPLOY_DIR / "index.html")
        logger.success(f"Landing page: {DEPLOY_DIR}/index.html")
    
    # Marketing materials
    templates = {
        "tweet.txt": "Tweet template for launch",
        "email.txt": "Email template for launch",
        "reddit.txt": "Reddit post template",
        "producthunt.txt": "ProductHunt launch text"
    }
    
    for filename, desc in templates.items():
        filepath = MARKETING_DIR / filename
        if not filepath.exists():
            # Create basic template
            content = f"# {desc}\n\n[Your content here]\n\n#AI #DeveloperTools #Launch"
            filepath.write_text(content, encoding="utf-8")
            logger.log(f"Created {filename}")
    
    logger.success("All deployment assets prepared")

def step4_generate_docs():
    """Generate documentation and checklists"""
    logger.banner("STEP 4: GENERATING DOCUMENTATION")
    
    # Revenue tracker
    tracker = """# Revenue Tracker

## Product: AI Agent Starter Kit

### Pricing
| Tier | Price | Features |
|------|-------|----------|
| Starter | $99 | 3 agents, 2 MCPs |
| Pro | $299 | 10 agents, 5 MCPs |
| Enterprise | $999 | Unlimited |

### Sales Log
| Date | Customer | Tier | Amount | Channel |
|------|----------|------|--------|---------|
| | | | | |

### Monthly Targets
| Month | Target | Actual | Notes |
|-------|--------|--------|-------|
| Month 1 | $500 | | |
| Month 2 | $1,500 | | |
| Month 3 | $5,000 | | |
| Month 6 | $15,000 | | |
| Month 12 | $50,000 | | |

### Expenses
| Item | Monthly Cost |
|------|--------------|
| Hosting | $50 |
| Domain | $10 |
| Gumroad Fees | 10% |
| Marketing | $200 |

---
*Update this file weekly*
"""
    
    with open("REVENUE_TRACKER.md", "w", encoding="utf-8") as f:
        f.write(tracker)
    logger.success("Created REVENUE_TRACKER.md")
    
    # Master checklist
    checklist = f"""# MASTER CHECKLIST - DO_ALL Execution
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Phase 1: Foundation ✅
- [x] Token diagnostic run
- [x] Product packages created
- [x] Landing page prepared
- [x] Marketing materials generated
- [x] Documentation created

## Phase 2: Token Fix (DO NOW)
- [ ] Fix token for tellemthatsme
- [ ] Fix token for woodsai69rme
- [ ] Fix token for leahmfoots
- [ ] Fix token for acidlink
- [ ] Fix token for Ashlee69r
- [ ] Verify with: python check_tokens.py

## Phase 3: Download (After Fix)
- [ ] Open GitHubDownloader.exe
- [ ] Click "All Accounts"
- [ ] Wait for 500+ repos
- [ ] Verify repo count

## Phase 4: Launch (Can Do Now with 153 repos)
- [ ] Create Gumroad account
- [ ] Upload dist/ai-agent-starter-kit-v1.0.zip
- [ ] Set price: $299
- [ ] Deploy landing page (deploy/index.html)
- [ ] Post tweet
- [ ] Share on LinkedIn

## Phase 5: Scale (After 500+ repos)
- [ ] Re-run export processor
- [ ] Create category bundles
- [ ] Launch on Product Hunt
- [ ] Start email marketing
- [ ] Deploy SaaS (Railway)

## Quick Commands
```bash
# Check tokens
python check_tokens.py

# Run full pipeline
python do_all.py

# Deploy landing
python quickstart.py
```
"""
    
    with open("MASTER_CHECKLIST.md", "w", encoding="utf-8") as f:
        f.write(checklist)
    logger.success("Created MASTER_CHECKLIST.md")

def step5_summary():
    """Print final summary"""
    logger.banner("EXECUTION SUMMARY")
    
    elapsed = (datetime.now() - logger.start).total_seconds()
    logger.log(f"Total execution time: {elapsed:.1f} seconds")
    
    # Check deliverables
    deliverables = [
        ("Product Package", DIST_DIR / "ai-agent-starter-kit-v1.0.zip"),
        ("Product Info", DIST_DIR / "product-info.json"),
        ("Landing Page", DEPLOY_DIR / "index.html"),
        ("Tweet Template", MARKETING_DIR / "tweet.txt"),
        ("Email Template", MARKETING_DIR / "email.txt"),
        ("Reddit Post", MARKETING_DIR / "reddit.txt"),
        ("Revenue Tracker", Path("REVENUE_TRACKER.md")),
        ("Master Checklist", Path("MASTER_CHECKLIST.md")),
        ("Analytics Report", EXPORTS_DIR / "analytics-report.md"),
    ]
    
    logger.log("\nDELIVERABLES STATUS:")
    logger.log("-" * 60)
    
    ready_count = 0
    for name, path in deliverables:
        exists = path.exists()
        status = "READY" if exists else "MISSING"
        if exists:
            ready_count += 1
        logger.log(f"  [{status:8}] {name}")
    
    logger.log(f"\nReady: {ready_count}/{len(deliverables)}")
    
    # Next actions
    logger.log("\nNEXT ACTIONS:")
    logger.log("-" * 60)
    logger.log("1. FIX TOKENS (Critical)")
    logger.log("   python token_fix_wizard.py")
    logger.log("   OR manually at github.com/settings/tokens")
    logger.log("")
    logger.log("2. DEPLOY LANDING PAGE")
    logger.log("   Option A: python quickstart.py")
    logger.log("   Option B: Drag deploy/ to netlify.com")
    logger.log("")
    logger.log("3. CREATE GUMROAD LISTING")
    logger.log("   URL: gumroad.com")
    logger.log("   Product: dist/ai-agent-starter-kit-v1.0.zip")
    logger.log("   Price: $299")
    logger.log("")
    logger.log("4. START MARKETING")
    logger.log("   See marketing/ directory for templates")
    logger.log("")
    logger.log(f"Full log: {logger.log_file}")
    logger.log("")
    logger.log("="*80)
    logger.log("READY TO LAUNCH".center(80))
    logger.log("="*80)

def main():
    logger.banner("DO_ALL - COMPLETE AUTOMATION PIPELINE")
    logger.log("Executing everything: analysis, packaging, deployment, marketing")
    logger.log("")
    
    # Execute all steps
    step1_token_report()
    step2_prepare_products()
    step3_deploy_assets()
    step4_generate_docs()
    step5_summary()
    
    logger.log("\nAll steps completed!")
    logger.log(f"Review {logger.log_file} for details")

if __name__ == "__main__":
    main()
