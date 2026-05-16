import json
from collections import Counter

with open('qa/QA_REPORT.json', 'r') as f:
    data = json.load(f)

repos = data['repos']

print('=== TOP 20 BY QUALITY ===')
for r in sorted(repos, key=lambda x: x['quality_score'], reverse=True)[:20]:
    print(f"{r['name']:40} Q:{r['quality_score']:3} Docker:{str(r['has_dockerfile']):5} Tests:{str(r['has_tests']):5} Size:{r['size_mb']:.1f}MB")

print('\n=== LANGUAGE BREAKDOWN ===')
langs = Counter()
for r in repos:
    for lang in r.get('languages', ['unknown']):
        langs[lang] += 1
for lang, count in langs.most_common(10):
    print(f'{lang:15} {count}')

print('\n=== TOP DEPLOYABLE REPOS ===')
for r in sorted([x for x in repos if x['deployable']], key=lambda x: x['quality_score'], reverse=True)[:15]:
    print(f"{r['name']:40} Q:{r['quality_score']}")

print('\n=== STATS ===')
print(f"Total: {len(repos)}")
print(f"Deployable: {sum(1 for r in repos if r['deployable'])}")
print(f"With Tests: {sum(1 for r in repos if r['has_tests'])}")
print(f"Avg Quality: {sum(r['quality_score'] for r in repos)/len(repos):.1f}")
