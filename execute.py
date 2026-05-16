#!/usr/bin/env python3
"""
EXECUTE.PY - Master Execution Script
Run this AFTER fixing your GitHub tokens to automate everything else
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class Executor:
    def __init__(self):
        self.config = {
            "accounts_file": os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader", "accounts.json"),
            "repos_dir": "repos",
            "products_dir": "ai-agent-starter-kit",
            "log_file": "execution.log"
        }
        self.results = {}
        
    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.config["log_file"], "a") as f:
            f.write(log_msg + "\n")
    
    def print_header(self, text: str):
        print(f"\n{colors.BOLD}{colors.CYAN}{'='*80}{colors.END}")
        print(f"{colors.BOLD}{colors.CYAN}{text.center(80)}{colors.END}")
        print(f"{colors.BOLD}{colors.CYAN}{'='*80}{colors.END}\n")
    
    def step1_verify_tokens(self) -> bool:
        """Step 1: Verify all tokens have proper scopes"""
        self.print_header("STEP 1: VERIFYING GITHUB TOKENS")
        
        if not os.path.exists(self.config["accounts_file"]):
            self.log(f"{colors.RED}ERROR: Accounts file not found!{colors.END}")
            self.log(f"Expected: {self.config['accounts_file']}")
            return False
        
        try:
            import requests
            with open(self.config["accounts_file"], "r") as f:
                accounts = json.load(f)
            
            all_valid = True
            for acc_id, acc_data in accounts.items():
                token = acc_data.get("token", "")
                username = acc_data.get("username", acc_id)
                
                if not token:
                    self.log(f"{colors.YELLOW}⚠ No token for {username}{colors.END}")
                    all_valid = False
                    continue
                
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
                scopes = resp.headers.get("X-OAuth-Scopes", "").split(", ")
                scopes = [s for s in scopes if s]
                
                if resp.status_code == 200 and "repo" in scopes:
                    user_data = resp.json()
                    public = user_data.get("public_repos", 0)
                    private = user_data.get("total_private_repos", 0)
                    self.log(f"{colors.GREEN}✓ {username}: VALID - Public: {public}, Private: {private}{colors.END}")
                else:
                    self.log(f"{colors.RED}✗ {username}: INVALID - Scopes: {scopes or 'NONE'}{colors.END}")
                    all_valid = False
            
            if not all_valid:
                self.log(f"\n{colors.RED}SOME TOKENS ARE INVALID!{colors.END}")
                self.log(f"Run: python token_fix_wizard.py")
                self.log(f"Then regenerate tokens with 'repo' scope at https://github.com/settings/tokens")
                return False
            
            self.log(f"{colors.GREEN}All tokens valid! Proceeding...{colors.END}")
            return True
            
        except Exception as e:
            self.log(f"{colors.RED}ERROR: {str(e)}{colors.END}")
            return False
    
    def step2_rebuild_inventory(self) -> bool:
        """Step 2: Re-scan all repos and rebuild inventory"""
        self.print_header("STEP 2: REBUILDING REPOSITORY INVENTORY")
        
        if not os.path.exists(self.config["repos_dir"]):
            self.log(f"{colors.RED}ERROR: Repos directory not found: {self.config['repos_dir']}{colors.END}")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, "analyze_monetization.py", self.config["repos_dir"]],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log(f"{colors.GREEN}✓ Inventory rebuilt successfully{colors.END}")
                if os.path.exists("monetization_report.json"):
                    with open("monetization_report.json", "r") as f:
                        report = json.load(f)
                    self.log(f"Total repos: {report.get('total_repos', 0)}")
                    self.log(f"Total size: {report.get('total_size_mb', 0)} MB")
                return True
            else:
                self.log(f"{colors.RED}✗ Failed to rebuild inventory{colors.END}")
                self.log(result.stderr)
                return False
                
        except Exception as e:
            self.log(f"{colors.RED}ERROR: {str(e)}{colors.END}")
            return False
    
    def step3_prepare_product(self) -> bool:
        """Step 3: Prepare AI Agent Starter Kit for distribution"""
        self.print_header("STEP 3: PREPARING AI AGENT STARTER KIT")
        
        product_dir = self.config["products_dir"]
        if not os.path.exists(product_dir):
            self.log(f"{colors.RED}ERROR: Product directory not found: {product_dir}{colors.END}")
            return False
        
        try:
            # Create distribution package
            dist_dir = "dist"
            os.makedirs(dist_dir, exist_ok=True)
            
            # Build the product package
            self.log("Building product package...")
            
            # Copy essential files
            import shutil
            package_name = "ai-agent-starter-kit-v1.0"
            package_dir = os.path.join(dist_dir, package_name)
            
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)
            
            shutil.copytree(product_dir, package_dir)
            
            # Create ZIP
            zip_path = os.path.join(dist_dir, f"{package_name}.zip")
            shutil.make_archive(
                os.path.join(dist_dir, package_name),
                'zip',
                package_dir
            )
            
            self.log(f"{colors.GREEN}✓ Product package created: {zip_path}{colors.END}")
            self.log(f"Size: {os.path.getsize(zip_path) / (1024*1024):.1f} MB")
            
            # Generate product info
            product_info = {
                "name": "AI Agent Starter Kit",
                "version": "1.0.0",
                "package": zip_path,
                "size_mb": round(os.path.getsize(zip_path) / (1024*1024), 1),
                "created": datetime.now().isoformat(),
                "pricing": {
                    "starter": 99,
                    "pro": 299,
                    "enterprise": 999
                }
            }
            
            with open(os.path.join(dist_dir, "product-info.json"), "w") as f:
                json.dump(product_info, f, indent=2)
            
            self.log(f"{colors.GREEN}✓ Product info saved{colors.END}")
            return True
            
        except Exception as e:
            self.log(f"{colors.RED}ERROR: {str(e)}{colors.END}")
            return False
    
    def step4_deploy_landing_page(self) -> bool:
        """Step 4: Prepare landing page for deployment"""
        self.print_header("STEP 4: PREPARING LANDING PAGE")
        
        landing_page = os.path.join(self.config["products_dir"], "marketing", "landing-page.html")
        if not os.path.exists(landing_page):
            self.log(f"{colors.RED}ERROR: Landing page not found{colors.END}")
            return False
        
        try:
            # Copy to deploy directory
            deploy_dir = "deploy"
            os.makedirs(deploy_dir, exist_ok=True)
            
            import shutil
            index_path = os.path.join(deploy_dir, "index.html")
            shutil.copy2(landing_page, index_path)
            
            self.log(f"{colors.GREEN}✓ Landing page ready: {index_path}{colors.END}")
            self.log(f"\nDeploy options:")
            self.log(f"  1. GitHub Pages: Copy {deploy_dir} to gh-pages branch")
            self.log(f"  2. Netlify: Drag {deploy_dir} folder to netlify.com")
            self.log(f"  3. Vercel: Run 'vercel {deploy_dir}'")
            self.log(f"  4. Local: Open {index_path} in browser")
            
            return True
            
        except Exception as e:
            self.log(f"{colors.RED}ERROR: {str(e)}{colors.END}")
            return False
    
    def step5_generate_marketing(self) -> bool:
        """Step 5: Generate marketing materials"""
        self.print_header("STEP 5: GENERATING MARKETING MATERIALS")
        
        try:
            marketing_dir = "marketing"
            os.makedirs(marketing_dir, exist_ok=True)
            
            # Generate tweet thread
            tweet_thread = """🚀 Just launched: AI Agent Starter Kit

