import json, re, os

with open('C:/temp/velvet-sojourner/repos/_SCAN_ALL_RESULTS.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

repos = data['repos']

# Categories with keyword patterns (name_patterns, desc_patterns, also check case-insensitive)
def classify_repo(repo):
    name = repo['name'].lower()
    desc = (repo.get('description') or '').lower()
    tier = repo.get('tier', '')
    score = repo.get('score', 0)

    # Determine if low quality
    is_empty = repo['file_count'] == 0 or (not desc.strip() and score < 10)

    classifications = []

    # 1. MCP Servers
    if re.search(r'\bmcp\b', name) or re.search(r'\bmcp\b', desc) or re.search(r'model.context.protocol', desc):
        classifications.append({
            'category': 'MCP Servers',
            'subcategory': 'MCP Server' if not re.search(r'client', name) else 'MCP Client',
            'tags': ['mcp', 'model-context-protocol'],
            'confidence': 'high'
        })

    # 2. Cryptocurrency / Trading Bots
    if (re.search(r'\bcrypto\b|\btrading\b|\btrader\b|\btrade\b|\bbot\b.*(crypto|trading)|solana|defi|blockchain|paper.trading|exchange|nautilus', name) or
        re.search(r'cryptocurrency|crypto.trading|trading.bot|trading.platform|exchange.*trading|paper.trading|market.data|portfolio.management|trading.card|ai.*trading', desc)):
        is_paper = bool(re.search(r'paper.trading|trade.sim|simulator', name + ' ' + desc))
        classifications.append({
            'category': 'Trading Bots & Crypto',
            'subcategory': 'Paper Trading' if is_paper else 'Trading Platform',
            'tags': ['crypto', 'trading', 'blockchain'],
            'confidence': 'high'
        })

    # 3. AI Frameworks & Agent Platforms
    if (re.search(r'\b(crewai|eliza|goose|claude.*agent|ai.*agent|agent.*(framework|platform|system)|multi.*agent|agent.*for|autonomous.*agent)\b', name) or
        re.search(r'\b(ai.agent|agent.framework|multi.agent|autonomous.agent|agent.platform)\b', desc)):
        classifications.append({
            'category': 'AI Frameworks & Agents',
            'subcategory': 'Agent Platform',
            'tags': ['ai-agents', 'framework'],
            'confidence': 'high'
        })

    # 4. Chatbots & Conversational AI
    if (re.search(r'\b(chatbot|chat.bot|chat.*organizer|chat.*archiver|chat.*sort|chat.*merg|chat.*scribe|chat.*whisperer|chatify|chatsort|chatty|conversation.crafter|swift.chat)\b', name) or
        re.search(r'\b(chat.organizer|conversation|chatbot|chat.history)\b', desc)):
        classifications.append({
            'category': 'Chatbots & Conversational AI',
            'subcategory': 'Chat Management' if re.search(r'organizer|sort|archiver|merg', name) else 'Chatbot',
            'tags': ['chat', 'conversation-ai'],
            'confidence': 'high'
        })

    # 5. Web Scraping & Data Extraction
    if (re.search(r'\b(scrapy|crawlee|firecrawl|crawl|scrape|scraping)\b', name) or
        re.search(r'\b(web.scrap|scraping|crawl|data.extraction)\b', desc)):
        classifications.append({
            'category': 'Web Scraping & Crawling',
            'subcategory': 'Scraping Framework',
            'tags': ['web-scraping', 'crawling'],
            'confidence': 'high'
        })

    # 6. Automation & Workflow
    if (re.search(r'\b(n8n|pipedream|workflow|automation|automate|n8n.*verse)\b', name) or
        re.search(r'\b(workflow.automation|ci.cd|pipeline|automation.platform)\b', desc)):
        classifications.append({
            'category': 'Automation & Workflow',
            'subcategory': 'Workflow Platform',
            'tags': ['automation', 'workflow'],
            'confidence': 'high'
        })

    # 7. Developer Tools & CLI
    if (re.search(r'\b(gemini.cli|claude.code|codeguide|plandex|code.*archaeologist|code.*lens|code.*flow|code.*narrative|onthereg|dev.*forge|dev.*plan|dev.*stream|devflow|spec.kit|context7|deepclaude|git.*insight|git.*mcp)\b', name) or
        re.search(r'\b(code.review|developer.tool|cli.tool|code.analysis|dev.toolkit|development.platform)\b', desc)):
        classifications.append({
            'category': 'Developer Tools',
            'subcategory': 'CLI Tool' if re.search(r'cli', name) else 'Dev Platform',
            'tags': ['developer-tools', 'cli'],
            'confidence': 'high'
        })

    # 8. Social Media Tools
    if (re.search(r'\b(social|engage|traffic.*boost|influence.*bloom|socialv0|socmedia|social.*boost|social.*automation)\b', name) and
        not re.search(r'social.selling|social.engagement', name)):
        # But check desc for social
        classifications.append({
            'category': 'Social Media Tools',
            'subcategory': 'Social Management',
            'tags': ['social-media', 'marketing'],
            'confidence': 'high'
        })

    # Also catch social by description
    if not classifications and re.search(r'\b(social.media|social.management|content.creator|social.growth)\b', desc):
        classifications.append({
            'category': 'Social Media Tools',
            'subcategory': 'Social Management',
            'tags': ['social-media', 'marketing'],
            'confidence': 'high'
        })

    # 9. Project Management
    if (re.search(r'\b(project.*(mag|hub|genesis|sifter|confluence|brain|sage)|idealaunch|devflow.*matrix|task.*board|kanban|taskmanage)\b', name) or
        re.search(r'\b(project.management|task.management|project.platform|sprint)\b', desc)):
        classifications.append({
            'category': 'Project Management',
            'subcategory': 'Task Management',
            'tags': ['project-management', 'productivity'],
            'confidence': 'high'
        })

    # 10. Monetization & Business
    if (re.search(r'\b(monetiz|money.*maker|money.*mint|earn.*big|profit|revenue|freebie.*optimiser|moneymaker|multi.*platform.*monetization)\b', name) or
        re.search(r'\b(monetization|money.making|revenue|profit\b)', desc)):
        classifications.append({
            'category': 'Monetization & Business',
            'subcategory': 'Revenue Generation',
            'tags': ['monetization', 'business'],
            'confidence': 'high'
        })

    # 11. Media & Video Tools
    if (re.search(r'\b(video.*studio|video.*forge|story.*loom|video|meme|gemcopilot|legacy.*video|muse.*master)\b', name) or
        re.search(r'\b(video.editing|video.generator|video.tribute|media.tool)\b', desc)):
        classifications.append({
            'category': 'Media & Video Tools',
            'subcategory': 'Video Editor' if 'studio' in name else 'Media Platform',
            'tags': ['video', 'media'],
            'confidence': 'high'
        })

    # 12. Knowledge Management & Documentation
    if (re.search(r'\b(linkwarden|knowl|note.*scribe|docu.*prime|wiki|deepwiki|brain.*organizer|knowledge|kbbolt)\b', name) or
        re.search(r'\b(knowledge.management|wiki|document.management|note.taking)\b', desc)):
        classifications.append({
            'category': 'Knowledge Management',
            'subcategory': 'Documentation',
            'tags': ['knowledge-management', 'docs'],
            'confidence': 'high'
        })

    # 13. AI App Builders / No-Code
    if (re.search(r'\b(dyad|lovable|open.*lovable|bolt.*clone|love.*bolt|no.code|v0.*clone|chatty.*app|create.*volo|app.*builder)\b', name) or
        re.search(r'\b(app.builder|no.code|low.code|ai.app.builder|scaffold)\b', desc)):
        classifications.append({
            'category': 'AI App Builders & No-Code',
            'subcategory': 'No-Code Platform',
            'tags': ['no-code', 'app-builder'],
            'confidence': 'high'
        })

    # 14. Prompt Engineering
    if (re.search(r'\b(prompt.*(brain|hub|waterfall|master|organizer)|prompts|leaked.*prompt|system.*prompt.*leak)\b', name) or
        re.search(r'\b(prompt.engineering|prompt.management|prompt.template)\b', desc)):
        classifications.append({
            'category': 'Prompt Engineering',
            'subcategory': 'Prompt Library',
            'tags': ['prompts', 'llm'],
            'confidence': 'high'
        })

    # 15. Browser Tools & Extensions
    if (re.search(r'\b(browser.*ext|tab.*time|firefox|bookmark|hyperlink.*organizer|link.*locker|favsort|favorite.*flow)\b', name) or
        re.search(r'\b(browser.extension|bookmark.management|tab.management)\b', desc)):
        classifications.append({
            'category': 'Browser Tools & Extensions',
            'subcategory': 'Bookmark Manager' if re.search(r'bookmark|favorite|fav|hyperlink|link', name) else 'Browser Extension',
            'tags': ['browser', 'extension'],
            'confidence': 'high'
        })

    # 16. Gaming & Trading Cards
    if (re.search(r'\b(game.*dev|engine.*craft|gamedev|marvel.*trad|poke.*marvel|poke.*monopoly|marvel.*card|trading.card)\b', name) or
        re.search(r'\b(trading.card|game.development|marvel|pokemon)\b', desc)):
        classifications.append({
            'category': 'Gaming & Trading Cards',
            'subcategory': 'Trading Cards' if re.search(r'marvel|poke|card|trading.card', name + ' ' + desc) else 'Game Dev',
            'tags': ['gaming', 'trading-cards'],
            'confidence': 'high'
        })

    # 17. Security & Privacy
    if (re.search(r'\b(cyber.*security|security.*suite|profile.*detective|guardian.*speak|remote.*access)\b', name) or
        re.search(r'\b(cybersecurity|security|privacy.first)\b', desc)):
        classifications.append({
            'category': 'Security & Privacy',
            'subcategory': 'Cybersecurity',
            'tags': ['security', 'privacy'],
            'confidence': 'high'
        })

    # 18. Analytics & Insights
    if (re.search(r'\b(insight.*(engine|garden|enterprise)|analytics|time.tunnel|time.travel.*(tracker|insights)|browse.*time|truth.*timeline|traffic.*roundabout)\b', name) or
        re.search(r'\b(analytics|insights|browser.history.analy|dashboard.*analytics)\b', desc)):
        classifications.append({
            'category': 'Analytics & Insights',
            'subcategory': 'Data Analytics',
            'tags': ['analytics', 'insights'],
            'confidence': 'high'
        })

    # 19. AI Tools & Directories
    if (re.search(r'\b(ai.*tool.*(directory|list|discover|stream)|tool.*stream|universal.*toolbox|directorybolt|ai.*directory|top.*ai.*directory)\b', name) or
        re.search(r'\b(ai.tools.directory|ai.tool.discovery)\b', desc)):
        classifications.append({
            'category': 'AI Tools & Directories',
            'subcategory': 'AI Directory',
            'tags': ['ai-tools', 'directory'],
            'confidence': 'high'
        })

    # 20. Templates & Startup Kits
    if (re.search(r'\b(template|starter.*kit|scaffold|create.*app|boilerplate|ai.*starter)\b', name) and
        re.search(r'(template|starter|scaffold|boilerplate)', name)):
        classifications.append({
            'category': 'Templates & Starter Kits',
            'subcategory': 'Project Template',
            'tags': ['template', 'starter-kit'],
            'confidence': 'medium'
        })

    # 21. Local AI / Self-Hosted
    if (re.search(r'\b(local.*ai|self.hosted|ollama|local.*operator|local.*deployer|local.*packaged|local.*alchemy)\b', name) or
        re.search(r'\b(local.ai|self.hosted|docker.compose)\b', desc)):
        classifications.append({
            'category': 'Local & Self-Hosted AI',
            'subcategory': 'Local AI',
            'tags': ['self-hosted', 'local-ai'],
            'confidence': 'high'
        })

    # 22. Productivity
    if (re.search(r'\b(productivity|instant.*code.*smith|tab.*time|meme.*verse|time.*track|calendar|task.*board)\b', name) or
        re.search(r'\b(productivity|task.management|time.tracking)\b', desc)):
        # Don't double count if already classified
        pass

    # 23. Healthcare & Fitness
    if (re.search(r'\b(super.*coach|fitness|ndis.*(assistant|flow)|plant.*path|health)\b', name) or
        re.search(r'\b(fitness|ndis|healthcare|plant.disease)\b', desc)):
        classifications.append({
            'category': 'Healthcare & Fitness',
            'subcategory': 'Fitness' if re.search(r'fitness|coach', name) else 'Healthcare',
            'tags': ['health', 'fitness'],
            'confidence': 'high'
        })

    # 24. Gambling & Betting
    if (re.search(r'\b(keno|gambling|betting|oracle.*picks)\b', name) or
        re.search(r'\b(keno|betting|gambling)\b', desc)):
        classifications.append({
            'category': 'Gambling & Betting',
            'subcategory': 'Keno Analysis' if 'keno' in name else 'Betting',
            'tags': ['gambling', 'keno'],
            'confidence': 'high'
        })

    # 25. Data Processing & ETL
    if (re.search(r'\b(etl|data.*process|content.*process|c.*comprehensive.*content|data.*pipeline|data.*ingestion)\b', name) or
        re.search(r'\b(data.processing|content.processing|chatgpt.export.process|etl.pipeline)\b', desc)):
        classifications.append({
            'category': 'Data Processing & ETL',
            'subcategory': 'Data Pipeline',
            'tags': ['data-processing', 'etl'],
            'confidence': 'medium'
        })

    # 26. Marketing & Sales
    if (re.search(r'\b(marketing|sales|social.selling|lead.generation|cold.outreach|g.*8461|convrt)\b', name) or
        re.search(r'\b(marketing|social.selling|lead.generation|cold.prospects)\b', desc)):
        classifications.append({
            'category': 'Marketing & Sales',
            'subcategory': 'Sales Platform',
            'tags': ['marketing', 'sales'],
            'confidence': 'high'
        })

    # 27. Education & Tutorial
    if (re.search(r'\b(learn.*typescript|tutorial|course|education|teach)\b', name) or
        re.search(r'\b(learn|tutorial|educational)\b', desc)):
        classifications.append({
            'category': 'Education & Tutorials',
            'subcategory': 'Learning',
            'tags': ['education', 'tutorial'],
            'confidence': 'medium'
        })

    # 28. LLM APIs & Backends
    if (re.search(r'\b(litellm|open.*webui|openrouter|superclaude|claude.*router|deepclaude)\b', name)) and not classifications:
        classifications.append({
            'category': 'LLM APIs & Backends',
            'subcategory': 'LLM Gateway' if re.search(r'llm|gateway|proxy|router', name) else 'LLM Backend',
            'tags': ['llm', 'api'],
            'confidence': 'high'
        })

    # Fallback for LLM related
    if not classifications:
        if re.search(r'\b(litellm|open.webui|openrouter|superclaude|claude.*router|deepclaude|claude.*conductor)\b', name):
            classifications.append({
                'category': 'LLM APIs & Backends',
                'subcategory': 'LLM Backend',
                'tags': ['llm', 'api'],
                'confidence': 'high'
            })

    # 29. AI Research
    if (re.search(r'\b(research|paper.*analysis|ai.*research)\b', name) or
        re.search(r'\b(research.platform|paper.analysis)\b', desc)) and not classifications:
        classifications.append({
            'category': 'AI Research',
            'subcategory': 'Research Platform',
            'tags': ['research', 'ai'],
            'confidence': 'medium'
        })

    # 30. Image Processing/OCR
    if (re.search(r'\b(image|ocr|diagram.*insight|image.*code.*scholar|image.*analysis)\b', name) or
        re.search(r'\b(image.processing|ocr|diagram.analysis)\b', desc)) and not classifications:
        classifications.append({
            'category': 'Image Processing & OCR',
            'subcategory': 'Image Analysis',
            'tags': ['image-processing', 'ocr'],
            'confidence': 'medium'
        })

    # If still no classification, try catch-all by description
    if not classifications:
        if re.search(r'\b(lovable.dev|bolt.new|lovable)\b', desc) and not re.search(r'\b(ai.app.builder|no.code)\b', name):
            classifications.append({
                'category': 'AI App Builders & No-Code',
                'subcategory': 'Lovable/Bolt Project',
                'tags': ['lovable', 'bolt'],
                'confidence': 'low'
            })
        elif desc.strip() and is_empty:
            classifications.append({
                'category': 'Empty/Low Quality',
                'subcategory': 'Empty Repository',
                'tags': ['empty'],
                'confidence': 'high'
            })
        elif not desc.strip() or score < 10:
            classifications.append({
                'category': 'Empty/Low Quality',
                'subcategory': 'Low Quality',
                'tags': ['low-quality'],
                'confidence': 'high'
            })
        elif re.search(r'\b(ai.*powered|ai.*power|artificial.intelligence)\b', desc):
            classifications.append({
                'category': 'AI Applications',
                'subcategory': 'General AI App',
                'tags': ['ai', 'application'],
                'confidence': 'low'
            })
        elif re.search(r'\b(dashboard|admin|management)\b', desc):
            classifications.append({
                'category': 'Dashboards & Admin Panels',
                'subcategory': 'Dashboard',
                'tags': ['dashboard', 'admin'],
                'confidence': 'low'
            })
        else:
            classifications.append({
                'category': 'Uncategorized',
                'subcategory': 'Other',
                'tags': [],
                'confidence': 'low'
            })

    return classifications[0]  # Return the best match

results = []
category_counts = {}

for repo in repos:
    classification = classify_repo(repo)
    
    cat = classification['category']
    if cat not in category_counts:
        category_counts[cat] = []
    category_counts[cat].append(repo['name'])
    
    results.append({
        'name': repo['name'],
        'category': classification['category'],
        'subcategory': classification['subcategory'],
        'tags': classification['tags'],
        'confidence': classification['confidence'],
        'score': repo.get('score', 0),
        'tier': repo.get('tier', '')
    })

print(f"Total repos tagged: {len(results)}")
print(f"Categories defined: {len(category_counts)}")
print()

# Sort categories by count
sorted_cats = sorted(category_counts.items(), key=lambda x: -len(x[1]))
for cat, repos_list in sorted_cats:
    print(f"  {cat}: {len(repos_list)} repos")

# Write JSON output (without score/tier)
json_output = []
for r in results:
    json_output.append({
        'name': r['name'],
        'category': r['category'],
        'subcategory': r['subcategory'],
        'tags': r['tags'],
        'confidence': r['confidence']
    })

os.makedirs('C:/temp/velvet-sojourner/docs', exist_ok=True)

with open('C:/temp/velvet-sojourner/docs/repo-categories.json', 'w', encoding='utf-8') as f:
    json.dump(json_output, f, indent=2, ensure_ascii=False)

print(f"\nJSON written to: C:/temp/velvet-sojourner/docs/repo-categories.json")

# --- Generate CATEGORY_INDEX.md ---
# Top scoring repos per category
from collections import defaultdict

cat_repos = defaultdict(list)
for r in results:
    cat_repos[r['category']].append(r)

lines = []
lines.append("# AgentForge Repository Category Index\n")
lines.append(f"_Auto-generated taxonomy of {len(results)} repositories across {len(category_counts)} categories._\n")
lines.append("---\n")

# Sort categories by count
for cat, repos_list in sorted_cats:
    # Get top 10 by score for this category
    cat_items = cat_repos[cat]
    cat_items.sort(key=lambda x: -x['score'])
    top10 = cat_items[:10]
    
    lines.append(f"## {cat}\n")
    lines.append(f"- **Total repos**: {len(repos_list)}")
    lines.append(f"- **Description**: ")
    # Generate description based on category and its repos
    desc_map = {
        'MCP Servers': 'Repositories implementing the Model Context Protocol (MCP) for AI tool integration and LLM interactions.',
        'Trading Bots & Crypto': 'Cryptocurrency trading platforms, bots, paper trading simulators, and blockchain-based financial tools.',
        'AI Frameworks & Agents': 'Core AI agent frameworks, multi-agent systems, and autonomous agent platforms.',
        'Chatbots & Conversational AI': 'Chat management tools, conversation organizers, and chatbot applications.',
        'Web Scraping & Crawling': 'Web scraping frameworks, crawlers, and data extraction tools for content acquisition.',
        'Automation & Workflow': 'Workflow automation platforms, CI/CD pipelines, and no-code automation tools.',
        'Developer Tools': 'CLI tools, code analysis platforms, development environments, and developer productivity utilities.',
        'Social Media Tools': 'Social media management, content scheduling, growth platforms, and engagement analytics.',
        'Project Management': 'Task management, project tracking, kanban boards, and team collaboration platforms.',
        'Monetization & Business': 'Revenue generation platforms, business tools, money-making opportunity analysis, and monetization dashboards.',
        'Media & Video Tools': 'Video editing, media processing, meme generation, and content creation tools.',
        'Knowledge Management': 'Documentation platforms, knowledge bases, note-taking apps, and wiki systems.',
        'AI App Builders & No-Code': 'No-code/low-code platforms, AI-powered app builders, and rapid prototyping tools.',
        'Prompt Engineering': 'Prompt libraries, management tools, system prompt collections, and prompt optimization utilities.',
        'Browser Tools & Extensions': 'Browser extensions, bookmark managers, tab management, and browser-based utilities.',
        'Gaming & Trading Cards': 'Game development tools, trading card platforms, and collectible marketplaces.',
        'Security & Privacy': 'Cybersecurity tools, privacy-focused applications, remote access solutions, and security monitoring.',
        'Analytics & Insights': 'Data analytics, browser history analysis, time tracking, and business intelligence dashboards.',
        'AI Tools & Directories': 'Curated directories of AI tools, discovery platforms, and AI resource collections.',
        'Templates & Starter Kits': 'Project templates, boilerplates, starter kits, and scaffolding tools for rapid development.',
        'Local & Self-Hosted AI': 'Self-hosted AI solutions, local LLM deployment tools, Ollama integrations, and Docker-based AI stacks.',
        'Healthcare & Fitness': 'Health tracking, fitness coaching, NDIS assistant tools, and medical diagnostic applications.',
        'Gambling & Betting': 'Keno analysis, betting platforms, and gambling-related analytical tools.',
        'Data Processing & ETL': 'Data pipeline tools, ETL frameworks, content processing systems, and data transformation utilities.',
        'Marketing & Sales': 'Social selling platforms, lead generation tools, marketing automation, and sales enablement systems.',
        'Education & Tutorials': 'Learning resources, educational platforms, coding tutorials, and training materials.',
        'LLM APIs & Backends': 'LLM API gateways, proxy servers, model backends, and inference infrastructure.',
        'AI Research': 'Research platforms, paper analysis tools, and AI research collaboration systems.',
        'Image Processing & OCR': 'Image analysis, OCR tools, diagram processing, and computer vision applications.',
        'AI Applications': 'General-purpose AI-powered applications and intelligent software solutions.',
        'Dashboards & Admin Panels': 'Administrative dashboards, monitoring panels, and management interfaces.',
        'Empty/Low Quality': 'Repositories with minimal content, no descriptions, or very low quality scores.',
        'Uncategorized': 'Repositories that did not match any defined category pattern.'
    }
    lines.append(f'  {desc_map.get(cat, "Miscellaneous repositories.")}')
    lines.append("")
    
    lines.append(f"| # | Repository | Score | Subcategory |")
    lines.append(f"|---|------------|-------|-------------|")
    for i, r in enumerate(top10, 1):
        lines.append(f"| {i} | {r['name']} | {r['score']} | {r['subcategory']} |")
    lines.append("")
    lines.append("---\n")

lines.append("\n_Generated by AgentForge Taxonomy Builder_")

with open('C:/temp/velvet-sojourner/docs/CATEGORY_INDEX.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"Index written to: C:/temp/velvet-sojourner/docs/CATEGORY_INDEX.md")
print(f"\nConfidence breakdown:")
from collections import Counter
conf_counts = Counter(r['confidence'] for r in results)
for k, v in conf_counts.items():
    print(f"  {k}: {v}")
