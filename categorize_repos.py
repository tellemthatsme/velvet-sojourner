import os
import json
from datetime import datetime

repos_dir = r'C:\temp\velvet-sojourner\repos'
scan_file = os.path.join(repos_dir, '_SCAN_RESULTS.json')

with open(scan_file) as f:
    repos = json.load(f)

# Categorize repos
categories = {
    'AI_AGENTS': {
        'name': 'AI Agents & Frameworks',
        'repos': [],
        'monetization': 'HIGH',
        'desc': 'Production-ready AI agent frameworks, multi-agent systems, and autonomous coding tools'
    },
    'CRYPTO_TRADING': {
        'name': 'Crypto & Trading',
        'repos': [],
        'monetization': 'HIGH',
        'desc': 'Trading bots, cryptocurrency platforms, algorithmic trading systems'
    },
    'DEV_TOOLS': {
        'name': 'Developer Tools',
        'repos': [],
        'monetization': 'MEDIUM',
        'desc': 'CLI tools, coding assistants, developer productivity tools'
    },
    'MCP_SERVERS': {
        'name': 'MCP Servers & Integrations',
        'repos': [],
        'monetization': 'HIGH',
        'desc': 'Model Context Protocol servers, API integrations, automation'
    },
    'WEB_APPS': {
        'name': 'Web Applications',
        'repos': [],
        'monetization': 'MEDIUM',
        'desc': 'Full-stack web apps, dashboards, platforms'
    },
    'AUTOMATION': {
        'name': 'Automation & Workflows',
        'repos': [],
        'monetization': 'HIGH',
        'desc': 'n8n workflows, automation scripts, no-code tools'
    },
    'CURATED_LISTS': {
        'name': 'Curated Lists & Resources',
        'repos': [],
        'monetization': 'LOW',
        'desc': 'Awesome lists, tool collections, resource directories'
    },
    'CLAUDE_CODE': {
        'name': 'Claude Code & AI Coding',
        'repos': [],
        'monetization': 'HIGH',
        'desc': 'Claude Code integrations, AI coding assistants, context engineering'
    },
    'SECURITY': {
        'name': 'Security & Privacy',
        'repos': [],
        'monetization': 'MEDIUM',
        'desc': 'Security tools, penetration testing, privacy tools'
    },
    'OTHER': {
        'name': 'Other',
        'repos': [],
        'monetization': 'LOW',
        'desc': 'Miscellaneous projects'
    }
}

# Categorization keywords
cat_keywords = {
    'AI_AGENTS': ['agent', 'ai', 'llm', 'chatgpt', 'crew', 'agentic', 'multi-agent', 'eliza', 'zerepy', 'clara'],
    'CRYPTO_TRADING': ['crypto', 'trading', 'trader', 'ccxt', 'bitcoin', 'solana', 'keno', 'beacon'],
    'DEV_TOOLS': ['cli', 'aider', 'crush', 'bolt', 'codeguide', 'instant', 'rui-code', 'roo-code', 'runcode'],
    'MCP_SERVERS': ['mcp', 'context7', 'metamcp', 'firecrawl', 'crawlee', 'playwright'],
    'WEB_APPS': ['dashboard', 'web', 'react', 'next', 'platform', 'interface', 'worldview'],
    'AUTOMATION': ['n8n', 'workflow', 'automat', 'pipedream', 'flowise'],
    'CURATED_LISTS': ['awesome', 'list', 'collection', 'directory', 'tool-discount'],
    'CLAUDE_CODE': ['claude', 'conductor', 'task-master', 'claudia', 'subagent'],
    'SECURITY': ['security', 'remote-access', 'penetration', 'cybersecurity']
}

for repo in repos:
    name = repo['name'].lower()
    desc = repo.get('description', '').lower()
    dirs = [d.lower() for d in repo.get('dirs', [])]
    
    categorized = False
    for cat_id, keywords in cat_keywords.items():
        for kw in keywords:
            if kw in name or kw in desc:
                categories[cat_id]['repos'].append(repo)
                categorized = True
                break
        if categorized:
            break
    
    if not categorized:
        categories['OTHER']['repos'].append(repo)

# Generate report
report = []
report.append('# COMPLETE REPOSITORY INVENTORY & MONETIZATION PLAN')
report.append(f'\n**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}')
report.append(f'**Total Repos:** {len(repos)}')
report.append(f'**Total Size:** {sum(r["size_mb"] for r in repos):.0f} MB ({sum(r["size_mb"] for r in repos)/1024:.1f} GB)')
report.append(f'**Total Files:** {sum(r["file_count"] for r in repos):,}')
report.append('')

