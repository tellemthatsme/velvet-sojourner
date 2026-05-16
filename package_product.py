import zipfile
from pathlib import Path

src = Path('deployment-platform')
dst = Path('dist/agentforge-v1.0.zip')

with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in src.rglob('*'):
        if f.is_file():
            arcname = f.relative_to(src)
            zf.write(f, arcname)
            print(f'Added: {arcname}')
    # Also include key docs
    for doc in ['AGENTFORGE.md', 'APP_UPDATE_LOG.md']:
        p = Path(doc)
        if p.exists():
            zf.write(p, p.name)
            print(f'Added: {p.name}')

print(f'\nCreated: {dst}')
print(f'Size: {dst.stat().st_size / 1024:.1f} KB')
