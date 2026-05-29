#!/usr/bin/env python3
import sys
from src.export_sorter import main
sys.argv = [arg for arg in sys.argv if arg != "--cli"]
main()
