import os
import json
from collections import defaultdict

def get_dir_stats(path):
    stats = {
        'total_size': 0,
        'file_count': 0,
        'types': defaultdict(int),
        'large_files': [],
        'folders': []
    }
    
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                size = entry.stat().st_size
                stats['total_size'] += size
                stats['file_count'] += 1
                ext = os.path.splitext(entry.name)[1].lower() or 'no_ext'
                stats['types'][ext] += 1
                
                if size > 100 * 1024 * 1024:  # > 100MB
                    stats['large_files'].append({
                        'name': entry.name,
                        'path': entry.path,
                        'size': size
                    })
            elif entry.is_dir():
                stats['folders'].append(entry.name)
    except PermissionError:
        pass
    return stats

def audit_drive(drive_path):
    report = {
        'root_folders': {},
        'overall': {
            'total_size': 0,
            'file_count': 0,
            'categories': defaultdict(lambda: {'size': 0, 'count': 0})
        }
    }
    
    # Categories mapping
    cat_map = {
        '.mp4': 'Videos', '.mov': 'Videos', '.avi': 'Videos', '.mkv': 'Videos',
        '.jpg': 'Photos', '.png': 'Photos', '.jpeg': 'Photos', '.gif': 'Photos',
        '.zip': 'Backups/Archives', '.rar': 'Backups/Archives', '.7z': 'Backups/Archives', '.tar': 'Backups/Archives', '.gz': 'Backups/Archives',
        '.txt': 'Text/Docs', '.md': 'Text/Docs', '.pdf': 'Text/Docs', '.doc': 'Text/Docs', '.docx': 'Text/Docs',
        '.py': 'Code', '.js': 'Code', '.html': 'Code', '.css': 'Code', '.json': 'Code'
    }

    print(f"Auditing {drive_path}...")
    
    try:
        for root, dirs, files in os.walk(drive_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    report['overall']['total_size'] += size
                    report['overall']['file_count'] += 1
                    
                    ext = os.path.splitext(file)[1].lower()
                    category = cat_map.get(ext, 'Other')
                    report['overall']['categories'][category]['size'] += size
                    report['overall']['categories'][category]['count'] += 1
                except (PermissionError, FileNotFoundError):
                    continue
            
            # Only do shallow scan logic for root folders to keep report clean
            if root == drive_path:
                for d in dirs:
                    report['root_folders'][d] = "Scanning..." # Placeholder
                    
    except Exception as e:
        print(f"Error: {e}")

    # Convert defaultdicts to regular dicts for JSON
    report['overall']['categories'] = dict(report['overall']['categories'])
    return report

if __name__ == "__main__":
    # For speed, we'll first just do a top-level folder scan and size calculation
    # Walking the entire drive might take too long if it's huge, 
    # but let's try a faster recursive size check first.
    
    drive = "E:\\"
    results = audit_drive(drive)
    
    with open("E_DRIVE_AUDIT_DATA.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print("Audit Data Generated.")
