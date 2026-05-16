#!/usr/bin/env python3
"""
INTERACTIVE TOKEN FIX WIZARD
Step-by-step guide to fix all 5 GitHub tokens
"""

import json
import os
import sys
import webbrowser
import time
from pathlib import Path

APP_DATA = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader")
ACCOUNTS_FILE = os.path.join(APP_DATA, "accounts.json")

def load_accounts():
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def step(text):
    print(f"\n{'─'*70}")
    print(f"  STEP: {text}")
    print(f"{'─'*70}")

def fix_token_wizard():
    clear_screen()
    banner("GITHUB TOKEN FIX WIZARD")
    print("This will walk you through fixing all 5 GitHub tokens.")
    print("Each token needs the 'repo' scope to access private repositories.")
    print("\nPress ENTER to start...")
    input()
    
    accounts = load_accounts()
    fixed_count = 0
    
    for acc_id, acc in accounts.items():
        username = acc["username"]
        old_token = acc["token"]
        
        clear_screen()
        banner(f"FIXING TOKEN: {username}")
        
        print(f"\nAccount: {username}")
        print(f"Current Token: {old_token[:20]}...{old_token[-10:]}")
        print(f"Status: MISSING 'repo' SCOPE")
        print(f"\nThis token CANNOT access private repositories.")
        
        print("\n" + "="*70)
        print("INSTRUCTIONS:")
        print("="*70)
        print("1. Open your browser to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token' > 'Generate new token (classic)'")
        print("3. Enter a name like: 'GitHub Downloader Full Access'")
        print("4. Set expiration to: 'No expiration' (or 90 days)")
        print("5. CHECK THE BOX for: 'repo' (Full control of private repositories)")
        print("   └── This is the CRITICAL step!")
        print("6. Scroll down and click 'Generate token'")
        print("7. COPY the new token (it starts with 'ghp_' or 'github_pat_')")
        print("8. PASTE it below:")
        print("="*70)
        
        # Open browser
        print(f"\n[Opening browser to GitHub token settings...]")
        webbrowser.open("https://github.com/settings/tokens")
        
        print("\n" + "─"*70)
        new_token = input(f"Paste new token for {username}: ").strip()
        
        if not new_token:
            print("❌ Skipped - no token entered")
            continue
            
        if not (new_token.startswith("ghp_") or new_token.startswith("github_pat_")):
            print(f"⚠️  Warning: Token doesn't look like a GitHub token!")
            confirm = input("Continue anyway? (y/n): ").lower()
            if confirm != 'y':
                continue
        
        # Update account
        acc["token"] = new_token
        acc["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        fixed_count += 1
        
        print(f"\n✅ Token updated for {username}")
        print(f"   New token: {new_token[:20]}...{new_token[-10:]}")
        
        if len(accounts) > fixed_count:
            print(f"\n➡️  {len(accounts) - fixed_count} accounts remaining...")
            input("Press ENTER to continue to next account...")
    
    # Save all changes
    save_accounts(accounts)
    
    clear_screen()
    banner("ALL TOKENS UPDATED")
    print(f"\nFixed {fixed_count}/{len(accounts)} accounts")
    print("\n✅ accounts.json has been saved!")
    print("\nNext step: VERIFY the tokens work")
    print("\nRun this command:")
    print("   python check_tokens.py")
    print("\nOr press ENTER to verify now...")
    input()
    
    # Run verification
    verify_tokens(accounts)

def verify_tokens(accounts):
    banner("VERIFYING TOKENS")
    
    try:
        import requests
    except ImportError:
        print("❌ 'requests' library not installed")
        print("   Install with: pip install requests")
        return
    
    all_ok = True
    
    for acc_id, acc in accounts.items():
        username = acc["username"]
        token = acc["token"]
        
        print(f"\nChecking {username}...", end=" ")
        
        headers = {"Authorization": f"token {token}"}
        
        try:
            resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            scopes = resp.headers.get("X-OAuth-Scopes", "")
            
            if resp.status_code == 200:
                data = resp.json()
                has_repo = "repo" in [s.strip() for s in scopes.split(",") if s.strip()]
                
                if has_repo:
                    print("✅ VALID WITH REPO SCOPE")
                    print(f"   Public repos: {data.get('public_repos', 0)}")
                    print(f"   Private repos: {data.get('total_private_repos', 0)}")
                else:
                    print("❌ VALID BUT MISSING 'repo' SCOPE")
                    print("   You need to regenerate with 'repo' checked!")
                    all_ok = False
            else:
                print(f"❌ INVALID TOKEN (HTTP {resp.status_code})")
                all_ok = False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            all_ok = False
    
    print("\n" + "="*70)
    if all_ok:
        print("✅ ALL TOKENS VERIFIED SUCCESSFULLY!")
        print("\nYou can now:")
        print("   1. Open GitHubDownloader.exe")
        print("   2. Click 'All Accounts'")
        print("   3. Download all ~504 repositories")
    else:
        print("⚠️  SOME TOKENS STILL HAVE ISSUES")
        print("\nPlease re-run this wizard for the failed accounts.")
    print("="*70)

if __name__ == "__main__":
    fix_token_wizard()
    print("\nPress ENTER to exit...")
    input()
