import json, sys

with open('C:/temp/velvet-sojourner/repos/_SCAN_ALL_RESULTS.json', 'r') as f:
    data = json.load(f)

repos = data['repos']
# Print out names, descriptions, tiers
for r in repos:
    desc = r.get('description', '') or ''
    name = r['name']
    tier = r.get('tier', '')
    score = r.get('score', 0)
    line = f"{name}|{desc[:150]}|{tier}|{score}"
    sys.stdout.buffer.write((line + '\n').encode('utf-8'))
