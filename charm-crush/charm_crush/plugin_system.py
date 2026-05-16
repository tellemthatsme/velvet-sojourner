"""
Plugin System for Charm Crush
Allows extending application functionality via Python scripts
"""
import os
import re
import sys
from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class PluginInfo:
    id: str
    name: str
    version: str
    author: str
    description: str
    permissions: List[str]
    enabled: bool = True


class PluginInterface:
    """Base class that all plugins must inherit from"""
    def initialize(self, context: Dict[str, Any]):
        pass
        
    def shutdown(self):
        pass


class PluginManager:
    """Discovers, loads, and manages lifecycle of application plugins"""
    
    def __init__(self, plugin_dir: str = None):
        if plugin_dir:
            self.plugin_dir = plugin_dir
        else:
            app_data = os.environ.get('APPDATA', os.environ.get('HOME', os.path.expanduser('~')))
            self.plugin_dir = os.path.join(app_data, 'CharmCrush', 'plugins')
            
        os.makedirs(self.plugin_dir, exist_ok=True)
        self._plugins = {} # id -> (PluginInfo, instance)
        self._plugin_settings = {}
        
    def discover_plugins(self) -> List[PluginInfo]:
        """Scans the plugin directory for available plugins"""
        discovered = []
        if not os.path.exists(self.plugin_dir):
            return []
            
        for item in os.listdir(self.plugin_dir):
            if item.endswith('.py') and item != '__init__.py':
                path = os.path.join(self.plugin_dir, item)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    info = self._parse_plugin_metadata(content)
                    if info:
                        discovered.append(info)
        return discovered
        
    def _parse_plugin_metadata(self, content: str) -> Optional[PluginInfo]:
        """Extracts metadata from plugin file header comments"""
        try:
            p_id = re.search(r'# Plugin: (.+)', content).group(1).strip()
            version = re.search(r'# Version: (.+)', content).group(1).strip()
            author = re.search(r'# Author: (.+)', content).group(1).strip()
            desc = re.search(r'# Description: (.+)', content).group(1).strip()
            perms_match = re.search(r'# Permissions: (.+)', content)
            perms = [p.strip() for p in perms_match.group(1).split(',')] if perms_match and perms_match.group(1).strip() else []
            
            return PluginInfo(
                id=p_id,
                name=p_id.replace('_', ' ').title(),
                version=version,
                author=author,
                description=desc,
                permissions=perms
            )
        except Exception:
            return None
            
    def load_plugin(self, plugin_id: str) -> bool:
        """Dynamically loads and initializes a plugin"""
        # In a real implementation, this would use importlib
        return False
        
    def get_plugin_settings(self, plugin_id: str) -> Dict:
        return self._plugin_settings.get(plugin_id, {})
        
    def get_statistics(self) -> Dict:
        return {
            'total_plugins': len(self.discover_plugins()),
            'loaded_plugins': len(self._plugins)
        }
        
    def create_plugin_template(self, plugin_id: str, output_dir: str) -> str:
        """Generates a boilerplate plugin file"""
        plugin_name = plugin_id.replace('_', ' ').title().replace(' ', '')
        content = f'''# Plugin: {plugin_id}
# Version: 1.0.0
# Author: Your Name
# Description: Description for {plugin_id}
# Permissions: 

from .plugin_system import PluginInterface

class {plugin_name}(PluginInterface):
    def initialize(self, context):
        print("{plugin_id} initialized")
        
    def shutdown(self):
        print("{plugin_id} shutdown")
'''
        file_path = os.path.join(output_dir, f"{plugin_id}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