The complete platform for building production-ready AI agents:

✅ 10 pre-configured agent frameworks
✅ 5 MCP server integrations  
✅ Universal LLM proxy (100+ models)
✅ One-command deployment

From 53 curated open-source repos → packaged product

Perfect for developers who want to add AI capabilities FAST.

Thread 🧵👇

1/ What's inside?

• CrewAI multi-agent system
• AutoGen conversational agents
• LangChain toolkit
• LiteLLM universal proxy
• Aider coding assistant
• And 5 more...

Everything pre-configured and tested.

2/ MCP Servers included:

• Context7 documentation
• Supabase database
• Git operations
• FastAPI bridge
• Playwright browser

Connect your agents to anything.

3/ Deployment options:

• Docker Compose (5 min setup)
• Railway (one-click)
• Vercel (serverless)
• Self-hosted

Your choice. Full control.

4/ Pricing:

• Starter: $99 (3 agents, 2 MCPs)
• Pro: $299 (10 agents, 5 MCPs) ⭐ Popular
• Enterprise: $999 (unlimited everything)

Lifetime updates included.

5/ Use cases:

→ Build AI customer support
→ Create autonomous research agents
→ Deploy coding assistants
→ Launch AI-powered features
→ Start an AI SaaS

All from one kit.

Get started: [LINK]

