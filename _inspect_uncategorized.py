import json

with open('C:/temp/velvet-sojourner/repos/_SCAN_ALL_RESULTS.json') as f:
    data = json.load(f)
repos = data['repos']

# Check repos with no description but non-zero files
count = 0
for r in repos:
    desc = (r.get('description') or '')
    name = r['name']
    if not desc.strip() and r['file_count'] > 0 and r['score'] > 0:
        print(f"{name}|files={r['file_count']}|score={r['score']}|tier={r['tier']}")
        count += 1
    if count >= 30:
        break
print("---")

# Check repos with description that might not match 
count = 0
for r in repos:
    desc = (r.get('description') or '').lower()
    name = r['name']
    if desc and 'lovable' in desc and r['score'] > 50 and 'trading' not in name and 'crypto' not in name:
        print(f"{name}|{desc[:120]}")
        count += 1
        if count >= 30:
            break