# Summary table
report.append('## SUMMARY BY CATEGORY\n')
report.append('| Category | Count | Total Size | Monetization |')
report.append('|----------|-------|------------|--------------|')
for cat_id, cat in sorted(categories.items(), key=lambda x: len(x[1]['repos']), reverse=True):
    if cat['repos']:
        total_size = sum(r['size_mb'] for r in cat['repos'])
        emoji = '🔥' if cat['monetization'] == 'HIGH' else '💰' if cat['monetization'] == 'MEDIUM' else '📊'
        report.append(f'| {cat["name"]} | {len(cat["repos"])} | {total_size:.0f} MB | {emoji} {cat["monetization"]} |')

# Detailed sections
report.append('\n---\n')
for cat_id, cat in sorted(categories.items(), key=lambda x: len(x[1]['repos']), reverse=True):
    if not cat['repos']:
        continue
    
    report.append(f'## {cat["name"].upper()}')
    report.append(f'*{cat["desc"]}*\n')
    report.append(f'**Monetization Potential:** {cat["monetization"]}')
    report.append('')
    
    # Sort by size descending
    for repo in sorted(cat['repos'], key=lambda x: x['size_mb'], reverse=True):
        langs = ', '.join(repo['languages']) if repo['languages'] != ['Unknown'] else 'N/A'
        features = []
        if repo['has_readme']:
            features.append('📄 README')
        if repo['has_package_json']:
            features.append('📦 Node/TS')
        if repo['has_requirements']:
            features.append('🐍 Python')
        if repo['has_docker']:
            features.append('🐳 Docker')
        if repo['has_ci']:
            features.append('🔄 CI/CD')
        
        feature_str = ' '.join(features)
        report.append(f'### {repo["name"]} ({repo["size_mb"]:.1f} MB)')
        report.append(f'Files: {repo["file_count"]:,} | Languages: {langs} | {feature_str}')
        if repo['description']:
            desc_text = repo['description'][:150]
            report.append(f'> {desc_text}')
        report.append('')
    
    report.append('---\n')

# Monetization recommendations
report.append('# MONETIZATION RECOMMENDATIONS\n')

report.append('## TIER 1: HIGH REVENUE POTENTIAL (Deploy Now)\n')
report.append('These are production-ready or near-production projects with clear monetization paths:\n')
for cat_id in ['AI_AGENTS', 'CRYPTO_TRADING', 'MCP_SERVERS']:
    cat = categories[cat_id]
    if cat['repos']:
        report.append(f'### {cat["name"]}')
        for repo in cat['repos']:
            if repo['size_mb'] > 1.0:
                report.append(f'- **{repo["name"]}** - {repo["size_mb"]:.0f}MB')
        report.append('')

report.append('## TIER 2: MEDIUM REVENUE POTENTIAL (Polish & Launch)\n')
for cat_id in ['CLAUDE_CODE', 'AUTOMATION', 'DEV_TOOLS']:
    cat = categories[cat_id]
    if cat['repos']:
        report.append(f'### {cat["name"]}')
        for repo in cat['repos']:
            if repo['size_mb'] > 0.5:
                report.append(f'- **{repo["name"]}** - {repo["size_mb"]:.0f}MB')
        report.append('')

report.append('## TIER 3: SUPPORTING ASSETS (Bundle & Resell)\n')
for cat_id in ['WEB_APPS', 'CURATED_LISTS']:
    cat = categories[cat_id]
    if cat['repos']:
        report.append(f'### {cat["name"]}')
        for repo in cat['repos']:
            if repo['size_mb'] > 0.1:
                report.append(f'- **{repo["name"]}** - {repo["size_mb"]:.0f}MB')
        report.append('')

# Write report
output_path = r'C:\temp\velvet-sojourner\REPO_INVENTORY.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f'Report written to: {output_path}')
print(f'Total categories: {len([c for c in categories.values() if c["repos"]])}')

# Print summary
print('\n=== CATEGORY SUMMARY ===')
for cat_id, cat in sorted(categories.items(), key=lambda x: len(x[1]['repos']), reverse=True):
    if cat['repos']:
        print(f'{cat["name"]}: {len(cat["repos"])} repos')
