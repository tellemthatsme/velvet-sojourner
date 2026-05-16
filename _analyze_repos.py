import json

with open('C:/temp/velvet-sojourner/repos/_SCAN_ALL_RESULTS.json', 'r') as f:
    data = json.load(f)

repos = data['repos']
print(f"Total repos: {len(repos)}")

# Print name, description (first 100 chars), tier, score for all repos
for r in repos:
    desc = r.get('description', '') or ''
    print(f"{r['name']}|{desc[:150]}|{r.get('tier','')}|{r.get('score',0)}")
