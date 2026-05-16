#!/usr/bin/env python3
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
    print("
Some items missing. Run: python proceed.py")
    sys.exit(1)

print("
" + "="*80)
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
