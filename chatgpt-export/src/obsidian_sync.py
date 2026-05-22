import os
import shutil
from pathlib import Path


class ObsidianSync:
    def __init__(self, vault_path=None):
        self.vault_path = Path(vault_path) if vault_path else None

    def sync(self, export_dir):
        if not self.vault_path:
            raise ValueError("Obsidian vault path not configured")
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Obsidian vault not found: {self.vault_path}")

        export_path = Path(export_dir)
        if not export_path.exists():
            raise FileNotFoundError(f"Export directory not found: {export_dir}")

        copied = 0
        for root, dirs, files in os.walk(export_path):
            for file in files:
                if file.endswith('.md'):
                    src = os.path.join(root, file)
                    rel_path = os.path.relpath(src, export_path)
                    dst = os.path.join(self.vault_path, rel_path)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    copied += 1
        
        return copied

    def list_files(self):
        if not self.vault_path:
            return []
        return [str(f.relative_to(self.vault_path)) for f in self.vault_path.rglob("*.md")]
