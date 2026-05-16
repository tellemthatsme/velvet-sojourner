#!/usr/bin/env python3
"""
Charm Crush Session Manager
A Windows desktop application for managing configuration files and sessions.

Entry point for the application.
"""

import sys
import os

# Add the current directory to path for imports
if getattr(sys, 'frozen', False):
    # Running as frozen executable
    os.chdir(os.path.dirname(sys.executable))

def main():
    """Main entry point"""
    from charm_crush.gui import main as gui_main
    gui_main()

if __name__ == '__main__':
    main()
