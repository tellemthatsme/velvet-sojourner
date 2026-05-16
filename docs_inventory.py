"""
Step 1: Inventory all docs across all repos
Checks for docs/, README quality, documentation files
"""
import os
import json
from datetime import datetime

REPOS_DIR = r'C:\temp\velvet-sojourner\repos'
OUTPUT_FILE = r'C:\temp\velvet-sojourner\repos\_DOCS_INVENTORY.json'
SUMMARY_FILE = r'C:\temp\velvet-sojourner\DOCS_INVENTORY.md'

DOC_KEYWORDS = [
    'docs/', 'documentation/', 'wiki/', 'guide/', 'manual/',
    'help/', 'tutorial/', 'examples/', 'getting-started/',
]


def scan_docs(repo_name, repo_path):
    info = {
        'name': repo_name,
        'has_docs_dir': False,
        'docs_files': [],
        'readme_path': '',
        'readme_size': 0,
        'readme_quality': 'none',
        'has_contributing': False,
        'has_changelog': False,
        'has_examples_dir': False,
        'has_tests_dir': False,
        'has_api_docs': False,
        'total_doc_files': 0,
        'doc_file_types': {},
    }

    try:
        top = set(os.listdir(repo_path))

        for f in top:
            if f.lower().startswith('readme'):
                rp = os.path.join(repo_path, f)
                info['readme_path'] = f
                try:
                    info['readme_size'] = os.path.getsize(rp)
                    with open(rp, 'r', encoding='utf-8', errors='ignore') as rf:
                        content = rf.read()
                    if len(content) > 5000:
                        info['readme_quality'] = 'excellent'
                    elif len(content) > 1000:
                        info['readme_quality'] = 'good'
                    elif len(content) > 100:
                        info['readme_quality'] = 'minimal'
                    else:
                        info['readme_quality'] = 'poor'
                except:
                    info['readme_quality'] = 'error'

        info['has_contributing'] = any(
            f.lower().startswith('contributing') or f.lower().startswith('contributor') for f in top)
        info['has_changelog'] = any(
            f.lower().startswith('changelog') or f.lower() == 'history.md' for f in top)
        info['has_examples_dir'] = os.path.isdir(os.path.join(repo_path, 'examples'))
        info['has_tests_dir'] = os.path.isdir(os.path.join(repo_path, 'tests'))

        docs_dirs = ['docs', 'documentation', 'wiki', 'guide']
        for dd in docs_dirs:
            ddp = os.path.join(repo_path, dd)
            if os.path.isdir(ddp):
                info['has_docs_dir'] = True
                doc_files = []
                doc_types = {}
                for dp, dn, fn in os.walk(ddp):
                    for f in fn:
                        ext = os.path.splitext(f)[1].lower()
                        doc_types[ext] = doc_types.get(ext, 0) + 1
                        doc_files.append(os.path.join(dp, f))
                info['docs_files'] = doc_files
                info['doc_file_types'] = doc_types
                info['total_doc_files'] = len(doc_files)
                break

        if not info['has_docs_dir']:
            for dp, dn, fn in os.walk(repo_path):
                if '.git' in dp.split(os.sep):
                    continue
                rel = os.path.relpath(dp, repo_path)
                if rel.startswith('docs') or rel.startswith('documentation'):
                    info['has_docs_dir'] = True
                    break

        if info['has_docs_dir'] and info['total_doc_files'] == 0:
            ddp = os.path.join(repo_path, 'docs')
            if os.path.isdir(ddp):
                for dp, dn, fn in os.walk(ddp):
                    for f in fn:
                        ext = os.path.splitext(f)[1].lower()
                        info['doc_file_types'][ext] = info['doc_file_types'].get(ext, 0) + 1
                        info['total_doc_files'] += 1

        if any(f.endswith(('.md', '.rst', '.txt')) and f not in ('README.md', 'readme.md')
               and f.lower() not in ('license', 'license.txt', 'license.md')
               for f in top):
            for f in top:
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.md', '.rst') and f.lower() not in ('readme.md', 'license.md', 'license.txt'):
                    info['has_api_docs'] = True
                    break

    except Exception as e:
        info['error'] = str(e)

    return info


