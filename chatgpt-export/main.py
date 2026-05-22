#!/usr/bin/env python3
import sys
import os

# Try GUI mode first, fallback to CLI
try:
    from PyQt6.QtWidgets import QApplication
    from src.gui import ExportGUI
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

if __name__ == "__main__":
    if "--cli" in sys.argv or not HAS_GUI:
        from src.export_sorter import main as cli_main
        sys.argv = [arg for arg in sys.argv if arg != "--cli"]
        cli_main()
    else:
        from PyQt6.QtWidgets import QApplication
        from src.gui import ExportGUI
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = ExportGUI()
        window.show()
        sys.exit(app.exec())
