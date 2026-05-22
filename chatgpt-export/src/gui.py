#!/usr/bin/env python3
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                 QHBoxLayout, QPushButton, QLabel, QFileDialog,
                                 QTextEdit, QProgressBar, QTabWidget,
                                 QTableWidget, QTableWidgetItem, QHeaderView,
                                 QMessageBox, QComboBox, QGroupBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from src.export_sorter import ExportSorter, ChatExport
from src.knowledge_base import KnowledgeBase
from src.obsidian_sync import ObsidianSync


class ExportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_dir, output_dir, out_format="md"):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.out_format = out_format

    def run(self):
        try:
            sorter = ExportSorter(Path(self.input_dir), Path(self.output_dir))
            stats = sorter.run(self.out_format)
            msg = f"Export complete! {stats.processed} files processed, {stats.duplicates} duplicates, {len(stats.errors)} errors"
            self.finished.emit(msg)
        except Exception as e:
            self.error.emit(str(e))


class ExportGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Export System")
        self.resize(1000, 750)
        self.input_dir = ""
        self.output_dir = ""
        self.kb = KnowledgeBase("knowledge.db")
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        io_group = QGroupBox("Export Settings")
        io_layout = QVBoxLayout(io_group)

        input_row = QHBoxLayout()
        self.input_label = QLabel("Input: Not selected")
        input_btn = QPushButton("📁 Select Input Folder")
        input_btn.clicked.connect(self.select_input)
        input_row.addWidget(self.input_label, 1)
        input_row.addWidget(input_btn)
        io_layout.addLayout(input_row)

        output_row = QHBoxLayout()
        self.output_label = QLabel("Output: Not selected")
        output_btn = QPushButton("📂 Select Output Folder")
        output_btn.clicked.connect(self.select_output)
        output_row.addWidget(self.output_label, 1)
        output_row.addWidget(output_btn)
        io_layout.addLayout(output_row)

        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Markdown (.md)", "HTML (.html)", "PDF (.pdf)"])
        format_row.addWidget(self.format_combo)
        format_row.addStretch()
        io_layout.addLayout(format_row)

        layout.addWidget(io_group)

        tabs = QTabWidget()
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_text)
        tabs.addTab(stats_tab, "📊 Statistics")

        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        tabs.addTab(preview_tab, "📋 Preview")

        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        search_row = QHBoxLayout()
        self.search_input = QTextEdit()
        self.search_input.setMaximumHeight(40)
        self.search_input.setPlaceholderText("Search conversations...")
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self.do_search)
        search_row.addWidget(self.search_input)
        search_row.addWidget(search_btn)
        search_layout.addLayout(search_row)
        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        search_layout.addWidget(self.search_results)
        tabs.addTab(search_tab, "🔍 Search")

        layout.addWidget(tabs)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        btn_row = QHBoxLayout()
        export_btn = QPushButton("▶️ Export")
        export_btn.setMinimumHeight(40)
        export_btn.clicked.connect(self.start_export)
        obsidian_btn = QPushButton("📓 Sync to Obsidian")
        obsidian_btn.clicked.connect(self.sync_obsidian)
        self.status_btn = QPushButton("📊 Show Stats")
        self.status_btn.clicked.connect(self.show_stats)
        btn_row.addWidget(export_btn)
        btn_row.addWidget(obsidian_btn)
        btn_row.addWidget(self.status_btn)
        layout.addLayout(btn_row)

        self.statusBar().showMessage("Ready")

    def select_input(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_dir = folder
            self.input_label.setText(f"Input: {folder}")

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = folder
            self.output_label.setText(f"Output: {folder}")

    def start_export(self):
        if not self.input_dir or not self.output_dir:
            QMessageBox.warning(self, "Missing Paths", "Please select both input and output folders")
            return

        fmt_map = {"Markdown (.md)": "md", "HTML (.html)": "html", "PDF (.pdf)": "pdf"}
        out_format = fmt_map[self.format_combo.currentText()]

        self.progress.setVisible(True)
        self.statusBar().showMessage("Exporting...")

        self.worker = ExportWorker(self.input_dir, self.output_dir, out_format)
        self.worker.finished.connect(self.export_finished)
        self.worker.error.connect(self.export_error)
        self.worker.start()

    def export_finished(self, message):
        self.progress.setVisible(False)
        self.statusBar().showMessage("Export complete")
        self.preview_text.append(f"\n✅ {message}")
        self.show_stats()

    def export_error(self, error):
        self.progress.setVisible(False)
        self.statusBar().showMessage("Export failed")
        self.preview_text.append(f"\n❌ ERROR: {error}")

    def sync_obsidian(self):
        vault = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault Folder")
        if vault and self.output_dir:
            sync = ObsidianSync(vault)
            try:
                count = sync.sync(self.output_dir)
                QMessageBox.information(self, "Sync Complete", f"Copied {count} files to Obsidian vault")
            except Exception as e:
                QMessageBox.warning(self, "Sync Failed", str(e))

    def show_stats(self):
        try:
            stats = self.kb.stats()
            self.stats_text.setText(
                f"Total conversations: {stats['total']}\n\n"
                f"By Topic:\n" + "\n".join(f"  {k}: {v}" for k, v in stats.get('by_topic', {}).items()) + "\n\n"
                f"By Source:\n" + "\n".join(f"  {k}: {v}" for k, v in stats.get('by_source', {}).items())
            )
        except Exception:
            self.stats_text.setText("No data yet. Run an export first.")

    def do_search(self):
        query = self.search_input.toPlainText().strip()
        if not query:
            return
        results = self.kb.search(query)
        if not results:
            self.search_results.setText("No results found.")
            return
        text = f"Found {len(results)} results for '{query}':\n\n"
        for r in results:
            text += f"📄 {r['title']} ({r['topic']}, {r['source']})\n{r['content']}\n---\n"
        self.search_results.setText(text)


def main():
    if not HAS_GUI:
        print("PyQt6 not installed. Use CLI mode:")
        print("  python src/export_sorter.py --help")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ExportGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
