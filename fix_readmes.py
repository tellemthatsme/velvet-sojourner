"""
Generate README for repos that have actual content but poor/no README
"""
import os

REPOS_DIR = r'repos'

repos_to_fix = [
    ('aud-ai-saver', 'Audio AI Saver', 'Converts audio files to text transcripts using AI speech recognition. Supports multiple audio formats with batch processing.'),
    ('ai-phone-farming-platform', 'AI Phone Farming Platform', 'Automated mobile device management platform for AI-driven phone farming operations.'),
    ('karma-intel-hub', 'Karma Intel Hub', 'Intelligence gathering and analysis hub for tracking AI agent metrics, performance data, and system health.'),
    ('memory-montage-maker', 'Memory Montage Maker', 'Create video montages from photos and memories with AI-powered scene selection and transition effects.'),
    ('v0-ai-news-dashboard', 'AI News Dashboard', 'Real-time AI news aggregator dashboard built with v0.dev. Curates latest developments in artificial intelligence.'),
    ('prompts', 'Agent Prompts Collection', 'Curated collection of AI agent prompts, system prompts, and instruction templates for various use cases.'),
    ('ai-influencer-platform', 'AI Influencer Platform', 'Platform for managing AI-generated influencer content, scheduling posts, and tracking engagement metrics.'),
]

for repo_name, title, desc in repos_to_fix:
    repo_path = os.path.join(REPOS_DIR, repo_name)
    if not os.path.isdir(repo_path):
        print(f'SKIP: {repo_name} - directory not found')
        continue

    readme_path = os.path.join(repo_path, 'README.md')
    existing = ''
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8', errors='replace') as f:
            existing = f.read().strip()

    if existing and len(existing) > 100:
        print(f'SKIP: {repo_name} - already has README ({len(existing)} chars)')
        continue

    # Detect languages/files
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        for fn in filenames:
            files.append(fn)

    js_files = [f for f in files if f.endswith(('.js', '.jsx', '.ts', '.tsx'))]
    py_files = [f for f in files if f.endswith('.py')]
    html_files = [f for f in files if f.endswith(('.html', '.htm'))]
    configs = [f for f in files if f in ('package.json', 'tsconfig.json', 'vite.config.ts', 'requirements.txt', 'Dockerfile')]
    image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]

    langs = []
    if js_files: langs.append('JavaScript/TypeScript')
    if py_files: langs.append('Python')
    if html_files: langs.append('HTML')

    file_count = len(files)
    total_size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(repo_path) for f in fn) / 1024

    readme = f'# {title}\n\n'
    readme += f'{desc}\n\n'
    readme += '## Overview\n\n'
    readme += f'This repository contains **{file_count} files** ({total_size:.0f} KB) primarily in '
    readme += f'{", ".join(langs) if langs else "various formats"}.\n\n'

    if configs:
        readme += '## Tech Stack\n\n'
        for cfg in configs:
            cfg_path = os.path.join(repo_path, cfg)
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()[:500]
                readme += f'**{cfg}:**\n```\n{content}\n```\n\n'

    readme += '## Quick Start\n\n'
    if 'package.json' in configs:
        readme += '```bash\nnpm install\nnpm run dev\n```\n\n'
    elif 'requirements.txt' in configs:
        readme += '```bash\npip install -r requirements.txt\npython main.py\n```\n\n'
    else:
        readme += 'Open the HTML files in your browser or deploy to a static hosting provider.\n\n'

    readme += '## Project Structure\n\n'
    dirs = sorted(set(os.path.relpath(os.path.join(dp, dn), repo_path).split(os.sep)[0]
                  for dp, dn, fn in os.walk(repo_path) for dn in dn if not dn.startswith(('.', '_'))))
    if dirs:
        readme += '```\n'
        for d in dirs[:10]:
            readme += f'{d}/\n'
        readme += '```\n\n'

    readme += '## License\n\nMIT\n'

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)

    print(f'OK: {repo_name} - generated README ({len(readme)} chars)')
