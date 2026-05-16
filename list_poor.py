import json
with open('repos/_SCAN_ALL_RESULTS.json') as f:
    repos = json.load(f)['repos']

poor = [r for r in repos if not r.get('has_readme') or r.get('has_readme') == 'poor']
print(f'Repos needing README: {len(poor)}')
total_sz = sum(r.get('size_mb', 0) for r in poor)
total_fl = sum(r.get('file_count', 0) for r in poor)
print(f'Total size: {total_sz:.0f} MB, Total files: {total_fl:,}')
print()

for r in sorted(poor, key=lambda x: -x.get('score', 0)):
    langs = ','.join(r.get('languages', ['?']))
    print(f'{r["name"]:45s} {r.get("size_mb",0):5}MB {r.get("file_count",0):5}f  score={r.get("score",0):3d}  [{langs}]')
