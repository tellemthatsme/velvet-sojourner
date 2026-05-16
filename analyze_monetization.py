#!/usr/bin/env python3
"""
Monetization Strategy Analyzer
Analyzes downloaded repos and recommends best monetization approach
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Category mappings based on repo names and keywords
CATEGORY_KEYWORDS = {
    "AI Agents & Frameworks": [
        "agent", "ai-", "claude", "gpt", "llm", "crew", "autogen", "langchain",
        "openai", "anthropic", "gemini", "mistral", "vector", "embedding", "rag",
        "prompt", "chain", "litellm", "aider", "eliza", "volo", "seek"
    ],
    "Crypto & Trading": [
        "crypto", "trading", "trade", "bitcoin", "ethereum", "defi", "blockchain",
        "wallet", "exchange", "portfolio", "bot", "signal", "chart", "token"
    ],
    "MCP Servers & Integrations": [
        "mcp", "server", "context", "supabase", "integration", "connector", "bridge"
    ],
    "Developer Tools": [
        "devtools", "cli", "tool", "utility", "generator", "builder", "compiler",
        "debugger", "linter", "formatter", "scanner", "analyzer"
    ],
    "Web Applications": [
        "web", "app", "dashboard", "ui", "frontend", "backend", "api", "site",
        "platform", "portal", "interface"
    ],
    "Automation & Workflows": [
        "automation", "workflow", "n8n", "pipeline", "cron", "schedule", "task",
        "batch", "process", "orchestration", "zapier", "ifttt"
    ],
    "Claude Code & AI Coding": [
        "claude-code", "cursor", "coding", "programming", "ide", "editor",
        "vscode", "extension", "plugin", "snippet"
    ],
    "Security & Privacy": [
        "security", "privacy", "encrypt", "protect", "guard", "shield", "audit",
        "compliance", "gdpr", "hipaa"
    ],
    "Curated Lists & Resources": [
        "awesome", "list", "resources", "curated", "collection", "awesome-",
        "roadmap", "guide", "tutorial", "examples"
    ]
}


def categorize_repo(repo_name: str, description: str = "") -> str:
    """Categorize a repo based on name and description"""
    text = f"{repo_name} {description}".lower()
    
    scores = defaultdict(int)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[category] += 1
    
    if scores:
        return max(scores, key=scores.get)
    return "Other"


def analyze_repos(repos_dir: str = "repos") -> Dict:
    """Analyze all downloaded repos and generate monetization report"""
    
    if not os.path.exists(repos_dir):
        print(f"Directory not found: {repos_dir}")
        return {}
    
    categories = defaultdict(list)
    total_size = 0
    total_files = 0
    
    # Scan repos directory
    for item in os.listdir(repos_dir):
        repo_path = os.path.join(repos_dir, item)
        if not os.path.isdir(repo_path):
            continue
        
        # Calculate size
        size = 0
        files = 0
        for root, dirs, filenames in os.walk(repo_path):
            files += len(filenames)
            for f in filenames:
                fp = os.path.join(root, f)
                try:
                    size += os.path.getsize(fp)
                except:
                    pass
        
        # Categorize
        category = categorize_repo(item)
        categories[category].append({
            "name": item,
            "size_mb": round(size / (1024*1024), 1),
            "files": files
        })
        
        total_size += size
        total_files += files
    
    # Calculate monetization scores
    category_scores = {}
    for cat, repos in categories.items():
        cat_size = sum(r["size_mb"] for r in repos)
        cat_count = len(repos)
        
        # Scoring algorithm
        score = 0
        if cat == "AI Agents & Frameworks":
            score = cat_count * 10 + cat_size * 0.5
        elif cat in ["MCP Servers & Integrations", "Crypto & Trading"]:
            score = cat_count * 8 + cat_size * 0.3
        elif cat in ["Automation & Workflows", "Claude Code & AI Coding"]:
            score = cat_count * 7 + cat_size * 0.2
        else:
            score = cat_count * 5 + cat_size * 0.1
        
        category_scores[cat] = {
            "count": cat_count,
            "size_mb": round(cat_size, 1),
            "repos": repos,
            "score": round(score, 1),
            "monetization_potential": "HIGH" if score > 100 else "MEDIUM" if score > 50 else "LOW"
        }
    
    # Sort by score
    sorted_categories = dict(sorted(
        category_scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    ))
    
    return {
        "total_repos": sum(len(v["repos"]) for v in category_scores.values()),
        "total_size_mb": round(total_size / (1024*1024), 1),
        "total_files": total_files,
        "categories": sorted_categories,
        "top_strategy": generate_strategy(sorted_categories)
    }


def generate_strategy(categories: Dict) -> Dict:
    """Generate recommended monetization strategy"""
    
    top_3 = list(categories.keys())[:3]
    
    strategies = {
        ("AI Agents & Frameworks",): {
            "name": "AI Agent SaaS Platform",
            "description": "Deploy top AI agent repos as managed services",
            "products": [
                "Universal LLM Proxy (litellm)",
                "AI Agent Orchestration Platform",
                "Claude Code Enhancement Suite"
            ],
            "pricing": "$49-499/month",
            "timeline": "2-4 weeks to MVP",
            "revenue_potential": "$10K-50K/month"
        },
        ("Crypto & Trading",): {
            "name": "Crypto Trading Suite",
            "description": "Package trading bots and analytics tools",
            "products": [
                "AI Trading Bot Marketplace",
                "Portfolio Analytics Dashboard",
                "Signal Service Subscription"
            ],
            "pricing": "$99-999/month",
            "timeline": "1-2 weeks to MVP",
            "revenue_potential": "$5K-25K/month"
        },
        ("MCP Servers & Integrations", "Developer Tools"): {
            "name": "Developer Tool Suite",
            "description": "Managed MCP servers and dev tools",
            "products": [
                "MCP Server Network",
                "Developer Productivity Pack",
                "API Integration Platform"
            ],
            "pricing": "$29-199/month",
            "timeline": "1-2 weeks to MVP",
            "revenue_potential": "$3K-15K/month"
        },
        ("Automation & Workflows",): {
            "name": "Workflow Automation Agency",
            "description": "Custom automation solutions and templates",
            "products": [
                "n8n Template Marketplace",
                "Custom Workflow Development",
                "Automation Consulting"
            ],
            "pricing": "$49-299/month + consulting",
            "timeline": "1 week to MVP",
            "revenue_potential": "$2K-10K/month"
        }
    }
    
    # Match top categories to strategies
    best_match = None
    best_score = 0
    
    for key, strategy in strategies.items():
        score = sum(1 for k in key if k in top_3)
        if score > best_score:
            best_score = score
            best_match = strategy
    
    if not best_match:
        best_match = {
            "name": "Mixed Portfolio Bundle",
            "description": "Bundle top repos across categories",
            "products": ["Premium Bundle", "Category-specific packs", "Consulting"],
            "pricing": "$99-299",
            "timeline": "2-3 weeks",
            "revenue_potential": "$5K-20K/month"
        }
    
    return best_match


def print_report(report: Dict):
    """Print formatted monetization report"""
    print("=" * 80)
    print("MONETIZATION STRATEGY ANALYZER")
    print("=" * 80)
    print()
    print(f"Total Repositories: {report['total_repos']}")
    print(f"Total Size: {report['total_size_mb']} MB")
    print(f"Total Files: {report['total_files']}")
    print()
    
    print("CATEGORY BREAKDOWN:")
    print("-" * 80)
    for cat, data in report["categories"].items():
        print(f"\n{cat}")
        print(f"  Count: {data['count']} | Size: {data['size_mb']} MB | Score: {data['score']}")
        print(f"  Potential: {data['monetization_potential']}")
        print(f"  Top Repos:")
        for repo in data['repos'][:5]:
            print(f"    - {repo['name']} ({repo['size_mb']} MB, {repo['files']} files)")
    
    print()
    print("=" * 80)
    print("RECOMMENDED STRATEGY")
    print("=" * 80)
    strategy = report["top_strategy"]
    print(f"Name: {strategy['name']}")
    print(f"Description: {strategy['description']}")
    print(f"Timeline: {strategy['timeline']}")
    print(f"Revenue Potential: {strategy['revenue_potential']}")
    print(f"Pricing: {strategy['pricing']}")
    print()
    print("Products:")
    for product in strategy['products']:
        print(f"  • {product}")
    
    print()
    print("QUICK START PLAN:")
    print("-" * 80)
    print("Week 1: Fix token scopes & re-download all repos")
    print("Week 2: Select top 5 repos for initial productization")
    print("Week 3: Deploy MVP of primary product")
    print("Week 4: Create landing page & payment processing")
    print("Week 5-6: Beta testing with early users")
    print("Week 7-8: Launch on Product Hunt & Hacker News")
    print()
    print("=" * 80)


def main():
    import sys
    
    repos_dir = sys.argv[1] if len(sys.argv) > 1 else "repos"
    
    print(f"Analyzing repositories in: {repos_dir}")
    print()
    
    report = analyze_repos(repos_dir)
    
    if not report:
        print("No repositories found. Run downloader first.")
        sys.exit(1)
    
    print_report(report)
    
    # Save report
    report_file = "monetization_report.json"
    try:
        with open(report_file, 'w') as f:
            # Convert to JSON-serializable format
            json_report = {
                "total_repos": report["total_repos"],
                "total_size_mb": report["total_size_mb"],
                "total_files": report["total_files"],
                "categories": {
                    k: {
                        "count": v["count"],
                        "size_mb": v["size_mb"],
                        "score": v["score"],
                        "monetization_potential": v["monetization_potential"],
                        "repo_names": [r["name"] for r in v["repos"]]
                    }
                    for k, v in report["categories"].items()
                },
                "top_strategy": report["top_strategy"]
            }
            json.dump(json_report, f, indent=2)
        print(f"\nReport saved to: {report_file}")
    except Exception as e:
        print(f"Could not save report: {e}")


if __name__ == "__main__":
    main()
