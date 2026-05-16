#!/usr/bin/env python3
"""
GitHub Token Diagnostic Tool
Checks token scopes and identifies missing private repo access
"""

import sys
import requests
import json
from typing import List, Tuple, Dict

def check_token(token: str, account_name: str = "") -> Dict:
    """Check a single token's scopes and repo access"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GitHubDownloader/3.3.0",
        "Authorization": f"token {token}"
    }
    
    result = {
        "account": account_name,
        "token_valid": False,
        "scopes": [],
        "has_repo_scope": False,
        "username": "",
        "public_repos": 0,
        "private_repos": 0,
        "fetched_repos": 0,
        "fetched_private": 0,
        "fetched_public": 0,
        "status": "UNKNOWN",
        "message": ""
    }
    
    try:
        # Check user info and scopes
        resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        
        # Get scopes from headers
        scopes_header = resp.headers.get("X-OAuth-Scopes", "")
        result["scopes"] = [s.strip() for s in scopes_header.split(",") if s.strip()]
        result["has_repo_scope"] = "repo" in result["scopes"] or "repo:status" in result["scopes"]
        
        if resp.status_code != 200:
            result["status"] = "INVALID"
            result["message"] = f"Token invalid: HTTP {resp.status_code}"
            return result
        
        user_data = resp.json()
        result["token_valid"] = True
        result["username"] = user_data.get("login", "")
        result["public_repos"] = user_data.get("public_repos", 0)
        result["private_repos"] = user_data.get("total_private_repos", 0)
        
        if not result["scopes"]:
            result["status"] = "NO_SCOPES"
            result["message"] = "Token has NO scopes! Regenerate with 'repo' scope."
            return result
        
        if not result["has_repo_scope"]:
            result["status"] = "MISSING_REPO_SCOPE"
            result["message"] = f"Missing 'repo' scope! Current: {', '.join(result['scopes'])}"
            return result
        
        # Fetch actual repos to verify access
        page = 1
        all_repos = []
        while page <= 10:  # Limit to prevent infinite loops
            resp = requests.get(
                "https://api.github.com/user/repos",
                headers=headers,
                params={"per_page": 100, "page": page, "type": "all"},
                timeout=15
            )
            if resp.status_code != 200:
                break
            repos = resp.json()
            if not repos:
                break
            all_repos.extend(repos)
            page += 1
        
        result["fetched_repos"] = len(all_repos)
        result["fetched_private"] = sum(1 for r in all_repos if r.get("private"))
        result["fetched_public"] = sum(1 for r in all_repos if not r.get("private"))
        
        # Check for discrepancies
        if result["private_repos"] > 0 and result["fetched_private"] == 0:
            result["status"] = "SCOPE_ISSUE"
            result["message"] = f"Has {result['private_repos']} private repos but fetched 0. Scope issue!"
        elif result["fetched_repos"] >= (result["public_repos"] + result["private_repos"]) * 0.8:
            result["status"] = "OK"
            result["message"] = f"All good! Fetched {result['fetched_repos']} repos."
        else:
            result["status"] = "PARTIAL"
            result["message"] = f"Partial access: {result['fetched_repos']}/{result['public_repos'] + result['private_repos']} repos"
            
    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Error: {str(e)}"
    
    return result


def print_report(results: List[Dict]):
    """Print formatted diagnostic report"""
    print("=" * 80)
    print("GITHUB TOKEN DIAGNOSTIC REPORT")
    print("=" * 80)
    print()
    
    total_expected = 0
    total_fetched = 0
    issues_found = []
    
    for r in results:
        print(f"Account: {r['account'] or r['username']}")
        print(f"  Username:     {r['username']}")
        print(f"  Token Valid:  {'YES' if r['token_valid'] else 'NO'}")
        print(f"  Scopes:       {', '.join(r['scopes']) if r['scopes'] else 'NONE'}")
        print(f"  Has Repo:     {'YES' if r['has_repo_scope'] else 'NO'}")
        print(f"  Public Repos: {r['public_repos']}")
        print(f"  Private Repos: {r['private_repos']}")
        print(f"  Fetched:      {r['fetched_repos']} (Public: {r['fetched_public']}, Private: {r['fetched_private']})")
        print(f"  Status:       {r['status']}")
        print(f"  Message:      {r['message']}")
        
        if r['status'] != "OK":
            issues_found.append(r)
        
        total_expected += r['public_repos'] + r['private_repos']
        total_fetched += r['fetched_repos']
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Expected Repos: {total_expected}")
    print(f"Total Fetched Repos:  {total_fetched}")
    print(f"Missing Repos:        {total_expected - total_fetched}")
    print(f"Accounts with Issues: {len(issues_found)}")
    print()
    
    if issues_found:
        print("ISSUES FOUND:")
        print("-" * 80)
        for issue in issues_found:
            print(f"  • {issue['account']}: {issue['message']}")
        print()
        print("TO FIX:")
        print("  1. Go to https://github.com/settings/tokens")
        print("  2. Generate new Classic token")
        print("  3. CHECK the 'repo' checkbox (Full control of private repositories)")
        print("  4. Update token in GitHubDownloader app")
    else:
        print("ALL TOKENS ARE HEALTHY!")
    
    print("=" * 80)


def main():
    """Main function - can load from accounts.json or accept tokens via arguments"""
    import os
    
    tokens = []
    
    # Try to load from accounts.json
    accounts_file = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader", "accounts.json")
    if os.path.exists(accounts_file):
        try:
            with open(accounts_file, 'r') as f:
                accounts = json.load(f)
            for acc_id, acc_data in accounts.items():
                tokens.append((acc_data.get("username", acc_id), acc_data.get("token", "")))
            print(f"Loaded {len(tokens)} accounts from {accounts_file}")
        except Exception as e:
            print(f"Error loading accounts: {e}")
    
    # Also accept tokens from command line
    if len(sys.argv) > 1:
        for i, token in enumerate(sys.argv[1:]):
            if token.startswith("github_pat_"):
                tokens.append((f"CLI_{i+1}", token))
    
    if not tokens:
        print("Usage: python check_tokens.py [token1] [token2] ...")
        print("Or ensure accounts.json exists in %APPDATA%/GitHubDownloader/")
        sys.exit(1)
    
    print(f"Checking {len(tokens)} tokens...")
    print()
    
    results = []
    for name, token in tokens:
        if not token:
            continue
        # Mask token for display
        masked = token[:20] + "..." + token[-8:] if len(token) > 30 else "***"
        print(f"Checking {name} ({masked})...", end=" ")
        result = check_token(token, name)
        results.append(result)
        print(f"[{result['status']}]")
    
    print()
    print_report(results)
    
    # Save report
    report_file = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GitHubDownloader", "token_report.json")
    try:
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")
    except Exception as e:
        print(f"\nCould not save report: {e}")


if __name__ == "__main__":
    main()