def main():
    print("=" * 60)
    print("DOCS INVENTORY SCANNER")
    print("=" * 60)
    print(f"Scanning: {REPOS_DIR}")
    print()

    all_repos = sorted(os.listdir(REPOS_DIR))
    results = []
    doc_stats = {
        'with_docs_dir': 0,
        'with_good_readme': 0,
        'with_excellent_readme': 0,
        'with_minimal_readme': 0,
        'with_poor_readme': 0,
        'with_contributing': 0,
        'with_changelog': 0,
        'with_examples': 0,
        'with_tests_dir': 0,
        'with_api_docs': 0,
        'total_doc_files': 0,
    }

    count = 0
    for repo_name in all_repos:
        repo_path = os.path.join(REPOS_DIR, repo_name)
        if not os.path.isdir(repo_path) or repo_name.startswith('_'):
            continue

        count += 1
        if count % 100 == 0:
            print(f"  Progress: {count}")

        info = scan_docs(repo_name, repo_path)
        results.append(info)

        q = info['readme_quality']
        if q in ('excellent', 'good', 'minimal', 'poor', 'none'):
            doc_stats[f'with_{q}_readme'] = doc_stats.get(f'with_{q}_readme', 0) + 1
        if info['has_docs_dir']:
            doc_stats['with_docs_dir'] += 1
        if info['has_contributing']:
            doc_stats['with_contributing'] += 1
        if info['has_changelog']:
            doc_stats['with_changelog'] += 1
        if info['has_examples_dir']:
            doc_stats['with_examples'] += 1
        if info['has_tests_dir']:
            doc_stats['with_tests_dir'] += 1
        if info['has_api_docs']:
            doc_stats['with_api_docs'] += 1
        doc_stats['total_doc_files'] += info['total_doc_files']

    good_readme = doc_stats.get('with_excellent_readme', 0) + doc_stats.get('with_good_readme', 0)

    output = {
        'scan_date': datetime.now().isoformat(),
        'total_repos': len(results),
        'stats': doc_stats,
        'repos_with_docs': [r for r in results if r['has_docs_dir']],
        'repos_with_good_docs': [r for r in results
                                 if r['readme_quality'] in ('excellent', 'good')
                                 or r['has_docs_dir']],
        'all_repos': results,
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)

    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write("# Docs Inventory Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total repos:** {len(results)}\n\n")
        f.write("## Summary\n\n")
        f.write(f"| Metric | Count | % |\n")
        f.write(f"|--------|-------|---|\n")
        f.write(f"| Has docs/ directory | {doc_stats['with_docs_dir']} | {doc_stats['with_docs_dir']*100//len(results)}% |\n")
        f.write(f"| Excellent README | {doc_stats.get('with_excellent_readme', 0)} | {doc_stats.get('with_excellent_readme', 0)*100//len(results)}% |\n")
        f.write(f"| Good README | {doc_stats.get('with_good_readme', 0)} | {doc_stats.get('with_good_readme', 0)*100//len(results)}% |\n")
        f.write(f"| Minimal README | {doc_stats.get('with_minimal_readme', 0)} | {doc_stats.get('with_minimal_readme', 0)*100//len(results)}% |\n")
        f.write(f"| Poor README | {doc_stats.get('with_poor_readme', 0)} | {doc_stats.get('with_poor_readme', 0)*100//len(results)}% |\n")
        f.write(f"| Has CONTRIBUTING.md | {doc_stats['with_contributing']} | {doc_stats['with_contributing']*100//len(results)}% |\n")
        f.write(f"| Has CHANGELOG.md | {doc_stats['with_changelog']} | {doc_stats['with_changelog']*100//len(results)}% |\n")
        f.write(f"| Has examples/ | {doc_stats['with_examples']} | {doc_stats['with_examples']*100//len(results)}% |\n")
        f.write(f"| Has tests/ | {doc_stats['with_tests_dir']} | {doc_stats['with_tests_dir']*100//len(results)}% |\n")
        f.write(f"| Has API docs | {doc_stats['with_api_docs']} | {doc_stats['with_api_docs']*100//len(results)}% |\n\n")
        f.write(f"**Total doc files across all repos:** {doc_stats['total_doc_files']}\n\n")

        f.write("## Repos with docs/ directories\n\n")
        f.write(f"| # | Repo | Doc Files | README Quality | Also Has |\n")
        f.write(f"|---|------|-----------|----------------|----------|\n")
        for i, r in enumerate(sorted(output['repos_with_docs'], key=lambda x: -x['total_doc_files']), 1):
            extras = []
            if r['has_examples_dir']:
                extras.append('examples')
            if r['has_tests_dir']:
                extras.append('tests')
            if r['has_contributing']:
                extras.append('contributing')
            if r['has_changelog']:
                extras.append('changelog')
            f.write(f"| {i} | {r['name']} | {r['total_doc_files']} | {r['readme_quality']} | {', '.join(extras)} |\n")

        f.write("\n## Repos WITHOUT any docs (no README or docs/)\n\n")
        no_docs = [r for r in results if r['readme_quality'] == 'none' and not r['has_docs_dir']]
        if no_docs:
            for i, r in enumerate(sorted(no_docs, key=lambda x: x['name']), 1):
                f.write(f"{i}. {r['name']}\n")
        else:
            f.write("All repos have at least a README or docs/ directory.\n")

    print(f"\n{'='*60}")
    print(f"INVENTORY COMPLETE")
    print(f"{'='*60}")
    print(f"Total repos: {len(results)}")
    print(f"With docs/ directory: {doc_stats['with_docs_dir']}")
    print(f"Good+Excellent README: {good_readme}")
    print(f"Has CONTRIBUTING.md: {doc_stats['with_contributing']}")
    print(f"Has CHANGELOG.md: {doc_stats['with_changelog']}")
    print(f"Has examples/: {doc_stats['with_examples']}")
    print(f"Has tests/: {doc_stats['with_tests_dir']}")
    print(f"Total doc files: {doc_stats['total_doc_files']}")
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"Summary: {SUMMARY_FILE}")


if __name__ == '__main__':
    main()