#AI #MachineLearning #DeveloperTools
"""
            
            with open(os.path.join(marketing_dir, "tweet-thread.txt"), "w") as f:
                f.write(tweet_thread)
            
            # Generate email template
            email = """Subject: Launch: AI Agent Starter Kit (Build AI Agents in 5 Minutes)

Hey [Name],

Want to add AI capabilities to your projects without spending months on setup?

I just launched the AI Agent Starter Kit - a complete platform with 10+ production-ready agent frameworks, MCP servers, and deployment configs.

What's included:
✓ CrewAI, AutoGen, LangChain (pre-configured)
✓ LiteLLM proxy (access 100+ models)
✓ 5 MCP server integrations
✓ Docker Compose deployment
✓ API gateway with auth

Perfect for:
→ Developers building AI features
→ Startups launching AI products
→ Teams automating workflows

Pricing:
• Starter: $99
• Pro: $299 (most popular)
• Enterprise: $999

All plans include lifetime updates.

Learn more: [LINK]

Questions? Just reply to this email.

Best,
[Your Name]
"""
            
            with open(os.path.join(marketing_dir, "email-launch.txt"), "w") as f:
                f.write(email)
            
            # Generate Reddit post
            reddit = """[Showoff Saturday] I built an AI Agent Starter Kit from 53 open-source repos

Hey r/webdev and r/MachineLearning,

Over the past few weeks I've been curating and packaging the best open-source AI agent frameworks into a complete starter kit.

**What's inside:**
- 10 agent frameworks (CrewAI, AutoGen, LangChain, etc.)
- 5 MCP server integrations
- Universal LLM proxy (100+ models via LiteLLM)
- Docker Compose deployment
- FastAPI gateway

**The goal:** Help developers deploy AI agents in minutes instead of months.

**Tech stack:**
- Python/FastAPI for the gateway
- Docker for deployment
- Redis for caching
- PostgreSQL for persistence

**Pricing:**
- Starter: $99
- Pro: $299 (includes all frameworks)
- Enterprise: $999 (custom development)

Would love your feedback! What other agent frameworks should I include?

[LINK]
"""
            
            with open(os.path.join(marketing_dir, "reddit-post.txt"), "w") as f:
                f.write(reddit)
            
            self.log(f"{colors.GREEN}✓ Marketing materials generated in {marketing_dir}/{colors.END}")
            self.log(f"  - tweet-thread.txt")
            self.log(f"  - email-launch.txt")
            self.log(f"  - reddit-post.txt")
            
            return True
            
        except Exception as e:
            self.log(f"{colors.RED}ERROR: {str(e)}{colors.END}")
            return False
    
    def step6_deployment_checklist(self) -> bool:
        """Step 6: Generate deployment checklist"""
        self.print_header("STEP 6: DEPLOYMENT CHECKLIST")
        
        checklist = """
# DEPLOYMENT CHECKLIST
## Complete these tasks to go live

### Pre-Launch (Do First)
- [ ] Fix all GitHub tokens (run: python token_fix_wizard.py)
- [ ] Re-download all repos (500+ expected)
- [ ] Test GitHubDownloader app functionality
- [ ] Set up Stripe/PayPal account for payments
- [ ] Create Gumroad account (gumroad.com)

