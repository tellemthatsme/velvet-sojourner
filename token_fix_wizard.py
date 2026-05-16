#!/usr/bin/env python3
"""
GitHub Token Fix Wizard
Automated tool to diagnose and fix token scope issues
"""

import os
import sys
import json
import webbrowser
import time
from datetime import datetime
from typing import Dict, List, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TokenFixWizard:
    def __init__(self):
        self.accounts_file = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")), 
            "GitHubDownloader", "accounts.json"
        )
        self.accounts = {}
        self.results = []
        
    def print_header(self, text: str):
        print(f"\n{colors.BOLD}{'='*80}{colors.END}")
        print(f"{colors.BOLD}{text.center(80)}{colors.END}")
        print(f"{colors.BOLD}{'='*80}{colors.END}\n")
        
    def print_step(self, num: int, text: str):
        print(f"{colors.BLUE}Step {num}:{colors.END} {colors.BOLD}{text}{colors.END}")
        
    def print_success(self, text: str):
        print(f"{colors.GREEN}✓ {text}{colors.END}")
        
    def print_error(self, text: str):
        print(f"{colors.RED}✗ {text}{colors.END}")
        
    def print_warning(self, text: str):
        print(f"{colors.YELLOW}⚠ {text}{colors.END}")
        
    def load_accounts(self) -> bool:
        """Load existing accounts from GitHubDownloader"""
        if not os.path.exists(self.accounts_file):
            self.print_error(f"No accounts file found at: {self.accounts_file}")
            self.print_warning("Make sure you've run GitHubDownloader at least once")
            return False
            
        try:
            with open(self.accounts_file, 'r') as f:
                self.accounts = json.load(f)
            self.print_success(f"Loaded {len(self.accounts)} accounts")
            return True
        except Exception as e:
            self.print_error(f"Failed to load accounts: {e}")
            return False
    
    def diagnose_tokens(self) -> List[Dict]:
        """Check all tokens for scope issues"""
        if not HAS_REQUESTS:
            self.print_error("Python 'requests' library not installed")
            self.print_warning("Install with: pip install requests")
            return []
            
        results = []
        
        for acc_id, acc_data in self.accounts.items():
            token = acc_data.get("token", "")
            username = acc_data.get("username", acc_id)
            
            if not token:
                continue
                
            print(f"\nChecking {colors.BOLD}{username}{colors.END}...", end=" ")
            
            try:
                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": f"token {token}",
                    "User-Agent": "TokenFixWizard/1.0"
                }
                
                # Check user info and scopes
                resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
                scopes_header = resp.headers.get("X-OAuth-Scopes", "")
                scopes = [s.strip() for s in scopes_header.split(",") if s.strip()]
                
                if resp.status_code != 200:
                    self.print_error(f"Invalid token (HTTP {resp.status_code})")
                    results.append({
                        "account": username,
                        "status": "INVALID",
                        "scopes": scopes,
                        "action": "REGENERATE"
                    })
                    continue
                
                user_data = resp.json()
                has_repo = "repo" in scopes
                
                if not scopes:
                    self.print_error("NO SCOPES - Needs regeneration")
                    results.append({
                        "account": username,
                        "status": "NO_SCOPES",
                        "scopes": [],
                        "public_repos": user_data.get("public_repos", 0),
                        "private_repos": user_data.get("total_private_repos", 0),
                        "action": "REGENERATE"
                    })
                elif not has_repo:
                    self.print_error(f"Missing 'repo' scope (has: {', '.join(scopes)})")
                    results.append({
                        "account": username,
                        "status": "MISSING_REPO",
                        "scopes": scopes,
                        "public_repos": user_data.get("public_repos", 0),
                        "private_repos": user_data.get("total_private_repos", 0),
                        "action": "REGENERATE"
                    })
                else:
                    self.print_success(f"OK - scopes: {', '.join(scopes)}")
                    results.append({
                        "account": username,
                        "status": "OK",
                        "scopes": scopes,
                        "public_repos": user_data.get("public_repos", 0),
                        "private_repos": user_data.get("total_private_repos", 0),
                        "action": "NONE"
                    })
                    
            except Exception as e:
                self.print_error(f"Error: {str(e)}")
                results.append({
                    "account": username,
                    "status": "ERROR",
                    "scopes": [],
                    "action": "CHECK_MANUALLY"
                })
                
        return results
    
    def generate_fix_instructions(self, results: List[Dict]):
        """Generate step-by-step fix instructions for broken tokens"""
        broken = [r for r in results if r["action"] == "REGENERATE"]
        
        if not broken:
            self.print_success("All tokens are healthy! No action needed.")
            return
            
        self.print_header("TOKEN FIX INSTRUCTIONS")
        
        print(f"{colors.BOLD}Accounts needing fix: {len(broken)}{colors.END}\n")
        
        for i, acc in enumerate(broken, 1):
            username = acc["account"]
            status = acc["status"]
            public = acc.get("public_repos", "?")
            private = acc.get("private_repos", "?")
            
            print(f"{colors.BOLD}Account {i}: {username}{colors.END}")
            print(f"  Status: {colors.RED}{status}{colors.END}")
            print(f"  Public repos: {public}")
            print(f"  Private repos: {private} (currently inaccessible)")
            print()
            
            self.print_step(1, f"Sign in to GitHub as {username}")
            print("   URL: https://github.com/login")
            print()
            
            self.print_step(2, "Navigate to Token Settings")
            print("   URL: https://github.com/settings/tokens")
            print("   Or: Settings → Developer settings → Personal access tokens → Tokens (classic)")
            print()
            
            self.print_step(3, "Generate New Token")
            print("   Click: 'Generate new token' → 'Generate new token (classic)'")
            print()
            
            self.print_step(4, "Configure Token")
            print(f"   Note: GitHubDownloader-v2-{username}")
            print("   Expiration: 90 days (recommended)")
            print()
            
            self.print_step(5, "SELECT THESE SCOPES (REQUIRED):")
            print(f"   {colors.GREEN}[✓]{colors.END} repo (Full control of private repositories)")
            print(f"      {colors.GREEN}[✓]{colors.END} repo:status")
            print(f"      {colors.GREEN}[✓]{colors.END} repo_deployment")
            print(f"      {colors.GREEN}[✓]{colors.END} public_repo")
            print(f"      {colors.GREEN}[✓]{colors.END} repo:invite")
            print(f"   {colors.GREEN}[✓]{colors.END} read:org (Read org and team membership)")
            print(f"   {colors.GREEN}[✓]{colors.END} user (Update all user data)")
            print()
            
            self.print_step(6, "Generate and Copy")
            print("   Click 'Generate token'")
            print(f"   {colors.RED}{colors.BOLD}COPY TOKEN IMMEDIATELY - YOU WON'T SEE IT AGAIN!{colors.END}")
            print()
            
            self.print_step(7, "Update in GitHubDownloader App")
            print("   1. Open GitHubDownloader.exe")
            print("   2. Go to 'Accounts' tab")
            print(f"   3. Select account '{username}'")
            print("   4. Click 'Remove'")
            print("   5. Click 'Add Account' → 'Token (PAT)' tab")
            print("   6. Paste new token")
            print("   7. Click 'Add'")
            print()
            print("-" * 80)
            print()
    
    def open_github_settings(self):
        """Open GitHub token settings in browser"""
        print("\nOpening GitHub token settings in browser...")
        webbrowser.open("https://github.com/settings/tokens")
        time.sleep(2)
    
    def create_batch_update_script(self, results: List[Dict]):
        """Create a script to bulk update tokens after regeneration"""
        broken = [r for r in results if r["action"] == "REGENERATE"]
        
        if not broken:
            return
            
        script_content = '''#!/usr/bin/env python3
"""
Batch Token Updater for GitHubDownloader
Run this after regenerating all tokens to update accounts.json
"""

import json
import os
from datetime import datetime

ACCOUNTS_FILE = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "GitHubDownloader", "accounts.json"
)

def update_token(account_name: str, new_token: str):
    """Update a specific account's token"""
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"Accounts file not found: {ACCOUNTS_FILE}")
        return False
        
    with open(ACCOUNTS_FILE, 'r') as f:
        accounts = json.load(f)
    
    # Find account by username
    updated = False
    for acc_id, acc_data in accounts.items():
        if acc_data.get("username") == account_name:
            acc_data["token"] = new_token
            acc_data["updated_at"] = datetime.now().isoformat()
            updated = True
            print(f"Updated token for {account_name}")
            break
    
    if updated:
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)
        return True
    else:
        print(f"Account not found: {account_name}")
        return False

def main():
    print("GitHub Token Batch Updater")
    print("=" * 60)
    print("Enter new tokens for each account (leave blank to skip)")
    print()
    
'''
        
        for acc in broken:
            username = acc["account"]
            script_content += f'''    print("Account: {username}")
    token = input("New token: ").strip()
    if token:
        update_token("{username}", token)
    print()
'''
        
        script_content += '''
    print("Done! Restart GitHubDownloader to use new tokens.")

if __name__ == "__main__":
    main()
'''
        
        script_path = "update_tokens.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.print_success(f"Created batch updater: {script_path}")
        print(f"Run it after regenerating tokens: python {script_path}")
    
    def run(self):
        """Main wizard flow"""
        self.print_header("GITHUB TOKEN FIX WIZARD v1.0")
        
        print("This wizard will:")
        print("  1. Diagnose all your GitHub tokens")
        print("  2. Identify which ones need fixing")
        print("  3. Generate step-by-step fix instructions")
        print("  4. Create tools to help update tokens")
        print()
        
        input("Press ENTER to start diagnosis...")
        
        # Step 1: Load accounts
        self.print_step(1, "Loading accounts from GitHubDownloader")
        if not self.load_accounts():
            print("\nTrying to create sample accounts file...")
            return
        
        # Step 2: Diagnose
        self.print_step(2, "Diagnosing token scopes")
        self.results = self.diagnose_tokens()
        
        # Step 3: Show summary
        self.print_header("DIAGNOSIS SUMMARY")
        
        ok_count = sum(1 for r in self.results if r["status"] == "OK")
        broken_count = len(self.results) - ok_count
        
        print(f"Total accounts checked: {len(self.results)}")
        print(f"Healthy tokens: {colors.GREEN}{ok_count}{colors.END}")
        print(f"Tokens needing fix: {colors.RED}{broken_count}{colors.END}")
        print()
        
        if broken_count == 0:
            self.print_success("All tokens are properly configured!")
            self.print_success("You can now download all repositories including private ones.")
            return
        
        # Step 4: Generate fix instructions
        self.generate_fix_instructions(self.results)
        
        # Step 5: Offer to open GitHub
        print("\nWould you like to open GitHub token settings now?")
        choice = input("Open browser? (y/n): ").strip().lower()
        if choice == 'y':
            self.open_github_settings()
        
        # Step 6: Create batch updater
        self.print_header("AUTOMATION TOOLS")
        self.create_batch_update_script(self.results)
        
        # Step 7: Final checklist
        self.print_header("POST-FIX CHECKLIST")
        print("After regenerating tokens:")
        print()
        print("□ Run: python update_tokens.py")
        print("□ Or manually update each account in GitHubDownloader")
        print("□ Run: python check_tokens.py (to verify)")
        print("□ Open GitHubDownloader → Accounts tab")
        print("□ Verify all accounts show 'Valid' status")
        print("□ Click 'Download All Accounts' to get all repos")
        print("□ Verify you now have 500+ repos instead of 153")
        print()
        
        self.print_success("Wizard complete! Follow the instructions above to fix your tokens.")
        print(f"\n{colors.BOLD}Estimated time to fix all tokens: 15-20 minutes{colors.END}")
        print(f"{colors.BOLD}Expected result: Access to 500+ repositories (currently 153){colors.END}")


def main():
    wizard = TokenFixWizard()
    wizard.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWizard cancelled by user.")
        sys.exit(0)
