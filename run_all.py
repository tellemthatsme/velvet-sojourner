#!/usr/bin/env python3
"""
MASTER EXECUTION SCRIPT - Run Everything
Automates the complete pipeline from token fix to product deployment
"""

import os
import sys
import json
import time
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MasterExecutor:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        self.log_file = "master_execution.log"
        
    def log(self, message: str, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    
    def print_banner(self, text: str):
        print(f"\n{colors.BOLD}{colors.CYAN}{'='*80}{colors.END}")
        print(f"{colors.BOLD}{colors.CYAN}{text.center(80)}{colors.END}")
        print(f"{colors.BOLD}{colors.CYAN}{'='*80}{colors.END}\n")
    
    def run_command(self, cmd: list, description: str, timeout: int = 120) -> bool:
        """Run a command and log results"""
        self.log(f"Running: {description}")
        self.log(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                self.log(f"SUCCESS: {description}", "SUCCESS")
                if result.stdout:
                    # Log last 5 lines
                    lines = result.stdout.strip().split('\n')[-5:]
                    for line in lines:
                        if line.strip():
                            self.log(f"  > {line}")
                return True
            else:
                self.log(f"FAILED: {description}", "ERROR")
                if result.stderr:
                    self.log(f"Error: {result.stderr[:200]}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"TIMEOUT: {description} (exceeded {timeout}s)", "WARNING")
            return False
        except Exception as e:
            self.log(f"EXCEPTION: {str(e)}", "ERROR")
            return False
    
    def step1_check_tokens(self) -> bool:
        """Step 1: Check current token status"""
        self.print_banner("STEP 1: CHECKING GITHUB TOKENS")
        
        if not os.path.exists("check_tokens.py"):
            self.log("check_tokens.py not found!", "ERROR")
            return False
        
        success = self.run_command(
            [sys.executable, "check_tokens.py"],
            "Token diagnostic check",
            timeout=60
        )
        
        # Check results
        if os.path.exists("token_report.json"):
            try:
                with open("token_report.json", "r") as f:
                    report = json.load(f)
                
                invalid = [r for r in report if r.get("status") != "OK"]
                if invalid:
                    self.log(f"{len(invalid)} tokens need fixing!", "WARNING")
                    self.log("Run: python token_fix_wizard.py", "INFO")
                    self.log("Or manually update tokens at github.com/settings/tokens", "INFO")
                    return False
                else:
                    self.log("All tokens are valid!", "SUCCESS")
                    return True
            except:
                pass
        
        return success
    
    def step2_fix_tokens(self) -> bool:
        """Step 2: Interactive token fix"""
        self.print_banner("STEP 2: FIXING TOKENS")
        
        self.log("Opening token fix wizard...", "INFO")
        self.log("Follow the instructions to regenerate your tokens", "INFO")
        self.log("", "INFO")
        self.log("QUICK FIX STEPS:", "INFO")
        self.log("1. Go to https://github.com/settings/tokens", "INFO")
        self.log("2. Generate new Classic token for EACH account", "INFO")
        self.log("3. CHECK the 'repo' scope checkbox", "INFO")
        self.log("4. Copy token and update in GitHubDownloader", "INFO")
        self.log("", "INFO")
        
        # Run wizard
        if os.path.exists("token_fix_wizard.py"):
            self.run_command(
                [sys.executable, "token_fix_wizard.py"],
                "Token fix wizard",
                timeout=300
            )
        
        input("\nPress ENTER after you've fixed all tokens...")
        
        # Re-check
        return self.step1_check_tokens()
    
    def step3_download_repos(self) -> bool:
        """Step 3: Download all repositories"""
        self.print_banner("STEP 3: DOWNLOADING REPOSITORIES")
        
        self.log("To download all repos:", "INFO")
        self.log("1. Open GitHubDownloader.exe", "INFO")
        self.log("2. Go to the 'Download' tab", "INFO")
        self.log("3. Click 'All Accounts' button", "INFO")
        self.log("4. Wait for completion (may take 1-2 hours)", "INFO")
        self.log("", "INFO")
        
        response = input("Have you downloaded all repos? (y/n): ").strip().lower()
        
        if response == 'y':
            # Count repos
            repos_dir = Path("repos")
            if repos_dir.exists():
                count = len([d for d in repos_dir.iterdir() if d.is_dir()])
                self.log(f"Found {count} repositories", "SUCCESS")
                
                if count < 200:
                    self.log(f"WARNING: Only {count} repos found. Expected 500+", "WARNING")
                    self.log("You may need to fix tokens first!", "WARNING")
                    return False
                return True
            else:
                self.log("repos/ directory not found!", "ERROR")
                return False
        else:
            self.log("Please download repos first, then re-run this script", "INFO")
            return False
    
    def step4_analyze_repos(self) -> bool:
        """Step 4: Analyze and categorize repositories"""
        self.print_banner("STEP 4: ANALYZING REPOSITORIES")
        
        if not os.path.exists("github_export_processor.py"):
            self.log("github_export_processor.py not found!", "ERROR")
            return False
        
        # Run analyzer (quick mode)
        success = self.run_command(
            [sys.executable, "github_export_processor.py", "--input", "repos", "--output", "exports", "--analyze"],
            "Repository analysis",
            timeout=300
        )
        
        if success and os.path.exists("exports/analytics-report.json"):
            try:
                with open("exports/analytics-report.json", "r") as f:
                    report = json.load(f)
                
                self.log(f"Analysis complete!", "SUCCESS")
                self.log(f"Total repos: {report.get('total_repos', 0)}", "INFO")
                self.log(f"Total size: {report.get('total_size_mb', 0)} MB", "INFO")
                self.log(f"Export ready: {report.get('export_ready', 0)}", "INFO")
                
                return True
            except Exception as e:
                self.log(f"Error reading report: {e}", "ERROR")
        
        return success
    
    def step5_create_bundles(self) -> bool:
        """Step 5: Create product bundles"""
        self.print_banner("STEP 5: CREATING PRODUCT BUNDLES")
        
        self.log("Creating export bundles...", "INFO")
        self.log("This may take several minutes for large repositories", "INFO")
        
        # Create output directory
        os.makedirs("products", exist_ok=True)
        
        # Run bundle creation (might timeout on large repos, that's OK)
        try:
            subprocess.run(
                [sys.executable, "github_export_processor.py", "--input", "repos", "--output", "products"],
                timeout=600,
                capture_output=True
            )
        except subprocess.TimeoutExpired:
            self.log("Bundle creation timed out (expected for large repos)", "WARNING")
            self.log("Manual bundling may be needed for some products", "INFO")
        
        # Check what was created
        products_dir = Path("products")
        if products_dir.exists():
            bundles = list(products_dir.glob("*.zip"))
            if bundles:
                self.log(f"Created {len(bundles)} product bundles:", "SUCCESS")
                for bundle in bundles:
                    size = bundle.stat().st_size / (1024*1024)
                    self.log(f"  - {bundle.name} ({size:.1f} MB)", "INFO")
                return True
            else:
                self.log("No bundles created yet", "WARNING")
                self.log("You can create them manually with: python github_export_processor.py", "INFO")
        
        return True  # Continue even if bundles aren't ready
    
    def step6_setup_product(self) -> bool:
        """Step 6: Prepare AI Agent Starter Kit for sale"""
        self.print_banner("STEP 6: SETTING UP AI AGENT STARTER KIT")
        
        kit_dir = Path("ai-agent-starter-kit")
        if not kit_dir.exists():
            self.log("ai-agent-starter-kit/ not found!", "ERROR")
            return False
        
        # Create distribution package
        self.log("Creating product package...", "INFO")
        
        try:
            dist_dir = Path("dist")
            dist_dir.mkdir(exist_ok=True)
            
            package_name = "ai-agent-starter-kit-v1.0"
            package_dir = dist_dir / package_name
            
            if package_dir.exists():
                shutil.rmtree(package_dir)
            
            shutil.copytree(kit_dir, package_dir)
            
            # Create ZIP
            zip_path = dist_dir / f"{package_name}.zip"
            shutil.make_archive(
                str(dist_dir / package_name),
                'zip',
                str(package_dir)
            )
            
            size = zip_path.stat().st_size / (1024*1024)
            self.log(f"Product package created: {zip_path}", "SUCCESS")
            self.log(f"Size: {size:.1f} MB", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"Error creating package: {e}", "ERROR")
            return False
    
    def step7_prepare_marketing(self) -> bool:
        """Step 7: Prepare marketing materials"""
        self.print_banner("STEP 7: PREPARING MARKETING MATERIALS")
        
        # Create deploy directory with landing page
        deploy_dir = Path("deploy")
        deploy_dir.mkdir(exist_ok=True)
        
        landing_page = Path("ai-agent-starter-kit/marketing/landing-page.html")
        if landing_page.exists():
            shutil.copy2(landing_page, deploy_dir / "index.html")
            self.log(f"Landing page copied to {deploy_dir}/index.html", "SUCCESS")
        
        # Generate quick marketing snippets
        marketing_dir = Path("marketing")
        marketing_dir.mkdir(exist_ok=True)
        
        snippets = {
            "tweet.txt": """🚀 Just launched: AI Agent Starter Kit

Build production-ready AI agents in minutes:
✅ 10 agent frameworks
✅ 5 MCP servers  
✅ 100+ LLM models
✅ One-command deploy

From 53 curated open-source repos → packaged product

Get it now: [YOUR_LINK]

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

[LINK]"""
        }
        
        for filename, content in snippets.items():
            filepath = marketing_dir / filename
            if not filepath.exists():
                filepath.write_text(content)
                self.log(f"Created {filepath}", "SUCCESS")
        
        self.log("Marketing materials ready!", "SUCCESS")
        return True
    
    def step8_generate_checklist(self) -> bool:
        """Step 8: Generate final deployment checklist"""
        self.print_banner("STEP 8: GENERATING DEPLOYMENT CHECKLIST")
        
        checklist = f"""# DEPLOYMENT CHECKLIST
## Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Pre-Launch ✅
- [ ] GitHub tokens fixed (run: python check_tokens.py)
- [ ] All repos downloaded (500+ expected)
- [ ] Products created in dist/
- [ ] Landing page ready in deploy/
- [ ] Marketing materials in marketing/

## Payment Setup 💰
- [ ] Create Gumroad account (gumroad.com)
- [ ] Set up Stripe account (stripe.com)
- [ ] Create product listings:
  - [ ] AI Agent Starter Kit - $299
  - [ ] Category bundles - $99-149
- [ ] Set up PayPal (optional)

## Deploy Landing Page 🌐
- [ ] Option 1: GitHub Pages
  - Create repo: yourusername.github.io
  - Copy deploy/index.html to repo
  - Enable GitHub Pages in settings
- [ ] Option 2: Netlify
  - Drag deploy/ folder to netlify.com
  - Get instant URL
- [ ] Option 3: Vercel
  - Run: vercel deploy

## Launch Marketing 📢
- [ ] Post tweet (see marketing/tweet.txt)
- [ ] Share on LinkedIn
- [ ] Post on Reddit r/webdev, r/MachineLearning
- [ ] Send email to list (see marketing/email.txt)
- [ ] Submit to Product Hunt

## SaaS Deployment (Optional) ☁️
- [ ] Sign up for Railway (railway.app)
- [ ] Deploy with: railway up
- [ ] Add environment variables
- [ ] Set up custom domain
- [ ] Configure Stripe billing

## Post-Launch 📊
- [ ] Monitor sales daily
- [ ] Respond to customer questions
- [ ] Collect feedback
- [ ] Plan v1.1 update
- [ ] Build email list

## Revenue Targets 🎯
- [ ] Week 1: $100-500
- [ ] Month 1: $500-2,000
- [ ] Month 3: $5,000-10,000
- [ ] Month 6: $15,000-35,000

---

## Quick Links
- Product Package: dist/ai-agent-starter-kit-v1.0.zip
- Landing Page: deploy/index.html
- Analytics: exports/analytics-report.md
- Marketing: marketing/

## Support
- Documentation: ai-agent-starter-kit/docs/
- Gateway API: ai-agent-starter-kit/gateway/
- Docker Config: ai-agent-starter-kit/docker-compose.yml

---

**You're ready to launch! 🚀**
"""
        
        with open("DEPLOYMENT_CHECKLIST.md", "w") as f:
            f.write(checklist)
        
        self.log("Deployment checklist saved: DEPLOYMENT_CHECKLIST.md", "SUCCESS")
        return True
    
    def run_all(self):
        """Run complete execution pipeline"""
        self.print_banner("MASTER EXECUTION - COMPLETE AUTOMATION")
        
        self.log("Starting complete execution pipeline", "INFO")
        self.log(f"Working directory: {os.getcwd()}", "INFO")
        self.log(f"Python: {sys.executable}", "INFO")
        self.log("", "INFO")
        
        # Execute steps
        steps = [
            ("Token Check", self.step1_check_tokens),
            ("Token Fix", self.step2_fix_tokens),
            ("Download Repos", self.step3_download_repos),
            ("Analyze Repos", self.step4_analyze_repos),
            ("Create Bundles", self.step5_create_bundles),
            ("Setup Product", self.step6_setup_product),
            ("Prepare Marketing", self.step7_prepare_marketing),
            ("Generate Checklist", self.step8_generate_checklist),
        ]
        
        for i, (name, step_func) in enumerate(steps, 1):
            self.log(f"\n{'='*60}", "INFO")
            self.log(f"STEP {i}/{len(steps)}: {name}", "INFO")
            self.log(f"{'='*60}", "INFO")
            
            try:
                result = step_func()
                self.results[name] = result
                
                if not result:
                    self.log(f"Step {i} ({name}) did not complete successfully", "WARNING")
                    response = input("\nContinue anyway? (y/n): ").strip().lower()
                    if response != 'y':
                        self.log("Execution stopped by user", "INFO")
                        break
            except Exception as e:
                self.log(f"Error in step {i}: {str(e)}", "ERROR")
                self.results[name] = False
        
        # Final summary
        self.print_summary()
    
    def print_summary(self):
        """Print execution summary"""
        self.print_banner("EXECUTION COMPLETE")
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        self.log(f"Total time: {minutes}m {seconds}s", "INFO")
        self.log(f"", "INFO")
        
        # Results table
        self.log("STEP RESULTS:", "INFO")
        self.log("-" * 60, "INFO")
        
        for name, result in self.results.items():
            status = f"{colors.GREEN}PASS{colors.END}" if result else f"{colors.YELLOW}REVIEW{colors.END}"
            self.log(f"  {name:20} {status}", "INFO")
        
        self.log("", "INFO")
        
        # Next actions
        passed = sum(1 for r in self.results.values() if r)
        total = len(self.results)
        
        self.log(f"Completed: {passed}/{total} steps", "INFO")
        self.log("", "INFO")
        
        self.log("NEXT ACTIONS:", "INFO")
        self.log("-" * 60, "INFO")
        
        if not self.results.get("Token Check", False):
            self.log("1. PRIORITY: Fix your GitHub tokens", "WARNING")
            self.log("   Run: python token_fix_wizard.py", "INFO")
        
        if not self.results.get("Download Repos", False):
            self.log("2. Download all repos with GitHubDownloader", "INFO")
            self.log("   Open: GitHubDownloader.exe", "INFO")
        
        self.log("3. Review DEPLOYMENT_CHECKLIST.md", "INFO")
        self.log("4. Set up Gumroad account", "INFO")
        self.log("5. Deploy landing page from deploy/", "INFO")
        self.log("6. Start marketing!", "INFO")
        
        self.log("", "INFO")
        self.log(f"Full log: {self.log_file}", "INFO")
        self.log("", "INFO")
        self.log(f"{colors.BOLD}{colors.GREEN}Ready to launch! 🚀{colors.END}", "INFO")


def main():
    executor = MasterExecutor()
    executor.run_all()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{colors.YELLOW}Execution cancelled.{colors.END}")
        sys.exit(0)