### Product Setup
- [ ] Customize ai-agent-starter-kit/README.md with your branding
- [ ] Update .env.example with your contact info
- [ ] Add your API keys to test the product
- [ ] Build product package (run: python execute.py)
- [ ] Test Docker deployment locally

### Landing Page
- [ ] Update landing-page.html with your branding
- [ ] Add your Gumroad purchase links
- [ ] Update contact email and social links
- [ ] Deploy to GitHub Pages/Netlify/Vercel
- [ ] Test on mobile and desktop

### Marketing
- [ ] Post tweet thread (see marketing/tweet-thread.txt)
- [ ] Send email to your list (see marketing/email-launch.txt)
- [ ] Post on Reddit (see marketing/reddit-post.txt)
- [ ] Share on LinkedIn
- [ ] Submit to Product Hunt

### SaaS Deployment (Optional)
- [ ] Sign up for Railway account
- [ ] Deploy using railway.json config
- [ ] Add environment variables (API keys)
- [ ] Set up custom domain
- [ ] Configure Stripe for subscriptions

### Post-Launch
- [ ] Monitor sales and traffic
- [ ] Collect customer feedback
- [ ] Fix any reported bugs
- [ ] Plan v1.1 features
- [ ] Build email list for updates

### Revenue Targets
- [ ] Week 1: $100-500
- [ ] Month 1: $500-2,000
- [ ] Month 3: $5,000-10,000
- [ ] Month 6: $15,000-35,000
- [ ] Month 12: $30,000-70,000

---
*Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """*
"""
        
        with open("DEPLOYMENT_CHECKLIST.md", "w") as f:
            f.write(checklist)
        
        self.log(f"{colors.GREEN}✓ Deployment checklist saved: DEPLOYMENT_CHECKLIST.md{colors.END}")
        return True
    
    def run_all(self):
        """Run all steps"""
        self.print_header("MASTER EXECUTION SCRIPT")
        self.log("This script will automate your post-token-fix setup")
        self.log("Make sure you've fixed your GitHub tokens first!")
        self.log("")
        
        input("Press ENTER to start (or Ctrl+C to cancel)...")
        
        # Track results
        results = {}
        
        # Step 1: Verify tokens
        results["tokens"] = self.step1_verify_tokens()
        if not results["tokens"]:
            self.log(f"\n{colors.RED}STOPPED: Fix your tokens first!{colors.END}")
            self.log(f"Run: python token_fix_wizard.py")
            return
        
        # Step 2: Rebuild inventory
        results["inventory"] = self.step2_rebuild_inventory()
        
        # Step 3: Prepare product
        results["product"] = self.step3_prepare_product()
        
        # Step 4: Deploy landing page
        results["landing"] = self.step4_deploy_landing_page()
        
        # Step 5: Generate marketing
        results["marketing"] = self.step5_generate_marketing()
        
        # Step 6: Deployment checklist
        results["checklist"] = self.step6_deployment_checklist()
        
        # Summary
        self.print_header("EXECUTION SUMMARY")
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        self.log(f"Steps completed: {passed}/{total}")
        self.log("")
        
        for step, success in results.items():
            status = f"{colors.GREEN}✓ PASS{colors.END}" if success else f"{colors.RED}✗ FAIL{colors.END}"
            self.log(f"  {step:15} {status}")
        
        self.log("")
        
        if passed == total:
            self.log(f"{colors.GREEN}{colors.BOLD}ALL STEPS COMPLETED SUCCESSFULLY!{colors.END}")
            self.log(f"")
            self.log(f"Next actions:")
            self.log(f"  1. Review DEPLOYMENT_CHECKLIST.md")
            self.log(f"  2. Customize marketing materials in marketing/")
            self.log(f"  3. Deploy landing page from deploy/index.html")
            self.log(f"  4. Upload product to Gumroad")
            self.log(f"  5. Start marketing!")
        else:
            self.log(f"{colors.YELLOW}Some steps failed. Check the logs above.{colors.END}")
        
        self.log(f"")
        self.log(f"Full log saved to: {self.config['log_file']}")


def main():
    executor = Executor()
    executor.run_all()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{colors.YELLOW}Execution cancelled by user.{colors.END}")
        sys.exit(0)
